FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Remove heavy packages not needed for mocks
RUN sed -i '/torch/d; /sentence-transformers/d' requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY apps/api /app/api
COPY apps/api/db/init.sql /app/api/db/init.sql

WORKDIR /app/api

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
# Wait for database and run migrations\n\
sleep 5\n\
psql $DATABASE_URL -f /app/api/db/init.sql 2>/dev/null || true\n\
# Start app\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start app
CMD ["/app/start.sh"]
