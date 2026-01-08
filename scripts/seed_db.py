"""
Seed database avec données MVP
- 20 docs knowledge
- 15 influenceurs
- 3 posts + 50 commentaires + 10 threads DM
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import json

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://influence:influence123@localhost:5432/influenceconnect")
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ============================================================================
# Knowledge Docs (pour ingestion)
# ============================================================================

KNOWLEDGE_DOCS = [
    # Policies
    {
        "title": "Politique de réponse allergies",
        "content": "En cas de mention d'allergie, réaction cutanée ou effet indésirable, TOUJOURS rediriger vers service client en DM. Ne JAMAIS donner de conseil médical. Demander détails produit et symptômes.",
        "doc_type": "policy",
        "category": "compliance"
    },
    {
        "title": "Politique grossesse/allaitement",
        "content": "Pour utilisatrices enceintes ou allaitantes, recommander consultation dermatologue. Éviter recommandations produits sans validation. Proposer redirection service client spécialisé.",
        "doc_type": "policy",
        "category": "compliance"
    },
    {
        "title": "Politique mineurs",
        "content": "Si utilisateur < 18 ans, recommander consultation adulte ou dermatologue. Éviter vente directe. Proposer informations générales uniquement.",
        "doc_type": "policy",
        "category": "compliance"
    },
    # FAQs
    {
        "title": "FAQ - Livraison standard",
        "content": "Livraison standard gratuite dès 30€ d'achat. Délai 3-5 jours ouvrés. Livraison express disponible (5.90€, 24-48h). Suivi par email et SMS.",
        "doc_type": "faq",
        "category": "livraison"
    },
    {
        "title": "FAQ - Retours et remboursements",
        "content": "Retours gratuits sous 30 jours. Produits non ouverts uniquement. Remboursement sous 7 jours après réception. Formulaire retour sur site web.",
        "doc_type": "faq",
        "category": "retours"
    },
    {
        "title": "FAQ - Programme fidélité",
        "content": "1€ = 1 point. 100 points = 5€ de réduction. Points valables 1 an. Avantages exclusifs membres : ventes privées, échantillons gratuits, birthday gift.",
        "doc_type": "faq",
        "category": "fidelite"
    },
    # Products
    {
        "title": "Revitalift Filler HA - Soin anti-âge",
        "content": "Crème anti-rides avec acide hyaluronique concentré. Réduit apparence rides et ridules. Hydrate intensément. Pour peaux matures, tous types. Prix: 24.99€. Application matin et soir sur visage propre.",
        "doc_type": "product",
        "category": "soin_visage"
    },
    {
        "title": "Infaillible 24H Foundation - Fond de teint longue tenue",
        "content": "Fond de teint ultra-résistant 24h. Couvrance modulable moyenne à haute. 40 teintes disponibles. Fini mat naturel. Prix: 16.99€. Application pinceau ou éponge.",
        "doc_type": "product",
        "category": "maquillage"
    },
    {
        "title": "Elseve Bond Repair - Shampooing réparateur",
        "content": "Shampooing pour cheveux abîmés, colorés. Technologie peptides réparateurs. Renforce fibre capillaire. Prix: 7.99€. Utilisation quotidienne cheveux mouillés, rincer.",
        "doc_type": "product",
        "category": "cheveux"
    },
    {
        "title": "UV Defender SPF50+ - Protection solaire",
        "content": "Fluide protecteur très haute protection UVA/UVB. Texture légère non grasse. Tous types peaux. Prix: 19.99€. Application quotidienne avant exposition 20 min.",
        "doc_type": "product",
        "category": "solaire"
    },
    # More products...
    {
        "title": "Age Perfect Golden Age - Crème de jour",
        "content": "Soin anti-âge peaux matures 60+. Enrichi en calcium. Raffermit et réconforte. Prix: 22.99€.",
        "doc_type": "product",
        "category": "soin_visage"
    },
    {
        "title": "Men Expert Hydra Energetic - Gel hydratant homme",
        "content": "Gel hydratant 24h homme. Non gras, pénétration rapide. Prix: 9.99€.",
        "doc_type": "product",
        "category": "homme"
    },
    {
        "title": "Paradise Mascara - Volume et longueur",
        "content": "Mascara ultra-noir. Brosse souple. Volume intense. Prix: 12.99€.",
        "doc_type": "product",
        "category": "maquillage"
    },
    {
        "title": "Casting Crème Gloss - Coloration sans ammoniaque",
        "content": "Coloration semi-permanente cheveux. Sans ammoniaque. 28 teintes. Prix: 8.99€.",
        "doc_type": "product",
        "category": "coloration"
    },
    # Claims
    {
        "title": "Claims acide hyaluronique",
        "content": "Acide hyaluronique: molécule naturellement présente dans peau. Propriétés hydratantes et repulpantes. Testé dermatologiquement. Réduit apparence rides (études cliniques).",
        "doc_type": "claim",
        "category": "ingredients"
    },
    {
        "title": "Claims vitamine C",
        "content": "Vitamine C: antioxydant puissant. Éclaircit teint, réduit taches brunes. Stimule production collagène. Usage quotidien recommandé.",
        "doc_type": "claim",
        "category": "ingredients"
    },
    {
        "title": "Claims rétinol",
        "content": "Rétinol (vitamine A): anti-rides prouvé. Stimule renouvellement cellulaire. Application soir uniquement. Protection solaire obligatoire jour.",
        "doc_type": "claim",
        "category": "ingredients"
    },
    {
        "title": "Routine anti-âge type",
        "content": "Routine anti-âge: 1) Nettoyant doux matin/soir 2) Sérum vitamine C matin 3) Crème hydratante SPF jour 4) Sérum rétinol soir 5) Crème nuit. Constance = clé résultats.",
        "doc_type": "faq",
        "category": "routine"
    },
    {
        "title": "Routine peau acnéique",
        "content": "Routine peau grasse/acnéique: 1) Gel nettoyant purifiant 2) Lotion astringente 3) Sérum acide salicylique 4) Hydratant matifiant non-comédogène. Éviter sur-nettoyage.",
        "doc_type": "faq",
        "category": "routine"
    },
    {
        "title": "Guide choix fond de teint",
        "content": "Choix fond de teint: 1) Déterminer sous-ton (chaud/froid/neutre) 2) Tester nuque/mâchoire 3) Choisir finish (mat/naturel/lumineux) selon type peau 4) Couvrance selon besoin.",
        "doc_type": "faq",
        "category": "maquillage"
    }
]

# ============================================================================
# Influenceurs
# ============================================================================

INFLUENCERS = [
    {"name": "Sophie Beauté", "instagram_handle": "@sophiebeaute", "tags": {"undertone": "warm", "hair_type": "wavy", "color_goal": "blonde", "locale": "fr", "formats": ["reels", "stories"]}, "promo_code": "SOPHIE10"},
    {"name": "Marie Glow", "instagram_handle": "@marieglow", "tags": {"undertone": "cool", "hair_type": "straight", "color_goal": "brunette", "locale": "fr", "formats": ["posts", "reels"]}, "promo_code": "MARIE15"},
    {"name": "Léa Makeup", "instagram_handle": "@leamakeup", "tags": {"undertone": "neutral", "hair_type": "curly", "color_goal": "red", "locale": "fr", "formats": ["stories", "posts"]}, "promo_code": "LEA20"},
    {"name": "Chloé Skincare", "instagram_handle": "@chloeskincare", "tags": {"undertone": "warm", "hair_type": "straight", "locale": "fr", "formats": ["reels"]}, "promo_code": "CHLOE10"},
    {"name": "Emma Beauty Pro", "instagram_handle": "@emmabeautypro", "tags": {"undertone": "cool", "hair_type": "wavy", "locale": "fr", "formats": ["posts", "stories", "reels"]}, "promo_code": "EMMA25"},
    {"name": "Laura Cheveux", "instagram_handle": "@lauracheveux", "tags": {"undertone": "neutral", "hair_type": "coily", "color_goal": "brunette", "locale": "fr", "formats": ["reels", "posts"]}, "promo_code": "LAURA15"},
    {"name": "Camille Paris", "instagram_handle": "@camilleparis", "tags": {"undertone": "warm", "hair_type": "curly", "color_goal": "blonde", "locale": "fr", "formats": ["stories"]}, "promo_code": "CAMILLE10"},
    {"name": "Julie Natural", "instagram_handle": "@julienatural", "tags": {"undertone": "cool", "hair_type": "wavy", "locale": "fr", "formats": ["posts", "reels"]}, "promo_code": "JULIE20"},
    {"name": "Anna Glam", "instagram_handle": "@annaglam", "tags": {"undertone": "neutral", "hair_type": "straight", "color_goal": "silver", "locale": "fr", "formats": ["reels", "stories"]}, "promo_code": "ANNA15"},
    {"name": "Sarah Trends", "instagram_handle": "@sarahtrends", "tags": {"undertone": "warm", "hair_type": "coily", "locale": "fr", "formats": ["posts"]}, "promo_code": "SARAH10"},
    {"name": "Océane Lifestyle", "instagram_handle": "@oceanelifestyle", "tags": {"undertone": "cool", "hair_type": "curly", "color_goal": "blonde", "locale": "fr", "formats": ["stories", "reels"]}, "promo_code": "OCEANE25"},
    {"name": "Pauline Beauty", "instagram_handle": "@paulinebeauty", "tags": {"undertone": "neutral", "hair_type": "wavy", "locale": "fr", "formats": ["posts", "reels"]}, "promo_code": "PAULINE15"},
    {"name": "Manon Makeup", "instagram_handle": "@manonmakeup", "tags": {"undertone": "warm", "hair_type": "straight", "color_goal": "red", "locale": "fr", "formats": ["reels"]}, "promo_code": "MANON20"},
    {"name": "Clara Chic", "instagram_handle": "@clarachic", "tags": {"undertone": "cool", "hair_type": "coily", "locale": "fr", "formats": ["posts", "stories"]}, "promo_code": "CLARA10"},
    {"name": "Inès Glowing", "instagram_handle": "@inesglowing", "tags": {"undertone": "neutral", "hair_type": "curly", "color_goal": "brunette", "locale": "fr", "formats": ["reels", "posts", "stories"]}, "promo_code": "INES15"}
]

# ============================================================================
# Posts et commentaires simulés
# ============================================================================

POSTS = [
    {"content": "Nouvelle routine anti-âge Revitalift 💆‍♀️ Résultats après 4 semaines !"},
    {"content": "Fond de teint Infaillible 24H - Mon avis complet après 2 mois 🎨"},
    {"content": "Routine capillaire Bond Repair pour cheveux abîmés 💇‍♀️"}
]

COMMENTS = [
    "Quelle crème tu utilises ?",
    "C'est efficace contre les rides ?",
    "Prix du fond de teint svp ?",
    "J'ai la peau grasse, ça marche pour moi ?",
    "Où acheter ce produit ?",
    "Livraison combien de temps ?",
    "J'ai fait une allergie avec votre crème, que faire ?",
    "Super produit merci !",
    "Quelle teinte pour peau claire ?",
    "Routine complète anti-âge SVP",
    # ... 40 autres commentaires variés
]

# ============================================================================
# Main seed function
# ============================================================================

async def seed_database():
    """Seed database with MVP data"""
    
    print("🌱 Starting database seed...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Seed influencers
            print("\n📸 Seeding influencers...")
            for inf in INFLUENCERS:
                await db.execute(
                    text("""
                        INSERT INTO influencers (name, instagram_handle, tags, promo_code, commission_rate, status)
                        VALUES (:name, :instagram_handle, :tags, :promo_code, 0.10, 'active')
                    """),
                    {
                        "name": inf["name"],
                        "instagram_handle": inf["instagram_handle"],
                        "tags": json.dumps(inf["tags"]),
                        "promo_code": inf["promo_code"]
                    }
                )
            await db.commit()
            print(f"✅ Created {len(INFLUENCERS)} influencers")
            
            # 2. Seed posts
            print("\n📝 Seeding posts...")
            post_ids = []
            for post in POSTS:
                result = await db.execute(
                    text("""
                        INSERT INTO posts (platform, content, created_at)
                        VALUES ('instagram', :content, NOW())
                        RETURNING id
                    """),
                    {"content": post["content"]}
                )
                post_ids.append(result.scalar_one())
            await db.commit()
            print(f"✅ Created {len(post_ids)} posts")
            
            # 3. Seed comments
            print("\n💬 Seeding comments...")
            for i, comment_text in enumerate(COMMENTS[:50]):
                post_id = post_ids[i % len(post_ids)]
                await db.execute(
                    text("""
                        INSERT INTO comments (post_id, platform, author_id, author_username, content, created_at)
                        VALUES (:post_id, 'instagram', :author_id, :author, :content, NOW())
                    """),
                    {
                        "post_id": post_id,
                        "author_id": f"user_{i}",
                        "author": f"user_{i}",
                        "content": comment_text
                    }
                )
            await db.commit()
            print(f"✅ Created {min(50, len(COMMENTS))} comments")
            
            # 4. Seed DM threads
            print("\n💌 Seeding DM threads...")
            for i in range(10):
                # Create thread
                result = await db.execute(
                    text("""
                        INSERT INTO threads (platform, participant_id, participant_username, status, created_at)
                        VALUES ('instagram', :participant_id, :username, 'open', NOW())
                        RETURNING id
                    """),
                    {"participant_id": f"dm_user_{i}", "username": f"dm_user_{i}"}
                )
                thread_id = result.scalar_one()
                
                # Add messages
                messages = [
                    "Bonjour, je cherche une crème anti-âge",
                    "J'ai la peau sèche et sensible",
                    "Budget environ 30€"
                ]
                for msg in messages:
                    await db.execute(
                        text("""
                            INSERT INTO messages (thread_id, platform, message_type, sender_id, sender_username, content, created_at)
                            VALUES (:thread_id, 'instagram', 'dm', :sender_id, :sender, :content, NOW())
                        """),
                        {
                            "thread_id": thread_id,
                            "sender_id": f"dm_user_{i}",
                            "sender": f"dm_user_{i}",
                            "content": msg
                        }
                    )
            await db.commit()
            print(f"✅ Created 10 DM threads with messages")
            
            print("\n✅ Database seed complete!")
            print("\nNext steps:")
            print("1. Run: python scripts/ingest_knowledge.py")
            print("2. Start app: docker compose up")
            
        except Exception as e:
            print(f"\n❌ Error seeding database: {str(e)}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())
