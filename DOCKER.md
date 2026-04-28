# Docker Setup for Java Study App

Run the entire Java Study App in Docker — no local Python or Ollama installation needed (Docker takes care of everything).

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) installed and running

## Quick Start (Recommended)

### Using Docker Compose (Easiest)

Docker Compose automatically starts both Ollama and the Study App together:

```bash
# Start everything
docker-compose up

# First time: gives Ollama time to pull the model (2-5 minutes)
# Subsequent times: Much faster (model is cached)

# Open in browser: http://localhost:5000
```

To stop:
```bash
docker-compose down
```

To stop and remove saved data:
```bash
docker-compose down -v
```

---

## Advanced Docker Usage

### Build the Image

```bash
docker build -t java-study-app .
```

### Run Just the App

Requires Ollama running separately:

```bash
# Terminal 1: Run Ollama
docker run -it --rm -v ollama:/root/.ollama -p 11434:11434 ollama/ollama

# Terminal 2: Run the Study App (connects to Ollama)
docker run -p 5000:5000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  java-study-app
```

### Run with Custom Settings

```bash
docker run -p 5000:5000 \
  -e OLLAMA_MODEL=qwen2.5:7b \
  -e SERVER_HOST=0.0.0.0 \
  -e DEBUG_MODE=true \
  java-study-app
```

### Save Progress Between Runs

Mount the checkpoints file:

```bash
docker run -p 5000:5000 \
  -v $(pwd)/checkpoints.json:/app/checkpoints.json \
  java-study-app
```

### Use a Smaller Model

For limited resources:

```bash
docker-compose up -e OLLAMA_MODEL=qwen2.5:7b
```

Or edit `docker-compose.yml`:

```yaml
environment:
  OLLAMA_MODEL: qwen2.5:7b  # Change to 7b, 14b, or 32b
```

---

## Docker Compose Configuration

The `docker-compose.yml` includes:

- **ollama**: LLM service with persistent model storage
- **study_app**: Web application with auto-connect to Ollama
- **Volume mounting**: Persist checkpoints and questions across restarts

### Key Services

| Service | Port | Purpose |
|---------|------|---------|
| `ollama` | 11434 | LLM API (internal, not exposed by default) |
| `study_app` | 5000 | Web interface (http://localhost:5000) |

---

## Troubleshooting

### "Can't connect to Ollama"

Make sure Ollama service is running:
```bash
docker-compose up
```

### "Port 5000 already in use"

Use a different port:
```bash
docker run -p 5001:5000 java-study-app
```

Or in `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Changed from 5000:5000
```

### "Permission denied" (macOS/Linux)

Add yourself to docker group:
```bash
sudo usermod -aG docker $USER
```

Then restart Docker or log out and back in.

### Check Logs

```bash
docker-compose logs study_app
docker-compose logs ollama
```

### View Running Containers

```bash
docker ps
```

---

## Performance Tuning

### Limit Resources

Edit `docker-compose.yml` to limit CPU and memory:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'           # Max 2 CPU cores
      memory: 8G          # Max 8 GB RAM
```

### Use Lighter Model

For systems with <8GB RAM:

```yaml
environment:
  OLLAMA_MODEL: qwen2.5:7b
```

### Persistent Model Storage

Models are stored in the `ollama_data` volume and persist between container restarts — no re-downloading needed.

---

## Network Access

By default, the app is only accessible from your machine.

To share with others on your network:

```bash
# Bind to all interfaces
docker run -p 0.0.0.0:5000:5000 java-study-app

# Others can access: http://<your-ip>:5000
```

Or in `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:5000:5000"  # Accessible from network
```

---

## Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean everything at once
docker system prune -a
```

---

## Tips & Tricks

### Run in Detached Mode

Start in background and check logs separately:

```bash
docker-compose up -d
docker-compose logs -f study_app
```

### Restart Just One Service

```bash
docker-compose restart study_app
```

### Pull a Different Model

Enter the Ollama container and pull:

```bash
docker-compose exec ollama ollama pull qwen2.5:32b
```

### View Container Shell

```bash
docker-compose exec study_app sh
```

---

For more info on Docker, see: https://docs.docker.com/
