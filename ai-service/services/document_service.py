import json
import logging
from typing import List, Dict, Any
from pypdf import PdfReader
import io
import os

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing patient documents"""

    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def process_json(self, content: bytes, patient_id: str, filename: str) -> List[Dict[str, Any]]:
        """Process JSON patient data"""
        try:
            data = json.loads(content.decode('utf-8'))
            chunks = []

            # Create chunks from different sections
            # Patient demographics
            if 'demographics' in data:
                demo = data['demographics']
                text = "PATIENTENDATEN / DEMOGRAPHIE:\n\n"
                text += f"Der Patient heißt {demo.get('name', 'Unknown')}.\n"
                text += f"Der Patient ist {demo.get('age', 'Unknown')} Jahre alt.\n"
                text += f"Geburtsdatum: {demo.get('dateOfBirth', 'Unknown')}\n"
                text += f"Geschlecht: {demo.get('gender', 'Unknown')}\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'demographics'
                })

            # Admission info
            if 'admission' in data:
                adm = data['admission']
                text = "AUFNAHME-INFORMATIONEN:\n"
                text += f"Aufnahmedatum: {adm.get('admissionDate', 'Unknown')}\n"
                text += f"Abteilung: {adm.get('department', 'Unknown')}\n"
                text += f"Station: {adm.get('ward', 'Unknown')}\n"
                text += f"Aufnahmegrund: {adm.get('admissionReason', 'Unknown')}\n"

                if 'dischargeDate' in adm and adm['dischargeDate']:
                    text += f"Entlassungsdatum: {adm['dischargeDate']}\n"
                    text += f"Aufenthaltsdauer: {adm.get('lengthOfStay', 'Unknown')} Tage\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'admission'
                })

            # Diagnoses
            if 'diagnoses' in data:
                text = "DIAGNOSEN:\n"
                for diag in data['diagnoses']:
                    text += f"\n- {diag.get('description', 'Unknown')} ({diag.get('code', 'N/A')})\n"
                    text += f"  Typ: {diag.get('type', 'Unknown')}\n"
                    text += f"  Diagnosedatum: {diag.get('diagnosedDate', 'Unknown')}\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'diagnoses'
                })

            # Medications
            if 'medications' in data:
                text = "MEDIKATION:\n"
                for med in data['medications']:
                    text += f"\n- {med.get('name', 'Unknown')} {med.get('dose', '')}\n"
                    text += f"  Frequenz: {med.get('frequency', 'Unknown')}\n"
                    text += f"  Verabreichung: {med.get('route', 'Unknown')}\n"
                    text += f"  Indikation: {med.get('indication', 'Unknown')}\n"
                    text += f"  Start: {med.get('startDate', 'Unknown')}\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'medications'
                })

            # Allergies
            if 'allergies' in data and data['allergies']:
                text = "ALLERGIEN:\n"
                for allergy in data['allergies']:
                    text += f"- {allergy.get('substance', 'Unknown')}: {allergy.get('reaction', 'Unknown')} "
                    text += f"(Schwere: {allergy.get('severity', 'Unknown')})\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'allergies'
                })

            # Procedures
            if 'procedures' in data:
                text = "DURCHGEFÜHRTE PROZEDUREN:\n"
                for proc in data['procedures']:
                    text += f"\n- {proc.get('name', 'Unknown')}\n"
                    text += f"  Datum: {proc.get('date', 'Unknown')}\n"
                    text += f"  Beschreibung: {proc.get('description', 'N/A')}\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'procedures'
                })

            # Vital signs
            if 'vitalSigns' in data:
                text = "VITALPARAMETER:\n"
                for vital in data['vitalSigns'][:5]:  # Last 5 measurements
                    text += f"\n{vital.get('timestamp', 'Unknown')}:\n"
                    text += f"  RR: {vital.get('bloodPressure', 'N/A')} mmHg\n"
                    text += f"  HF: {vital.get('heartRate', 'N/A')}/min\n"
                    text += f"  Temp: {vital.get('temperature', 'N/A')}°C\n"
                    text += f"  SpO2: {vital.get('oxygenSaturation', 'N/A')}%\n"
                    text += f"  AF: {vital.get('respiratoryRate', 'N/A')}/min\n"

                chunks.append({
                    'text': text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'vital_signs'
                })

            logger.info(f"Processed JSON file {filename}: {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing JSON: {str(e)}")
            return []

    def process_pdf(self, content: bytes, patient_id: str, filename: str) -> List[Dict[str, Any]]:
        """Process PDF document"""
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)

            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"

            # Split into chunks
            chunks = self._split_text(full_text, patient_id, filename)

            logger.info(f"Processed PDF file {filename}: {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return []

    def process_text(self, content: bytes, patient_id: str, filename: str) -> List[Dict[str, Any]]:
        """Process text document"""
        try:
            text = content.decode('utf-8')

            # Split into chunks
            chunks = self._split_text(text, patient_id, filename)

            logger.info(f"Processed text file {filename}: {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []

    def _split_text(self, text: str, patient_id: str, filename: str) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at a newline or space
            if end < len(text):
                # Look for newline
                newline_pos = text.rfind('\n', start, end)
                if newline_pos > start + self.chunk_size // 2:
                    end = newline_pos
                else:
                    # Look for space
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start + self.chunk_size // 2:
                        end = space_pos

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'patient_id': patient_id,
                    'source': filename,
                    'section': 'document'
                })

            start = end - self.chunk_overlap

        return chunks

    def get_available_patients(self) -> List[Dict[str, Any]]:
        """Get list of available patients from sample data"""
        patients = []
        sample_data_dir = "/app/sample-data"

        try:
            if not os.path.exists(sample_data_dir):
                return []

            for patient_dir in os.listdir(sample_data_dir):
                patient_path = os.path.join(sample_data_dir, patient_dir)
                if not os.path.isdir(patient_path):
                    continue

                # Try to read patient.json for metadata
                patient_json_path = os.path.join(patient_path, "patient.json")
                if os.path.exists(patient_json_path):
                    with open(patient_json_path, 'r') as f:
                        data = json.load(f)

                    patient_info = {
                        'patient_id': patient_dir,
                        'name': data.get('demographics', {}).get('name', 'Unknown'),
                        'age': data.get('demographics', {}).get('age', 0),
                        'gender': data.get('demographics', {}).get('gender', 'Unknown'),
                        'admission_date': data.get('admission', {}).get('admissionDate'),
                        'department': data.get('admission', {}).get('department'),
                        'document_count': len([f for f in os.listdir(patient_path) if os.path.isfile(os.path.join(patient_path, f))])
                    }

                    patients.append(patient_info)

            return patients

        except Exception as e:
            logger.error(f"Error getting available patients: {str(e)}")
            return []
