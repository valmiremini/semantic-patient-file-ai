# System Architecture

Detaillierte Architektur-Dokumentation des Semantic Patient File AI Systems.

## Übersicht

Das System folgt einer modernen Microservices-Architektur mit klarer Trennung von Verantwortlichkeiten.

## Komponenten-Diagramm

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                               │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    React Frontend (Port 3000)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │ PatientList  │  │ChatInterface │  │ReportGenerator│      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  │              ▲              ▲              ▲                  │   │
│  │              └──────────────┴──────────────┘                  │   │
│  │                    API Service Client                         │   │
│  └────────────────────────────┬────────────────────────────────┘   │
│                               │ HTTP/REST                           │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                               │       API LAYER                      │
│  ┌────────────────────────────▼───────────────────────────────┐    │
│  │           Node.js Backend API (Port 3001)                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │ Patient  │  │   Chat   │  │  Report  │  │  Upload  │  │    │
│  │  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │  │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │    │
│  │       │             │              │              │         │    │
│  │  ┌────▼─────────────▼──────────────▼──────────────▼─────┐ │    │
│  │  │              AI Service Client                        │ │    │
│  │  └───────────────────────┬───────────────────────────────┘ │    │
│  └──────────────────────────┼─────────────────────────────────┘    │
│                             │ HTTP                                  │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────┐
│                             │        AI LAYER                        │
│  ┌──────────────────────────▼─────────────────────────────────┐    │
│  │         Python AI Service (FastAPI, Port 8000)              │    │
│  │                                                              │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │    │
│  │  │   Document     │  │   Embedding    │  │    RAG       │ │    │
│  │  │   Service      │  │   Service      │  │   Service    │ │    │
│  │  └────────┬───────┘  └───────┬────────┘  └──────┬───────┘ │    │
│  │           │                   │                   │          │    │
│  │           │        ┌──────────▼───────────────────▼───────┐ │    │
│  │           │        │      Qdrant Service Client          │ │    │
│  │           │        └──────────┬───────────────────────────┘ │    │
│  │           │                   │                              │    │
│  │           │        ┌──────────▼───────────────────────────┐ │    │
│  │           │        │       OpenAI API Client              │ │    │
│  │           │        └──────────────────────────────────────┘ │    │
│  │           │                                                  │    │
│  │  ┌────────▼────────┐                                        │    │
│  │  │  Report Service │                                        │    │
│  │  └─────────────────┘                                        │    │
│  └──────────────────────────┬───────────────────────────────────┘    │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
┌─────────────────────────────┼────────────────────────────────────────┐
│                             │       DATA LAYER                       │
│  ┌──────────────────────────▼───────────────────────────────────┐   │
│  │            Qdrant Vector Database (Port 6333)                 │   │
│  │                                                                │   │
│  │  Collection: patient_documents                                │   │
│  │  ┌──────────────────────────────────────────────────────┐    │   │
│  │  │  Vector: [1536 dimensions]                           │    │   │
│  │  │  Payload: {patient_id, text, source, section}        │    │   │
│  │  └──────────────────────────────────────────────────────┘    │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │            Sample Data (File System)                           │   │
│  │  patient1/  patient2/  patient3/                               │   │
│  │    ├── patient.json                                            │   │
│  │    ├── labs.txt                                                │   │
│  │    └── notes.txt                                               │   │
│  └────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                                │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    OpenAI API                                   │  │
│  │  • GPT-4o-mini (Text Generation)                               │  │
│  │  • text-embedding-3-small (Embeddings)                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

## Datenfluss

### 1. Chat-Anfrage

```
User Input
    │
    ▼
Frontend (ChatInterface)
    │
    │ POST /api/chat
    │ { patient_id, question, history }
    ▼
Backend API (chat.routes.ts)
    │
    │ Forward to AI Service
    │ POST /chat
    ▼
AI Service (rag_service.py)
    │
    ├─► Embedding Service
    │   └─► OpenAI API (create embedding)
    │
    ├─► Qdrant Service
    │   └─► Search similar vectors (RAG)
    │       └─► Returns: relevant chunks
    │
    └─► RAG Service
        ├─► Build context from chunks
        └─► OpenAI API (generate answer)
            └─► Returns: answer + sources
                │
                ▼
            Backend API
                │
                ▼
            Frontend
                │
                ▼
            Display to User
```

### 2. Bericht-Generierung

```
User Action
    │
    ▼
Frontend (ReportGenerator)
    │
    │ POST /api/reports/generate
    │ { patient_id }
    ▼
Backend API (report.routes.ts)
    │
    │ Forward to AI Service
    │ POST /generate-report
    ▼
AI Service (report_service.py)
    │
    ├─► Retrieve all patient data
    │   ├─► Multiple embedding queries
    │   └─► Qdrant searches
    │       └─► Collect all relevant chunks
    │
    └─► Report Service
        └─► OpenAI API (structured generation)
            └─► Returns: structured report JSON
                │
                ▼
            Backend API
                │
                ▼
            Frontend
                │
                ▼
            Display formatted report
```

### 3. Dokument-Upload

```
User Upload (Files)
    │
    ▼
Frontend (Upload Component)
    │
    │ POST /api/upload (multipart/form-data)
    │ { patient_id, files[] }
    ▼
Backend API (upload.routes.ts)
    │
    │ Forward files to AI Service
    │ POST /upload
    ▼
AI Service (document_service.py)
    │
    ├─► Process documents
    │   ├─► JSON: Extract structured data
    │   ├─► PDF: Extract text
    │   └─► TXT: Read text
    │       └─► Create chunks (overlapping)
    │
    ├─► Embedding Service
    │   └─► Create embeddings for chunks
    │       └─► OpenAI API
    │
    └─► Qdrant Service
        └─► Store vectors + metadata
            └─► Returns: success + stats
                │
                ▼
            Backend API
                │
                ▼
            Frontend
                │
                ▼
            Confirmation to User
```

## Technische Details

### Frontend (React + TypeScript)

**Komponenten-Hierarchie:**
```
App.tsx
├── PatientList.tsx
├── ChatInterface.tsx
└── ReportGenerator.tsx

Services:
└── api.service.ts (Axios HTTP Client)
```

**State Management**: React Hooks (useState, useEffect)
**Styling**: TailwindCSS utility-first
**Routing**: Single-Page Application (keine Router)

### Backend API (Node.js + Express)

**Layer-Architektur:**
```
Routes (Express Router)
    │
    ▼
Controllers (Request Handling)
    │
    ▼
Services (Business Logic)
    │
    ▼
External APIs (AI Service)
```

**Middleware-Stack:**
1. CORS (Cross-Origin Resource Sharing)
2. Body Parser (JSON)
3. Morgan (HTTP Logging)
4. Custom Logger
5. Error Handler

### AI Service (Python + FastAPI)

**Service-Architektur:**
```
FastAPI Main Application
├── Embedding Service
│   └── OpenAI Embeddings API
├── Qdrant Service
│   └── Vector DB Client
├── RAG Service
│   ├── Retrieval (Vector Search)
│   └── Generation (LLM)
├── Report Service
│   └── Structured Output Generation
└── Document Service
    ├── JSON Parser
    ├── PDF Parser
    └── Text Chunker
```

**Async Processing**: FastAPI mit async/await
**Dependency Injection**: FastAPI DI System
**Validation**: Pydantic Models

### Vector Database (Qdrant)

**Collection Schema:**
```
Collection: patient_documents
├── Vector: float[1536]  (Embedding dimension)
└── Payload:
    ├── patient_id: string
    ├── text: string
    ├── source: string
    └── section: string
```

**Index**: HNSW (Hierarchical Navigable Small World)
**Distance Metric**: Cosine Similarity
**Persistence**: Disk-based storage

## RAG (Retrieval-Augmented Generation)

### Embedding-Prozess

1. **Text Chunking**:
   - Chunk Size: 1000 Zeichen
   - Overlap: 200 Zeichen
   - Boundary Detection: Newline > Space

2. **Embedding Creation**:
   - Model: text-embedding-3-small
   - Dimension: 1536
   - Batch Processing: Multiple texts

3. **Storage**:
   - Vector + Metadata in Qdrant
   - Patient-ID als Filter

### Retrieval-Prozess

1. **Query Embedding**:
   - User question → Embedding

2. **Vector Search**:
   - Cosine Similarity Search
   - Filter: patient_id
   - Limit: Top 5 results
   - Threshold: Score > 0.3

3. **Context Building**:
   - Combine retrieved chunks
   - Add source information

### Generation-Prozess

1. **Prompt Engineering**:
   - System Prompt (Role Definition)
   - Context Injection
   - User Question

2. **LLM Call**:
   - Model: GPT-4o-mini
   - Temperature: 0.7
   - Max Tokens: 1000

3. **Response Formatting**:
   - Markdown Support
   - Source References

## Sicherheit & Performance

### Sicherheit

- **No Authentication** (Prototype only!)
- **Input Validation**: Pydantic models
- **File Type Restrictions**: JSON, PDF, TXT only
- **File Size Limits**: 10MB max
- **CORS**: Enabled for development

### Performance

- **Caching**: None (could be added)
- **Connection Pooling**: Axios, Qdrant Client
- **Async Operations**: FastAPI async
- **Vector Search**: O(log n) with HNSW
- **Batch Processing**: Multiple embeddings at once

### Skalierung

**Horizontal Scaling möglich für:**
- Frontend (Static Hosting)
- Backend API (Load Balancer)
- AI Service (Worker Pool)

**Vertical Scaling erforderlich für:**
- Qdrant (RAM für Vektoren)

**Bottlenecks:**
- OpenAI API Rate Limits
- Qdrant Search Performance
- Network Latency

## Deployment

### Development (Docker Compose)

```yaml
services:
  - qdrant (Vector DB)
  - ai-service (Python)
  - backend (Node.js)
  - frontend (React/Vite)
```

### Production Considerations

1. **Kubernetes Deployment**
2. **Managed Vector DB** (Qdrant Cloud)
3. **CDN für Frontend**
4. **API Gateway**
5. **Load Balancer**
6. **Monitoring & Logging** (Prometheus, ELK)
7. **Secrets Management** (Vault)
8. **SSL/TLS Certificates**

## Monitoring

### Health Checks

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:3001/health
- **AI Service**: http://localhost:8000/health
- **Qdrant**: http://localhost:6333/health

### Logs

- Docker Compose Logs
- Application Logs (Console)
- HTTP Access Logs (Morgan)

### Metrics (nicht implementiert, aber empfohlen)

- Request Count
- Response Times
- Error Rates
- Vector Search Performance
- LLM Token Usage

---

**Letzte Aktualisierung**: November 2024
