FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN groupadd -r app && useradd -r -g app app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 8004

# Drop privileges
USER app

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
