# 📱 Configuration Instagram pour Influence Connect

## 🎯 Vue d'ensemble

Pour recevoir et répondre aux DMs Instagram, vous devez configurer l'API Meta Graph et connecter votre compte Instagram Business.

⚠️ **Important**: L'intégration Instagram nécessite:
- Un compte Instagram Business (pas un compte personnel)
- Une Page Facebook liée au compte Instagram
- Une App Meta Developer configurée
- Des permissions spécifiques approuvées par Meta

---

## 📋 Prérequis

1. **Compte Instagram Business**
   - Convertir votre compte personnel en Business: Paramètres → Compte → Passer à un compte professionnel
   - Ou créer un nouveau compte Business

2. **Page Facebook**
   - Créer une Page Facebook si nécessaire
   - Lier votre compte Instagram à cette Page: Paramètres IG → Compte → Pages liées

3. **Compte Meta Developer**
   - S'inscrire sur https://developers.facebook.com
   - Vérifier votre compte (téléphone, email)

---

## 🔧 Étape 1: Créer une App Meta

### 1.1 Créer l'application
```
1. Aller sur https://developers.facebook.com/apps
2. Cliquer "Créer une app"
3. Choisir le type: "Business"
4. Remplir:
   - Nom de l'app: "Influence Connect"
   - Email de contact: votre email
   - Compte professionnel: créer si nécessaire
5. Cliquer "Créer l'app"
```

### 1.2 Ajouter Instagram Graph API
```
1. Dans le tableau de bord de l'app
2. Chercher "Instagram" dans les produits
3. Cliquer "Configurer" sur "Instagram Graph API"
4. Accepter les conditions
```

---

## 🔑 Étape 2: Obtenir les Tokens

### 2.1 App ID et App Secret
```
Tableau de bord → Paramètres → Paramètres de base

Copier:
- App ID (ID de l'app)
- App Secret (Clé secrète de l'app - cliquer "Afficher")
```

### 2.2 Access Token de Page
```
1. Aller dans Outils → Explorateur de l'API Graph
2. Sélectionner votre app dans le menu déroulant
3. Cliquer "Générer un jeton d'accès"
4. Sélectionner votre Page Facebook
5. Autoriser les permissions:
   - pages_manage_metadata
   - pages_read_engagement
   - pages_messaging
   - instagram_basic
   - instagram_manage_messages
   - instagram_manage_comments

6. Copier le token généré
```

### 2.3 Instagram Account ID
```bash
# Utiliser l'Explorateur d'API Graph
# Requête GET:
/{page-id}?fields=instagram_business_account

# Ou avec curl:
curl -X GET "https://graph.facebook.com/v18.0/{PAGE_ID}?fields=instagram_business_account&access_token={ACCESS_TOKEN}"

# Réponse:
{
  "instagram_business_account": {
    "id": "17841... <-- Copier cet ID"
  }
}
```

---

## ⚙️ Étape 3: Configurer l'Application

### 3.1 Créer le fichier .env
```bash
cd /tmp/influence-connect

cat > .env << 'EOF'
# Anthropic AI
ANTHROPIC_API_KEY=sk-ant-votre-clé-réelle

# Instagram / Meta Graph API
META_APP_ID=votre_app_id
META_APP_SECRET=votre_app_secret
META_ACCESS_TOKEN=votre_page_access_token
INSTAGRAM_ACCOUNT_ID=votre_instagram_business_account_id

# Webhook
WEBHOOK_VERIFY_TOKEN=un_token_secret_aléatoire_que_vous_choisissez

# Database & Redis (déjà configurés)
DATABASE_URL=postgresql://influence:influence123@db:5432/influenceconnect
REDIS_URL=redis://redis:6379

# Models
MODEL_CLASSIFIER=claude-haiku-4-5-20251001
MODEL_DRAFTER=claude-sonnet-4-5-20250929
MODEL_VERIFIER=claude-opus-4-5-20251101
EMBEDDING_MODEL=BAAI/bge-m3

# Features
HITL_REQUIRED=true
SHOW_AI_BADGE=false
LOG_LEVEL=INFO
EOF
```

### 3.2 Redémarrer l'API
```bash
docker compose -f docker-compose.simple.yml restart api
```

---

## 🌐 Étape 4: Exposer votre Application (Webhooks)

Instagram doit pouvoir envoyer des webhooks à votre serveur. En développement local, utilisez **ngrok**:

### 4.1 Installer ngrok
```bash
# macOS
brew install ngrok

# Ou télécharger: https://ngrok.com/download
```

### 4.2 Créer un compte ngrok
```
1. S'inscrire sur https://ngrok.com
2. Copier votre authtoken
3. Configurer: ngrok config add-authtoken VOTRE_TOKEN
```

### 4.3 Lancer le tunnel
```bash
# Dans un terminal séparé
ngrok http 8000

# Copier l'URL HTTPS affichée, ex: https://abc123.ngrok.io
```

---

## 🔗 Étape 5: Configurer les Webhooks Meta

### 5.1 Ajouter l'URL de callback
```
1. Tableau de bord Meta App → Produits → Webhooks
2. Cliquer "Configurer" pour Instagram
3. URL de rappel: https://votre-url-ngrok.io/api/webhooks/instagram
4. Token de vérification: le même que WEBHOOK_VERIFY_TOKEN dans .env
5. Cliquer "Vérifier et enregistrer"
```

### 5.2 S'abonner aux événements
```
Cocher les événements:
- messages
- messaging_postbacks
- message_echoes (optionnel)

Cliquer "S'abonner"
```

---

## ✅ Étape 6: Tester la Connexion

### 6.1 Vérifier le webhook
```bash
# Vérifier les logs de l'API
docker compose -f docker-compose.simple.yml logs -f api

# Vous devriez voir:
# "Webhook verified successfully"
```

### 6.2 Envoyer un DM de test
```
1. Depuis votre téléphone ou un autre compte
2. Envoyer un DM à votre compte Instagram Business
3. Message de test: "Bonjour, je cherche une crème hydratante"
```

### 6.3 Vérifier la réception
```bash
# Voir les logs en temps réel
docker compose -f docker-compose.simple.yml logs -f api | grep -E "(Received|Processing|Draft)"

# Vérifier dans l'inbox API
curl http://localhost:8000/api/messages/inbox

# Voir les messages en attente
curl http://localhost:8000/api/messages/pending
```

---

## 🧪 Test Manuel (Sans Instagram)

Pour tester le pipeline sans configurer Instagram:

### Simuler un message entrant
```bash
curl -X POST http://localhost:8000/api/messages/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Salut, tu recommandes quoi pour les peaux grasses ?",
    "platform": "instagram",
    "sender_id": "test_user_123",
    "sender_username": "test_beaute"
  }'
```

### Réponse attendue
```json
{
  "message_id": 1,
  "classification": {
    "category": "product_inquiry",
    "intent": "recommendation_request",
    "urgency": "normal",
    "requires_human": false
  },
  "draft": {
    "text": "...",
    "confidence": 0.85,
    "rag_sources": [...]
  },
  "status": "pending_approval",
  "next_action": "human_review_required"
}
```

---

## 🔐 Permissions Meta (Production)

Pour passer en production, demander à Meta l'approbation des permissions:

### Permissions requises
- `pages_messaging` - Répondre aux messages
- `instagram_manage_messages` - Gérer les DMs Instagram
- `instagram_basic` - Infos de base du compte
- `pages_manage_metadata` - Métadonnées de la page

### Processus d'approbation
```
1. Tableau de bord → Révision de l'app
2. Ajouter les permissions à réviser
3. Fournir:
   - Vidéo de démo de l'app
   - Explication du cas d'usage
   - URL de politique de confidentialité
   - Conditions d'utilisation
4. Soumettre pour révision (délai: 2-7 jours)
```

---

## 🚨 Troubleshooting

### "Webhook verification failed"
```bash
# Vérifier que WEBHOOK_VERIFY_TOKEN dans .env correspond
# Vérifier que ngrok est bien lancé
# Vérifier les logs: docker compose logs api
```

### "Invalid access token"
```bash
# Le token a peut-être expiré
# Regénérer un token de longue durée:

curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_TOKEN}"
```

### "Messages not received"
```bash
# Vérifier que le compte est bien Business
# Vérifier la subscription webhook
# Vérifier que ngrok est actif
# Tester l'endpoint manuellement:

curl https://votre-url-ngrok.io/api/health
```

### "Permission error"
```
# Vérifier que toutes les permissions sont accordées
# Aller dans Explorateur API → Permissions
# Régénérer le token avec toutes les permissions
```

---

## 📊 Monitoring

### Voir les webhooks reçus
```bash
# Logs Meta App
Tableau de bord → Webhooks → Afficher les événements récents

# Logs API locale
docker compose logs -f api
```

### Statistiques
```bash
# Messages traités
curl http://localhost:8000/api/stats/messages

# Taux d'approbation HITL
curl http://localhost:8000/api/stats/hitl
```

---

## 🎯 Prochaines Étapes

Une fois l'intégration Instagram configurée:

1. **Configurer les influenceurs**: Ajouter via API ou base de données
2. **Alimenter la knowledge base**: Ajouter des docs produits
3. **Tester le workflow complet**: DM → Classification → Draft → Validation → Envoi
4. **Monitorer les performances**: Temps de réponse, satisfaction
5. **Optimiser les prompts**: Ajuster selon les retours

---

## 📚 Ressources

- [Meta Graph API - Instagram](https://developers.facebook.com/docs/instagram-api)
- [Instagram Messaging](https://developers.facebook.com/docs/messenger-platform/instagram)
- [Webhooks Instagram](https://developers.facebook.com/docs/graph-api/webhooks/getting-started/instagram)
- [Ngrok Documentation](https://ngrok.com/docs)

---

## ⚡ Quick Start (Résumé)

```bash
# 1. Créer app Meta + obtenir tokens
# 2. Configurer .env
# 3. Redémarrer l'API
docker compose -f docker-compose.simple.yml restart api

# 4. Lancer ngrok
ngrok http 8000

# 5. Configurer webhook Meta avec URL ngrok
# 6. Envoyer un DM de test
# 7. Vérifier les logs
docker compose logs -f api
```

Votre système est maintenant connecté à Instagram ! 🎉
