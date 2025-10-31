# ---------- Stage 1: Base ----------
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask py5paisa

# Expose port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
