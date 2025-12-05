# Quick Start Guide

Schnellanleitung zum Starten des Projekts in 5 Minuten.

## Voraussetzungen

- Docker & Docker Compose installiert
- OpenAI API Key (optional, aber empfohlen)

## Schritte

### 1. OpenAI API Key eintragen (optional)

Öffnen Sie die `.env` Datei und fügen Sie Ihren API Key ein:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

**Ohne API Key**: Das System funktioniert grundsätzlich, aber KI-Antworten sind eingeschränkt.

### 2. Docker Container starten

```bash
docker-compose up --build
```

Beim ersten Start werden alle Dependencies installiert und die Beispieldaten geladen. Dies dauert ca. 3-5 Minuten.

### 3. Warten bis alle Services laufen

Warten Sie, bis alle Container gestartet sind. Sie sollten folgende Ausgaben sehen:

```
✅ qdrant      | Service started successfully
✅ ai-service  | Application startup complete
✅ backend     | Backend server running on port 3001
✅ frontend    | VITE ready in 1234 ms
```

### 4. Frontend öffnen

Öffnen Sie Ihren Browser und navigieren Sie zu:

**http://localhost:3000**

### 5. Erste Schritte in der Anwendung

1. **Patienten auswählen**: Klicken Sie auf einen Patienten in der linken Seitenleiste (z.B. "Max Mustermann")

2. **Chat ausprobieren**: Stellen Sie eine Frage, z.B.:
   - "Gib mir eine Zusammenfassung"
   - "Welche Diagnosen wurden gestellt?"
   - "Welche Medikamente nimmt der Patient?"

3. **Bericht generieren**: Wechseln Sie zur "Bericht"-Ansicht und klicken Sie auf "Bericht generieren"

## Verfügbare Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001/health
- **AI Service**: http://localhost:8000/docs (API-Dokumentation)
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Stoppen

```bash
docker-compose down
```

## Neu starten

```bash
docker-compose restart
```

## Logs anzeigen

```bash
# Alle Logs
docker-compose logs -f

# Nur AI Service
docker-compose logs -f ai-service

# Nur Backend
docker-compose logs -f backend

# Nur Frontend
docker-compose logs -f frontend
```

## Probleme?

### Port bereits belegt

Wenn Port 3000, 3001 oder 8000 bereits belegt ist:

```bash
# Ports in docker-compose.yml anpassen
# Beispiel: "3002:3000" statt "3000:3000"
```

### Qdrant startet nicht

```bash
# Alte Daten löschen
rm -rf qdrant/storage
docker-compose up --build
```

### Container startet nicht

```bash
# Alles neu bauen
docker-compose down -v
docker-compose up --build
```

## Nächste Schritte

- Lesen Sie die vollständige [README.md](README.md) für Details
- Erkunden Sie die [API-Dokumentation](http://localhost:8000/docs)
- Fügen Sie eigene Patientendaten hinzu (siehe README.md)

Viel Erfolg! 🚀
