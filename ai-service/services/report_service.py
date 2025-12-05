import logging
from typing import Dict, Any, Optional
import os
from openai import OpenAI
import requests
import json
from pathlib import Path

from services.embedding_service import EmbeddingService
from services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating medical reports"""

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
                logger.info(f"Initialized OpenAI LLM for reports: {self.llm_model}")
            else:
                logger.warning("No OPENAI_API_KEY set, using local template-based reports")
                self.llm_client = None
                self.model_type = "local"
        elif self.model_type == "ollama":
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:3b")
            self.llm_client = "ollama"
            logger.info(f"Initialized Ollama LLM for reports: {self.llm_model} at {self.ollama_base_url}")
        elif self.model_type == "local":
            self.llm_client = None
            logger.info("Using local template-based report generation (no external API)")
        else:
            self.llm_client = None
            logger.warning(f"Unsupported model type: {self.model_type}, using local reports")

    def generate_report(self, patient_id: str) -> Dict[str, Any]:
        """Generate discharge report for patient"""
        try:
            # Load structured patient data from JSON
            structured_data = self._load_patient_json(patient_id)

            # Retrieve all relevant patient data from RAG
            patient_data = self._retrieve_patient_data(patient_id)

            if not patient_data:
                return {
                    'error': 'Keine Patientendaten gefunden',
                    'patient_id': patient_id
                }

            # Generate structured report using LLM
            if self.llm_client:
                report = self._generate_structured_report(patient_id, patient_data)
            else:
                # Fallback report without LLM
                report = self._generate_basic_report(patient_id, patient_data)

            # Override critical fields with accurate structured data
            if structured_data:
                report = self._merge_structured_data(report, structured_data)

            return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _retrieve_patient_data(self, patient_id: str) -> str:
        """Retrieve all relevant patient data"""
        try:
            # Create embeddings for different aspects
            queries = [
                "Patientendaten Demographie Aufnahme",
                "Diagnosen",
                "Medikation Therapie",
                "Laborwerte",
                "Klinischer Verlauf",
                "Prozeduren Operationen"
            ]

            all_results = []

            for query in queries:
                query_embedding = self.embedding_service.create_embedding(query)

                results = self.qdrant_service.search(
                    query_vector=query_embedding,
                    patient_id=patient_id,
                    limit=10,
                    score_threshold=0.2
                )

                all_results.extend(results)

            # Remove duplicates based on text
            seen_texts = set()
            unique_results = []

            for result in all_results:
                text = result['payload']['text']
                if text not in seen_texts:
                    seen_texts.add(text)
                    unique_results.append(result)

            # Combine all texts
            patient_data = "\n\n".join([
                f"[{r['payload']['source']} - {r['payload']['section']}]:\n{r['payload']['text']}"
                for r in unique_results
            ])

            return patient_data

        except Exception as e:
            logger.error(f"Error retrieving patient data: {str(e)}")
            return ""

    def _generate_structured_report(self, patient_id: str, patient_data: str) -> Dict[str, Any]:
        """Generate structured report using LLM"""
        try:
            prompt = f"""Erstelle einen strukturierten Entlassungsbericht basierend auf den folgenden Patientendaten.

Der Bericht soll folgende Abschnitte enthalten:

1. PATIENTENINFORMATIONEN
   - Name, Alter, Geschlecht
   - Aufnahmedatum, Entlassungsdatum, Aufenthaltsdauer
   - Abteilung/Station

2. GRUND DER HOSPITALISATION
   - Aufnahmegrund
   - Leitsymptome

3. DIAGNOSEN
   - Hauptdiagnose
   - Nebendiagnosen

4. KLINISCHER VERLAUF
   - Zusammenfassung des Verlaufs während des Aufenthalts
   - Wichtige Befunde
   - Durchgeführte Untersuchungen/Prozeduren

5. THERAPIE
   - Durchgeführte Behandlungen
   - Operative Eingriffe (falls zutreffend)

6. MEDIKATION BEI ENTLASSUNG
   - Liste aller Medikamente mit Dosierung

7. LABORWERTE
   - Wichtigste/auffällige Laborwerte
   - Trend (Aufnahme vs. Entlassung)

8. EMPFEHLUNGEN
   - Weitere Verlaufskontrolle
   - Ambulante Weiterbehandlung
   - Medikamentenanpassungen

PATIENTENDATEN:
{patient_data}

---

Erstelle den Bericht als JSON mit folgender Struktur:
{{
  "patientInfo": {{
    "name": "...",
    "age": ...,
    "gender": "...",
    "admissionDate": "...",
    "dischargeDate": "...",
    "lengthOfStay": ...,
    "department": "..."
  }},
  "admissionReason": "...",
  "diagnoses": {{
    "primary": "...",
    "secondary": ["...", "..."]
  }},
  "clinicalCourse": "...",
  "therapy": "...",
  "medications": [
    {{
      "name": "...",
      "dose": "...",
      "frequency": "...",
      "indication": "..."
    }}
  ],
  "labs": {{
    "summary": "...",
    "notable": ["...", "..."]
  }},
  "recommendations": {{
    "followUp": ["...", "..."],
    "ambulatory": ["...", "..."],
    "lifestyle": ["...", "..."]
  }}
}}

Wichtig:
- Sei präzise und medizinisch korrekt
- Nutze die tatsächlichen Daten aus den Patientenakten
- Wenn Informationen fehlen, lasse das Feld leer oder schreibe "Keine Angaben"
- Formuliere professionell und klar
"""

            messages = [
                {
                    "role": "system",
                    "content": "Du bist ein medizinischer AI-Assistent, der Entlassungsberichte erstellt. Antworte NUR mit validen JSON, ohne zusätzlichen Text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            if self.llm_client == "ollama":
                # Ollama API call with format json
                logger.info("Calling Ollama for report generation...")
                response = requests.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.llm_model,
                        "messages": messages,
                        "stream": False,
                        "format": "json"  # Force JSON output
                    },
                    timeout=180  # Increased timeout for report generation
                )
                response.raise_for_status()
                result = response.json()
                content = result["message"]["content"]
                logger.info(f"Received response from Ollama: {len(content)} chars")
            else:
                # OpenAI API call
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content

            # Parse JSON response
            if not content or not content.strip():
                logger.error("Empty response from LLM")
                raise ValueError("Empty response from LLM")

            logger.info(f"Parsing JSON response: {content[:200]}...")
            report_json = json.loads(content)

            # Add metadata
            report_json['patient_id'] = patient_id
            report_json['generated_at'] = None  # Will be set by main.py

            return report_json

        except Exception as e:
            logger.error(f"Error generating structured report: {str(e)}")
            return self._generate_basic_report(patient_id, patient_data)

    def _generate_basic_report(self, patient_id: str, patient_data: str) -> Dict[str, Any]:
        """Generate basic report without LLM (fallback)"""
        return {
            'patient_id': patient_id,
            'patientInfo': {
                'name': 'Nicht verfügbar',
                'note': 'LLM nicht konfiguriert'
            },
            'rawData': patient_data[:1000] + "..." if len(patient_data) > 1000 else patient_data,
            'message': 'Bericht konnte nicht vollständig generiert werden (kein LLM-API-Key konfiguriert)'
        }

    def _load_patient_json(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Load structured patient data from JSON file"""
        try:
            # Try to find patient.json in sample-data directory
            patient_json_path = Path(f"/app/sample-data/{patient_id}/patient.json")

            if not patient_json_path.exists():
                logger.warning(f"No patient.json found for {patient_id}")
                return None

            with open(patient_json_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded structured data for {patient_id}")
                return data

        except Exception as e:
            logger.error(f"Error loading patient.json: {str(e)}")
            return None

    def _merge_structured_data(self, report: Dict[str, Any], structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge accurate structured data with AI-generated report"""
        try:
            # Extract demographics
            demographics = structured_data.get('demographics', {})
            admission = structured_data.get('admission', {})

            # Override patientInfo with accurate data
            if 'patientInfo' not in report:
                report['patientInfo'] = {}

            # Always use accurate structured data for critical fields
            report['patientInfo']['name'] = demographics.get('name', report['patientInfo'].get('name'))
            report['patientInfo']['age'] = demographics.get('age', report['patientInfo'].get('age'))
            report['patientInfo']['gender'] = demographics.get('gender', report['patientInfo'].get('gender'))

            # Use structured admission data
            report['patientInfo']['admissionDate'] = admission.get('admissionDate', report['patientInfo'].get('admissionDate'))
            report['patientInfo']['dischargeDate'] = admission.get('dischargeDate', report['patientInfo'].get('dischargeDate'))
            report['patientInfo']['lengthOfStay'] = admission.get('lengthOfStay', report['patientInfo'].get('lengthOfStay'))
            report['patientInfo']['department'] = admission.get('department', report['patientInfo'].get('department'))

            logger.info(f"Merged structured data: age={report['patientInfo']['age']}, name={report['patientInfo']['name']}")
            return report

        except Exception as e:
            logger.error(f"Error merging structured data: {str(e)}")
            return report
