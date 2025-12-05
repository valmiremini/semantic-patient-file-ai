import os
import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database"""

    def __init__(self, embedding_dimension: int = 1536):
        self.host = os.getenv("QDRANT_HOST", "qdrant")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = "patient_documents"
        self.embedding_dimension = embedding_dimension

        # Initialize client
        self.client = QdrantClient(host=self.host, port=self.port)
        logger.info(f"Connected to Qdrant at {self.host}:{self.port}")

        # Create collection if it doesn't exist
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Collection created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error ensuring collection: {str(e)}")
            raise

    def store_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> List[str]:
        """Store vectors with metadata in Qdrant"""
        try:
            points = []
            ids = []

            for vector, payload in zip(vectors, payloads):
                point_id = str(uuid.uuid4())
                ids.append(point_id)

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Stored {len(points)} vectors in Qdrant")
            return ids

        except Exception as e:
            logger.error(f"Error storing vectors: {str(e)}")
            raise

    def search(
        self,
        query_vector: List[float],
        patient_id: str,
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            # Create filter for patient_id
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="patient_id",
                        match=MatchValue(value=patient_id)
                    )
                ]
            )

            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })

            logger.info(f"Found {len(formatted_results)} results for patient {patient_id}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []

    def delete_by_patient(self, patient_id: str):
        """Delete all documents for a patient"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted documents for patient {patient_id}")

        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def get_all_patient_ids(self) -> List[str]:
        """Get all unique patient IDs in the database"""
        try:
            # Scroll through all points and collect unique patient_ids
            patient_ids = set()
            offset = None

            while True:
                results, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                if not results:
                    break

                for point in results:
                    if 'patient_id' in point.payload:
                        patient_ids.add(point.payload['patient_id'])

                if offset is None:
                    break

            return list(patient_ids)

        except Exception as e:
            logger.error(f"Error getting patient IDs: {str(e)}")
            return []
