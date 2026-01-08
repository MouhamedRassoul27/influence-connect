# 🚀 Influence Connect - Guide de Démarrage Rapide

## Prérequis
- Docker Desktop installé et démarré
- Port 8000 et 5432 disponibles

## 1. Démarrer l'application

```bash
cd /tmp/influence-connect

# Démarrer tous les services
docker compose -f docker-compose.simple.yml up -d

# Attendre 10 secondes que tout démarre
sleep 10

# Vérifier que l'API fonctionne
curl http://localhost:8000/api/health
```

## 2. Seed la base de données

```bash
# Créer les données de test (influenceurs, threads, messages)
docker compose -f docker-compose.simple.yml exec api python /app/scripts/seed_db.py

# Générer les embeddings pour la knowledge base (optionnel, nécessite connexion Internet)
docker compose -f docker-compose.simple.yml exec api python /app/scripts/ingest_knowledge.py
```

## 3. Tester l'API

### Health check
```bash
curl http://localhost:8000/api/health
```

### Documentation interactive (Swagger)
```
http://localhost:8000/docs
```

### Lister les threads
```bash
curl http://localhost:8000/api/messages/inbox
```

### Traiter un message (pipeline IA complet)
```bash
curl -X POST http://localhost:8000/api/messages/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Quelle crème anti-rides pour peau sèche ?",
    "platform": "instagram",
    "sender_id": "test_user_123",
    "sender_username": "test_user"
  }'
```

**📱 Pour connecter à Instagram réel**: Voir [INSTAGRAM_SETUP.md](INSTAGRAM_SETUP.md)

## 4. Voir les logs

```bash
# Tous les services
docker compose -f docker-compose.simple.yml logs -f

# API seulement
docker compose -f docker-compose.simple.yml logs -f api

# Dernières 50 lignes
docker compose -f docker-compose.simple.yml logs --tail=50 api
```

## 5. Arrêter l'application

```bash
# Arrêter les services (garde les données)
docker compose -f docker-compose.simple.yml down

# Arrêter ET supprimer les données
docker compose -f docker-compose.simple.yml down -v
```

## 🎯 URLs importantes

- **API Health**: http://localhost:8000/api/health
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **Database**: localhost:5432 (user: influence, password: influence123)
- **Redis**: localhost:6379

## ⚙️ Configuration

Modifier `.env` pour personnaliser :
```env
ANTHROPIC_API_KEY=sk-ant-votre-clé  # REQUIS pour l'IA
HITL_REQUIRED=true                   # Validation humaine obligatoire
LOG_LEVEL=INFO                       # DEBUG pour plus de logs
```

## 🔧 Troubleshooting

### Port 8000 déjà utilisé
```bash
lsof -ti:8000 | xargs kill -9
```

### Reconstruire les images
```bash
docker compose -f docker-compose.simple.yml build --no-cache
docker compose -f docker-compose.simple.yml up -d
```

### Réinitialiser complètement
```bash
docker compose -f docker-compose.simple.yml down -v
docker system prune -a
docker compose -f docker-compose.simple.yml up -d --build
```

### Vérifier les conteneurs
```bash
docker compose -f docker-compose.simple.yml ps
```

## 📝 Notes

- Le modèle d'embedding (BAAI/bge-m3) se télécharge au premier appel RAG (~2GB)
- Sans connexion Internet, le RAG ne fonctionnera pas mais le reste de l'API oui
- Les clés Anthropic de test sont requises pour les appels IA réels
