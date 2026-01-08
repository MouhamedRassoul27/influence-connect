# Influence Connect

MVP production-ready : IA Community Manager L'Oréal pour Instagram avec HITL (Human-in-the-Loop).

## 🎯 Vue d'ensemble

Simule l'essentiel d'Instagram (Inbox DM + Commentaires) pour tester une IA community manager avec :
- Génération de réponses intelligentes (Claude Sonnet)
- Classification intent + risque (Claude Haiku)  
- Vérification brand-safe (Claude Opus)
- Console de validation humaine (HITL)
- Matching influenceur automatique
- Tracking d'attribution UTM

## 🏗️ Architecture

```
influence-connect/
├── apps/
│   ├── web/          # Next.js (Inbox, Comments, Influencers, Dashboard)
│   └── api/          # FastAPI (Pipeline IA, RAG, DB)
├── packages/
│   └── shared/       # Types TypeScript partagés
├── knowledge/        # Documents RAG (policies, FAQ, produits)
├── docker-compose.yml
└── scripts/          # seed, ingest, replay
```

## 🚀 Démarrage rapide (5 minutes)

```bash
# 1. Clone et setup
git clone <repo>
cd influence-connect
cp .env.example .env

# 2. Config API keys
# Éditer .env et ajouter :
ANTHROPIC_API_KEY=sk-ant-...

# 3. Lancer tout
docker compose up -d

# 4. Seed données
docker compose exec api python scripts/seed_db.py

# 5. Ingest knowledge base
docker compose exec api python scripts/ingest_knowledge.py

# 6. Ouvrir l'app
open http://localhost:3000
```

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| Web (Next.js) | 3000 | Interface utilisateur |
| API (FastAPI) | 8000 | Backend + IA |
| Postgres | 5432 | Base de données |
| pgAdmin | 5050 | Admin DB (optionnel) |

## 🤖 Pipeline IA

Pour chaque message entrant (DM ou commentaire) :

```
1. CLASSIFY (Haiku)    → intent + risk_flags
2. RETRIEVE (pgvector) → knowledge top-5
3. DRAFT (Sonnet)      → réponse + produits + influenceurs
4. VERIFY (Opus)       → brand-safe check
5. HITL (Humain)       → approve/edit/escalate
6. SEND (stub)         → prêt pour Meta API
```

## 🎨 Pages principales

- `/inbox` - Liste threads DM avec filtres
- `/thread/[id]` - Conversation + contexte + actions IA
- `/comments` - Posts simulés + commentaires + reply
- `/influencers` - CRUD ambassadeurs + matching tags
- `/dashboard` - KPIs temps réel
- `/eval` - Métriques qualité IA

## 📊 Modèles Claude (config exacte)

```yaml
# apps/api/config/models.yaml
classifier: claude-haiku-4-5-20251001
drafter: claude-sonnet-4-5-20250929
verifier: claude-opus-4-5-20251101
embeddings: BAAI/bge-m3
```

## 🔒 Conformité

- ❌ Jamais de conseil médical
- ⚠️ Escalade auto : allergies, effets indésirables, mineurs, litiges, presse
- ✅ HITL par défaut, autopilot uniquement pour intents safe + risk faible
- 🏷️ Option "Réponse générée par IA" (toggle par marché)

## 📈 Tracking attribution

- Liens UTM automatiques : `?utm_source=instagram&utm_medium=dm&utm_campaign=...`
- Codes promo par influenceur
- Events : click, view_content, add_to_cart, purchase

## 🧪 Tests

```bash
# Tests backend
docker compose exec api pytest

# Tests smoke
curl http://localhost:8000/health
curl http://localhost:8000/api/classify -X POST -d '{"text":"Quelle crème anti-âge?"}'

# Replay messages
docker compose exec api python scripts/replay_events.py
```

## 📚 Documentation

- [Architecture détaillée](docs/ARCHITECTURE.md)
- [Guide développeur](docs/DEV_GUIDE.md)
- [Prompts système](apps/api/prompts/README.md)
- [Schéma DB](apps/api/db/schema.sql)

## 🔧 Configuration

Variables d'environnement importantes :

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Modèles (override config/models.yaml)
MODEL_CLASSIFIER=claude-haiku-4-5-20251001
MODEL_DRAFTER=claude-sonnet-4-5-20250929
MODEL_VERIFIER=claude-opus-4-5-20251101

# DB
DATABASE_URL=postgresql://user:pass@db:5432/influenceconnect

# Features
HITL_REQUIRED=true
AUTOPILOT_SAFE_INTENTS=availability,pricing,where_to_buy
SHOW_AI_BADGE=false  # "Réponse générée par IA"
```

## 🎯 Roadmap

- [x] MVP Pipeline IA complet
- [x] HITL console
- [x] RAG avec pgvector
- [x] Tracking attribution
- [ ] Intégration Meta Graph API réelle
- [ ] A/B testing autopilot vs HITL
- [ ] Multi-langue (FR/EN/ES)
- [ ] Mobile app (React Native)

## 📄 License

MIT
