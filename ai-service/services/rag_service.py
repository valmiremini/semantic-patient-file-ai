import logging
from typing import List, Dict, Any
import os
from openai import OpenAI
import requests

from services.embedding_service import EmbeddingService
from services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for Retrieval-Augmented Generation"""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.qdrant_service = QdrantService(
            embedding_dimension=embedding_service.get_embedding_dimension()
        )

        # Initialize LLM
        self.model_type = os.getenv("MODEL_TYPE", "local")

        if self.model_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
                self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
                logger.info(f"Initialized OpenAI LLM: {self.llm_model}")
            else:
                logger.warning("No OPENAI_API_KEY set, using local template-based responses")
                self.llm_client = None
                self.model_type = "local"
        elif self.model_type == "ollama":
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:3b")
            self.llm_client = "ollama"
            logger.info(f"Initialized Ollama LLM: {self.llm_model} at {self.ollama_base_url}")
        elif self.model_type == "local":
            self.llm_client = None
            logger.info("Using local template-based LLM responses (no external API)")
        else:
            self.llm_client = None
            logger.warning(f"Unsupported model type: {self.model_type}, using local responses")

    def store_documents(self, patient_id: str, chunks: List[Dict[str, Any]]):
        """Store document chunks in vector database"""
        try:
            # Extract texts
            texts = [chunk['text'] for chunk in chunks]

            # Create embeddings
            embeddings = self.embedding_service.create_embeddings(texts)

            # Prepare payloads
            payloads = []
            for chunk, embedding in zip(chunks, embeddings):
                payload = {
                    'patient_id': patient_id,
                    'text': chunk['text'],
                    'source': chunk.get('source', 'unknown'),
                    'section': chunk.get('section', 'unknown')
                }
                payloads.append(payload)

            # Store in Qdrant
            self.qdrant_service.store_vectors(embeddings, payloads)

            logger.info(f"Stored {len(chunks)} chunks for patient {patient_id}")

        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise

    def query(
        self,
        patient_id: str,
        question: str,
        conversation_history: List[Dict[str, str]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Query patient documents using RAG"""
        try:
            # Create embedding for question
            question_embedding = self.embedding_service.create_embedding(question)

            # Search for relevant context
            search_results = self.qdrant_service.search(
                query_vector=question_embedding,
                patient_id=patient_id,
                limit=top_k + 5,  # Get more results for better coverage
                score_threshold=0.1  # Lower threshold to include more relevant docs
            )

            if not search_results:
                return {
                    'answer': "Ich konnte keine relevanten Informationen zu Ihrer Frage in den Patientenakten finden.",
                    'sources': []
                }

            # Build context from search results
            context_parts = []
            sources = []

            for i, result in enumerate(search_results):
                payload = result['payload']
                context_parts.append(
                    f"[Quelle {i+1} - {payload['source']} / {payload['section']}]:\n{payload['text']}"
                )

                sources.append({
                    'source': payload['source'],
                    'section': payload['section'],
                    'score': result['score'],
                    'text': payload['text'][:200] + "..." if len(payload['text']) > 200 else payload['text']
                })

            context = "\n\n".join(context_parts)

            # Generate answer using LLM or template
            if self.llm_client:
                answer = self._generate_answer(question, context, conversation_history)
            else:
                # Template-based answer (local mode)
                answer = self._generate_template_answer(question, search_results)

            return {
                'answer': answer,
                'sources': sources
            }

        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            raise

    def _generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate answer using LLM"""
        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": """Du bist ein medizinischer AI-Assistent, der Fragen zu Patientendossiers beantwortet.

Deine Aufgabe:
- Beantworte Fragen präzise und direkt basierend auf den bereitgestellten Informationen
- Bei einfachen Fragen (z.B. Name, Alter, Diagnose): Gib eine kurze, klare Antwort
- Bei komplexen Fragen: Strukturiere deine Antworten übersichtlich mit Absätzen und Aufzählungen
- Verwende medizinische Fachterminologie korrekt
- Wenn Informationen KLAR in den Quellen stehen, antworte selbstbewusst und direkt
- NUR wenn Informationen wirklich fehlen oder unklar sind, erwähne dies
- Gib KEINE medizinischen Ratschläge oder Diagnosen
- Verweise auf die Quellen nur, wenn es für die Antwort relevant ist

Formatierung:
- Kurze Antworten für einfache Fragen (z.B. "Der Patient heißt Max Mustermann.")
- Bei längeren Antworten: Nutze Markdown, Überschriften (##), Aufzählungen (-) und Fettdruck (**Text**)
- Sei prägnant und vermeide unnötige Absicherungen oder Zweifel bei klaren Fakten
"""
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 3 exchanges
                    messages.append(msg)

            # Add current question with context
            messages.append({
                "role": "user",
                "content": f"""Kontext aus den Patientenakten:

{context}

---

Frage: {question}

Bitte beantworte die Frage basierend auf dem oben stehenden Kontext."""
            })

            # Call LLM
            if self.llm_client == "ollama":
                # Ollama API call
                response = requests.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.llm_model,
                        "messages": messages,
                        "stream": False
                    },
                    timeout=60
                )
                response.raise_for_status()
                answer = response.json()["message"]["content"]
            else:
                # OpenAI API call
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                answer = response.choices[0].message.content

            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Fehler bei der Antwortgenerierung: {str(e)}"

    def _generate_template_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate template-based answer without LLM (local mode)"""
        try:
            if not search_results:
                return "Leider konnte ich keine relevanten Informationen zu Ihrer Frage finden."

            # Build structured answer from search results
            answer = f"## Antwort basierend auf gefundenen Informationen\n\n"

            # Group by source
            by_source = {}
            for result in search_results:
                source = result['payload']['source']
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(result['payload'])

            # Format answer
            for source, items in by_source.items():
                answer += f"**Aus {source}:**\n\n"
                for item in items:
                    # Clean and format text
                    text = item['text'].strip()
                    # Limit length
                    if len(text) > 500:
                        text = text[:500] + "..."
                    answer += f"{text}\n\n"

            answer += "\n---\n\n"
            answer += "💡 **Hinweis:** Dies ist eine Basis-Antwort basierend auf gefundenen Dokumenten. "
            answer += "Für intelligentere Antworten konfigurieren Sie einen LLM-Provider (OpenAI oder Ollama)."

            return answer

        except Exception as e:
            logger.error(f"Error generating template answer: {str(e)}")
            return "Fehler beim Erstellen der Antwort."
