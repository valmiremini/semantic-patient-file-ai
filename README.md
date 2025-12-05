# Semantic Patient File AI Platform

Ein vollständiger, dockerisierter Prototyp einer KI-gestützten Plattform für das Gesundheitswesen mit semantischer Patientenakten-Analyse und automatischer Berichtgenerierung.

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Architektur](#architektur)
- [Tech-Stack](#tech-stack)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [API-Dokumentation](#api-dokumentation)
- [Beispiel-Patientendaten](#beispiel-patientendaten)
- [Erweiterbarkeit](#erweiterbarkeit)
- [Sicherheitshinweise](#sicherheitshinweise)
- [Lizenz](#lizenz)

## Überblick

Diese Plattform demonstriert den Einsatz von KI-Technologien (RAG - Retrieval-Augmented Generation) zur intelligenten Analyse von Patientendossiers im Gesundheitswesen. Der Prototyp ist vollständig dockerisiert und nutzt moderne Web-Technologien.

![Semantic Patient File AI](https://github.com/user-attachments/assets/544436a6-b3ed-4036-8231-3b916bad0834)


### Hauptfunktionen

1. **Semantic Patient File Chat**: Interaktive Chat-Oberfläche zur Befragung von Patientendossiers mit kontextbasierter KI-Antwortgenerierung

2. **Auto-Report Generator**: Automatische Generierung strukturierter Entlassungsberichte aus den verfügbaren Patientendaten

## Features

- **RAG-basierte Suche**: Semantische Suche in Patientenakten mit Vector Database (Qdrant)
- **Chat-Interface**: Natürlichsprachliche Interaktion mit den Patientendaten
- **Automatische Berichtgenerierung**: KI-gestützte Erstellung von Entlassungsberichten
- **Multi-Format-Support**: Verarbeitung von JSON, PDF und TXT-Dateien
- **Quellenangabe**: Transparente Darstellung der verwendeten Datenquellen
- **Docker-basiert**: Einfaches Setup mit Docker Compose
- **Beispieldaten**: Drei realistische (aber fiktive) Patientendossiers enthalten

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│                   (React Frontend)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (Node.js)                       │
│              Express + TypeScript                            │
│   Routes: /patients /chat /reports /upload                  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                AI Service (Python/FastAPI)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Embedding   │  │     RAG      │  │    Report    │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Qdrant Vector  │
                    │    Database     │
                    └─────────────────┘
```

## Tech-Stack

### Frontend
- **React** 18.2 - UI Framework
- **TypeScript** 5.3 - Type Safety
- **Vite** 5.0 - Build Tool
- **TailwindCSS** 3.3 - Styling
- **Lucide React** - Icons
- **React Markdown** - Markdown Rendering

### Backend
- **Node.js** 20 - Runtime
- **Express** 4.18 - Web Framework
- **TypeScript** 5.3 - Type Safety
- **Axios** - HTTP Client
- **Multer** - File Upload

### AI Service
- **Python** 3.11
- **FastAPI** 0.115 - API Framework
- **OpenAI API** - LLM & Embeddings
- **Qdrant Client** - Vector Database Client
- **LangChain** - AI Framework
- **PyPDF** - PDF Processing

### Infrastructure
- **Docker** & **Docker Compose** - Containerization
- **Qdrant** - Vector Database

## Voraussetzungen

- Docker & Docker Compose (Version 20.10+)
- OpenAI API Key (optional, für vollständige Funktionalität)
- 8GB RAM (empfohlen)
- 10GB freier Festplattenspeicher

## Installation

### 1. Repository klonen

```bash
git clone <repository-url>
cd semantic-patient-file-ai-prototype
```

### 2. Umgebungsvariablen konfigurieren

Kopieren Sie die Beispiel-Konfiguration:

```bash
cp .env.example .env
```

Bearbeiten Sie die `.env` Datei und fügen Sie Ihren OpenAI API Key ein:

```env
OPENAI_API_KEY=sk-...your-key-here...
MODEL_TYPE=openai
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

> **Hinweis**: Ohne API-Key funktioniert die Suche grundsätzlich, aber die LLM-Antworten sind eingeschränkt.

### 3. Docker Container starten

```bash
docker-compose up --build
```

Beim ersten Start werden alle Dependencies installiert und die Beispiel-Patientendaten geladen. Dies kann einige Minuten dauern.

### 4. Services überprüfen

Nach erfolgreichem Start sind folgende Services verfügbar:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **AI Service**: http://localhost:8000
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Konfiguration

### Umgebungsvariablen

#### AI Service

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `OPENAI_API_KEY` | OpenAI API Schlüssel | - |
| `MODEL_TYPE` | LLM Provider (openai/ollama) | openai |
| `EMBEDDING_MODEL` | Embedding Modell | text-embedding-3-small |
| `LLM_MODEL` | Chat Modell | gpt-4o-mini |
| `QDRANT_HOST` | Qdrant Host | qdrant |
| `QDRANT_PORT` | Qdrant Port | 6333 |

#### Backend

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `PORT` | Server Port | 3001 |
| `AI_SERVICE_URL` | AI Service URL | http://ai-service:8000 |

#### Frontend

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `VITE_BACKEND_URL` | Backend URL | http://localhost:3001 |

## Verwendung

### 1. Patienten auswählen

Nach dem Start sehen Sie die Liste der verfügbaren Patienten in der linken Seitenleiste. Klicken Sie auf einen Patienten, um ihn auszuwählen.

### 2. Chat-Interface nutzen

Wechseln Sie zur "Chat"-Ansicht und stellen Sie Fragen zu den Patientenakten:

**Beispielfragen:**
- "Gib mir eine Zusammenfassung"
- "Welche Diagnosen wurden gestellt?"
- "Welche Medikamente nimmt der Patient?"
- "Wie war der klinische Verlauf in den letzten 72 Stunden?"
- "Welche Laborwerte sind auffällig?"

Die KI durchsucht die Patientenakten semantisch und generiert kontextbasierte Antworten mit Quellenangaben.

### 3. Bericht generieren

Wechseln Sie zur "Bericht"-Ansicht und klicken Sie auf "Bericht generieren". Die KI erstellt automatisch einen strukturierten Entlassungsbericht mit folgenden Abschnitten:

- Patienteninformationen
- Grund der Hospitalisation
- Diagnosen (Haupt- und Nebendiagnosen)
- Klinischer Verlauf
- Therapie
- Medikation bei Entlassung
- Laborwerte (Zusammenfassung und auffällige Werte)
- Empfehlungen (Verlaufskontrolle, ambulante Betreuung, Lebensstil)

Der Bericht kann als JSON heruntergeladen werden.

## API-Dokumentation

### Backend API

#### GET /api/patients

Abrufen aller verfügbaren Patienten.

**Response:**
```json
[
  {
    "patient_id": "patient1",
    "name": "Max Mustermann",
    "age": 59,
    "gender": "männlich",
    "admission_date": "2024-11-15T08:30:00Z",
    "department": "Innere Medizin",
    "document_count": 3
  }
]
```

#### POST /api/chat

Chat-Anfrage mit RAG.

**Request:**
```json
{
  "patient_id": "patient1",
  "question": "Welche Diagnosen wurden gestellt?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Vorherige Frage"
    },
    {
      "role": "assistant",
      "content": "Vorherige Antwort"
    }
  ]
}
```

**Response:**
```json
{
  "answer": "Der Patient hat folgende Diagnosen...",
  "sources": [
    {
      "source": "patient.json",
      "section": "diagnoses",
      "score": 0.89,
      "text": "Diagnoseinformationen..."
    }
  ],
  "timestamp": "2024-11-21T10:30:00Z"
}
```

#### POST /api/reports/generate

Entlassungsbericht generieren.

**Request:**
```json
{
  "patient_id": "patient1"
}
```

**Response:**
```json
{
  "report": {
    "patient_id": "patient1",
    "patientInfo": {...},
    "diagnoses": {...},
    "clinicalCourse": "...",
    "medications": [...],
    "recommendations": {...}
  },
  "timestamp": "2024-11-21T10:30:00Z"
}
```

#### POST /api/upload

Patientendokumente hochladen.

**Request:** (multipart/form-data)
- `patient_id`: String
- `files`: File[] (JSON, PDF, TXT)

**Response:**
```json
{
  "patient_id": "new_patient",
  "files_processed": 3,
  "chunks_created": 45,
  "message": "Successfully processed 3 files with 45 chunks"
}
```

### AI Service API

Vollständige API-Dokumentation verfügbar unter: http://localhost:8000/docs (Swagger UI)

## Beispiel-Patientendaten

Das Projekt enthält drei vollständig ausgearbeitete, fiktive Patientendossiers:

### Patient 1: Max Mustermann
- **Alter**: 59 Jahre, männlich
- **Hauptdiagnose**: Akuter Myokardinfarkt (STEMI)
- **Abteilung**: Innere Medizin / Kardiologie
- **Verlauf**: 5 Tage stationär, erfolgreiche PCI mit Stentimplantation
- **Dokumente**:
  - patient.json (Stammdaten, Diagnosen, Medikation)
  - labs.txt (Laborverlauf über 5 Tage)
  - notes.txt (Klinischer Verlauf, Visiten, Prozeduren)

### Patient 2: Anna Schmidt
- **Alter**: 46 Jahre, weiblich
- **Hauptdiagnose**: Lobärpneumonie (bakteriell)
- **Abteilung**: Pneumologie
- **Verlauf**: 4 Tage stationär, erfolgreiche Antibiotikatherapie
- **Dokumente**:
  - patient.json
  - labs.txt
  - notes.txt

### Patient 3: Peter Meier
- **Alter**: 72 Jahre, männlich
- **Hauptdiagnose**: Kolonkarzinom (Stadium IIIB)
- **Abteilung**: Chirurgie
- **Verlauf**: 8 Tage stationär, laparoskopische Hemikolektomie
- **Dokumente**:
  - patient.json
  - labs.txt
  - notes.txt

Alle Daten sind vollständig erfunden und dienen ausschließlich zu Demonstrationszwecken.

## Erweiterbarkeit

### Neue Patienten hinzufügen

1. Erstellen Sie einen neuen Ordner in `sample-data/`:
```bash
mkdir sample-data/patient4
```

2. Fügen Sie Dokumente hinzu (JSON, PDF oder TXT):
```bash
sample-data/patient4/
├── patient.json
├── labs.txt
└── notes.txt
```

3. Starten Sie die Container neu:
```bash
docker-compose restart ai-service
```

### Alternative LLM-Provider

Das System unterstützt auch lokale LLMs über Ollama:

```env
MODEL_TYPE=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.1
```

### Frontend-Anpassungen

- Komponenten befinden sich in `frontend/src/components/`
- Styling mit TailwindCSS in `frontend/src/index.css`
- API-Service in `frontend/src/services/api.service.ts`

### Backend-Erweiterungen

- Neue Routes in `backend/src/routes/`
- Controller in `backend/src/controllers/`
- Services in `backend/src/services/`

### AI-Service-Erweiterungen

- Services in `ai-service/services/`
- Neue Endpoints in `ai-service/main.py`
- RAG-Logik in `ai-service/services/rag_service.py`

## Sicherheitshinweise

⚠️ **WICHTIG**: Dies ist ein Prototyp für Demonstrationszwecke!

- **Keine echten Patientendaten verwenden!** Alle Daten im System sind fiktiv.
- **Keine Produktionsumgebung**: Das System hat keine Authentifizierung oder Autorisierung.
- **Datenschutz**: Speichern Sie keine realen medizinischen Daten.
- **API-Keys**: Schützen Sie Ihre OpenAI API-Keys. Committen Sie niemals `.env`-Dateien.
- **DSGVO**: Bei Verwendung mit realen Daten müssen DSGVO-Anforderungen erfüllt werden.

### Für Produktionsumgebung erforderlich:

- Benutzer-Authentifizierung (OAuth2, JWT)
- Rollenbasierte Zugriffskontrolle (RBAC)
- Ende-zu-Ende-Verschlüsselung
- Audit-Logging
- Backup-Strategie
- Compliance mit medizinischen Standards (z.B. IHE, HL7 FHIR)
- DSGVO-Konformität
- Medizinprodukte-Zertifizierung (falls anwendbar)

## Troubleshooting

### Services starten nicht

```bash
# Logs prüfen
docker-compose logs -f

# Container neu bauen
docker-compose down
docker-compose up --build
```

### Qdrant Connection Error

```bash
# Warten bis Qdrant bereit ist
docker-compose ps

# Healthcheck prüfen
curl http://localhost:6333/health
```

### OpenAI API Fehler

- API-Key überprüfen in `.env`
- Rate Limits beachten
- Guthaben auf OpenAI Account prüfen

### Frontend verbindet nicht mit Backend

- Backend-URL in `frontend/.env` prüfen
- CORS-Einstellungen überprüfen
- Ports 3000, 3001, 8000 müssen frei sein

## Lizenz

MIT License - Dieses Projekt steht zur freien Verfügung für Lern- und Demonstrationszwecke.

---


## Support & Feedback

Bei Fragen oder Problemen öffnen Sie bitte ein Issue im Repository.
