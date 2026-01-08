FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY apps/api /app/api

WORKDIR /app/api

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
