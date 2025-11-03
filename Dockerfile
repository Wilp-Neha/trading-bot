# ---------- Stage 1: Base ----------
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
