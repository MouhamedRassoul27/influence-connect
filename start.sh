#!/bin/bash

echo "🚀 Influence Connect - Quick Start"
echo "==================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter to continue..."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Seed database: docker compose exec api python /app/scripts/seed_db.py"
    echo "2. Ingest knowledge: docker compose exec api python /app/scripts/ingest_knowledge.py"
    echo "3. Open frontend: http://localhost:3000"
    echo "4. API docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: docker compose logs -f"
    echo "Stop: docker compose down"
else
    echo "❌ Error starting services. Check logs with: docker compose logs"
    exit 1
fi
