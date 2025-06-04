# This Dockerfile builds the full stack application
# It combines both frontend and backend into a single container

# Multi-stage build for production deployment
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static

# Create a simple static file server for frontend
RUN echo 'from fastapi.staticfiles import StaticFiles\n\
from fastapi.responses import FileResponse\n\
import os\n\
\n\
# Mount static files\n\
app.mount("/static", StaticFiles(directory="static"), name="static")\n\
\n\
@app.get("/{full_path:path}")\n\
async def serve_frontend(full_path: str):\n\
    """Serve frontend files for any non-API routes"""\n\
    if full_path.startswith("chat") or full_path.startswith("inventory") or full_path.startswith("sessions"):\n\
        # Let FastAPI handle API routes\n\
        return\n\
    \n\
    file_path = os.path.join("static", full_path)\n\
    if os.path.exists(file_path) and os.path.isfile(file_path):\n\
        return FileResponse(file_path)\n\
    else:\n\
        # Return index.html for SPA routing\n\
        return FileResponse("static/index.html")' >> main.py

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
