# Projektstruktur

Vollständige Übersicht über alle Dateien und Ordner im Projekt.

## Verzeichnisbaum

```
semantic-patient-file-ai-prototype/
│
├── 📁 ai-service/                          # Python AI Service (FastAPI)
│   ├── Dockerfile                          # Docker Image für AI Service
│   ├── requirements.txt                    # Python Dependencies
│   ├── main.py                             # FastAPI Application Entry Point
│   └── 📁 services/                        # Service Layer
│       ├── __init__.py                     # Package Initialization
│       ├── document_service.py             # Dokumenten-Verarbeitung (JSON/PDF/TXT)
│       ├── embedding_service.py            # OpenAI Embeddings
│       ├── qdrant_service.py              # Vector Database Client
│       ├── rag_service.py                 # Retrieval-Augmented Generation
│       └── report_service.py              # Bericht-Generierung
│
├── 📁 backend/                             # Node.js Backend API (Express)
│   ├── Dockerfile                          # Docker Image für Backend
│   ├── package.json                        # NPM Dependencies & Scripts
│   ├── tsconfig.json                       # TypeScript Configuration
│   └── 📁 src/                             # Source Code
│       ├── index.ts                        # Express Server Entry Point
│       ├── 📁 controllers/                 # Request Handler
│       │   ├── chat.controller.ts
│       │   ├── patient.controller.ts
│       │   ├── report.controller.ts
│       │   └── upload.controller.ts
│       ├── 📁 middleware/                  # Express Middleware
│       │   ├── error.middleware.ts
│       │   └── logger.middleware.ts
│       ├── 📁 routes/                      # API Routes
│       │   ├── chat.routes.ts
│       │   ├── patient.routes.ts
│       │   ├── report.routes.ts
│       │   └── upload.routes.ts
│       └── 📁 services/                    # Business Logic
│           └── ai.service.ts               # AI Service HTTP Client
│
├── 📁 frontend/                            # React Frontend (Vite)
│   ├── Dockerfile                          # Docker Image für Frontend
│   ├── package.json                        # NPM Dependencies & Scripts
│   ├── tsconfig.json                       # TypeScript Configuration
│   ├── tsconfig.node.json                  # TypeScript Config für Vite
│   ├── vite.config.ts                      # Vite Build Configuration
│   ├── tailwind.config.js                  # TailwindCSS Configuration
│   ├── postcss.config.js                   # PostCSS Configuration
│   ├── index.html                          # HTML Entry Point
│   └── 📁 src/                             # Source Code
│       ├── main.tsx                        # React Entry Point
│       ├── App.tsx                         # Main Application Component
│       ├── index.css                       # Global Styles (Tailwind)
│       ├── 📁 components/                  # React Components
│       │   ├── ChatInterface.tsx           # Chat UI mit RAG
│       │   ├── PatientList.tsx             # Patienten-Sidebar
│       │   └── ReportGenerator.tsx         # Bericht-Generator UI
│       ├── 📁 services/                    # API Clients
│       │   └── api.service.ts              # Backend API Client
│       └── 📁 types/                       # TypeScript Types
│           └── index.ts                    # Type Definitions
│
├── 📁 sample-data/                         # Beispiel-Patientendaten
│   ├── 📁 patient1/                        # Max Mustermann (STEMI)
│   │   ├── patient.json                    # Stammdaten, Diagnosen, Medikation
│   │   ├── labs.txt                        # Laborverlauf (5 Tage)
│   │   └── notes.txt                       # Klinischer Verlauf, Visiten
│   ├── 📁 patient2/                        # Anna Schmidt (Pneumonie)
│   │   ├── patient.json
│   │   ├── labs.txt
│   │   └── notes.txt
│   └── 📁 patient3/                        # Peter Meier (Kolonkarzinom)
│       ├── patient.json
│       ├── labs.txt
│       └── notes.txt
│
├── 📁 qdrant/                              # Qdrant Vector Database
│   └── 📁 storage/                         # Persistente Daten (wird erstellt)
│
├── docker-compose.yml                      # Docker Compose Orchestration
├── .env                                    # Environment Variables (OpenAI API Key)
├── .env.example                            # Example Environment Variables
├── .gitignore                              # Git Ignore Rules
│
├── 📄 README.md                            # Haupt-Dokumentation
├── 📄 QUICKSTART.md                        # 5-Minuten Quick Start Guide
├── 📄 ARCHITECTURE.md                      # Detaillierte Architektur-Dokumentation
└── 📄 PROJECT_STRUCTURE.md                 # Diese Datei
```

## Datei-Übersicht nach Typ

### Docker & Configuration (9 Dateien)

```
docker-compose.yml              # Orchestration aller Services
.env                            # Secrets & Configuration
.env.example                    # Configuration Template
.gitignore                      # Git Ignore Rules

ai-service/Dockerfile           # Python Container
backend/Dockerfile              # Node.js Container
frontend/Dockerfile             # React Container

ai-service/requirements.txt     # Python Dependencies
backend/package.json            # Node.js Dependencies
```

### Python Backend (7 Dateien)

```
ai-service/main.py                          # FastAPI Application (241 Zeilen)
ai-service/services/__init__.py
ai-service/services/embedding_service.py    # Embeddings (82 Zeilen)
ai-service/services/qdrant_service.py       # Vector DB (138 Zeilen)
ai-service/services/document_service.py     # Dokument-Parser (213 Zeilen)
ai-service/services/rag_service.py          # RAG Pipeline (157 Zeilen)
ai-service/services/report_service.py       # Report Generator (178 Zeilen)
```

**Total**: ~1009 Zeilen Python Code

### TypeScript Backend (14 Dateien)

```
backend/src/index.ts                        # Express Server (53 Zeilen)
backend/src/services/ai.service.ts          # AI Client (97 Zeilen)

backend/src/controllers/chat.controller.ts       # (24 Zeilen)
backend/src/controllers/patient.controller.ts    # (15 Zeilen)
backend/src/controllers/report.controller.ts     # (23 Zeilen)
backend/src/controllers/upload.controller.ts     # (26 Zeilen)

backend/src/routes/chat.routes.ts           # (7 Zeilen)
backend/src/routes/patient.routes.ts        # (7 Zeilen)
backend/src/routes/report.routes.ts         # (7 Zeilen)
backend/src/routes/upload.routes.ts         # (24 Zeilen)

backend/src/middleware/error.middleware.ts  # (13 Zeilen)
backend/src/middleware/logger.middleware.ts # (5 Zeilen)

backend/tsconfig.json                       # TypeScript Config
```

**Total**: ~301 Zeilen TypeScript Code

### TypeScript/React Frontend (13 Dateien)

```
frontend/src/main.tsx                       # Entry Point (8 Zeilen)
frontend/src/App.tsx                        # Main App (114 Zeilen)
frontend/src/index.css                      # Tailwind Styles (28 Zeilen)

frontend/src/components/ChatInterface.tsx       # (218 Zeilen)
frontend/src/components/PatientList.tsx         # (79 Zeilen)
frontend/src/components/ReportGenerator.tsx     # (267 Zeilen)

frontend/src/services/api.service.ts        # API Client (57 Zeilen)
frontend/src/types/index.ts                 # Type Definitions (54 Zeilen)

frontend/index.html                         # HTML Entry
frontend/vite.config.ts                     # Vite Config
frontend/tsconfig.json                      # TypeScript Config
frontend/tsconfig.node.json                 # TypeScript Node Config
frontend/tailwind.config.js                 # TailwindCSS Config
```

**Total**: ~825 Zeilen TypeScript/React Code

### Sample Data (9 Dateien)

```
sample-data/patient1/patient.json           # 187 Zeilen JSON
sample-data/patient1/labs.txt               # 168 Zeilen
sample-data/patient1/notes.txt              # 252 Zeilen

sample-data/patient2/patient.json           # 95 Zeilen JSON
sample-data/patient2/labs.txt               # 144 Zeilen
sample-data/patient2/notes.txt              # 180 Zeilen

sample-data/patient3/patient.json           # 147 Zeilen JSON
sample-data/patient3/labs.txt               # 218 Zeilen
sample-data/patient3/notes.txt              # 313 Zeilen
```

**Total**: ~1704 Zeilen Beispieldaten

### Dokumentation (4 Dateien)

```
README.md                       # Haupt-Dokumentation (437 Zeilen)
QUICKSTART.md                   # Quick Start Guide (107 Zeilen)
ARCHITECTURE.md                 # Architektur-Details (521 Zeilen)
PROJECT_STRUCTURE.md            # Diese Datei (245 Zeilen)
```

**Total**: ~1310 Zeilen Dokumentation

## Statistik

### Code Metrics

| Kategorie | Dateien | Zeilen | Sprache |
|-----------|---------|--------|---------|
| AI Service | 7 | ~1009 | Python |
| Backend API | 14 | ~301 | TypeScript |
| Frontend | 13 | ~825 | TypeScript/React |
| Sample Data | 9 | ~1704 | JSON/Text |
| Dokumentation | 4 | ~1310 | Markdown |
| Configuration | 9 | ~200 | YAML/JSON/JS |
| **TOTAL** | **56** | **~5349** | - |

### Service Ports

| Service | Port | Protokoll |
|---------|------|-----------|
| Frontend | 3000 | HTTP |
| Backend | 3001 | HTTP |
| AI Service | 8000 | HTTP |
| Qdrant | 6333 | HTTP |
| Qdrant gRPC | 6334 | gRPC |

### Docker Images

| Service | Base Image | Size (ca.) |
|---------|-----------|------------|
| ai-service | python:3.11-slim | ~800 MB |
| backend | node:20-alpine | ~200 MB |
| frontend | node:20-alpine | ~200 MB |
| qdrant | qdrant/qdrant:latest | ~400 MB |

## API Endpoints

### Backend API (Port 3001)

```
GET    /health                  # Health Check
GET    /api/patients            # Liste aller Patienten
POST   /api/chat                # Chat mit RAG
POST   /api/reports/generate    # Bericht generieren
POST   /api/upload              # Dokumente hochladen
```

### AI Service (Port 8000)

```
GET    /health                  # Health Check
GET    /patients                # Liste aller Patienten
POST   /chat                    # RAG Query
POST   /generate-report         # Report Generation
POST   /upload                  # Document Upload
GET    /docs                    # Swagger API Docs
```

## Abhängigkeiten

### AI Service (Python)

- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- qdrant-client==1.12.0
- openai==1.54.3
- langchain==0.3.7
- pypdf==4.3.1

### Backend (Node.js)

- express==4.18.2
- axios==1.6.2
- cors==2.8.5
- multer==1.4.5-lts.1
- typescript==5.3.3

### Frontend (React)

- react==18.2.0
- vite==5.0.8
- tailwindcss==3.3.6
- axios==1.6.2
- lucide-react==0.294.0
- react-markdown==9.0.1

## Build-Zeiten (ca.)

| Service | Erster Build | Rebuild |
|---------|--------------|---------|
| ai-service | ~3-4 min | ~30 sec |
| backend | ~1-2 min | ~10 sec |
| frontend | ~1-2 min | ~10 sec |
| qdrant | ~30 sec | - |

## Entwicklungs-Workflow

```
1. Code ändern in src/
2. Hot Reload (automatisch)
   - Frontend: Vite HMR
   - Backend: nodemon
   - AI Service: uvicorn --reload
3. Logs prüfen: docker-compose logs -f
4. Browser: http://localhost:3000
```

## Deployment-Größen

| Component | Dev Size | Prod Size |
|-----------|----------|-----------|
| Frontend Build | ~5 MB | ~500 KB |
| Backend Build | ~2 MB | ~1 MB |
| AI Service | ~800 MB | ~800 MB |
| Qdrant Data | ~100 MB | variable |

## Maintenance

### Regelmäßige Updates

```bash
# Backend Dependencies
cd backend && npm update

# Frontend Dependencies
cd frontend && npm update

# AI Service Dependencies
cd ai-service && pip install -U -r requirements.txt
```

### Logs Rotation

```bash
# Docker Logs löschen
docker-compose down
docker system prune -a
```

### Backup

```bash
# Qdrant Daten sichern
tar -czf qdrant-backup.tar.gz qdrant/storage/
```

---

**Erstellt am**: November 2024
**Letzte Aktualisierung**: November 2024
