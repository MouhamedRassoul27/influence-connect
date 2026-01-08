"""
L'Oréal Tools Service - Integrated with Skin Genius, Virtual Try-On, etc.
"""

import logging
from typing import List, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# L'Oréal Product Catalog (actual products)
LOREAL_PRODUCTS = {
    "peau_grasse": [
        {
            "id": "pure-zone-gel",
            "name": "Pure Zone Gel Purifiant",
            "category": "Nettoyage",
            "price": "18.99 EUR",
            "benefits": ["Purifiant", "Léger", "Régule le sébum"],
            "url": "https://www.loreal-paris.fr/pure-zone-gel-purifiant.html",
            "ingredients": ["Zinc", "Surfactants doux"]
        },
        {
            "id": "effaclar-duo",
            "name": "Effaclar Duo+",
            "category": "Soin",
            "price": "22.99 EUR",
            "benefits": ["Anti-imperfections", "Sans huile", "Absorption rapide"],
            "url": "https://www.loreal-paris.fr/effaclar-duo.html",
            "ingredients": ["Acide salicylique", "Niacinamide"]
        },
    ],
    "peau_seche": [
        {
            "id": "hydra-genius",
            "name": "Hydra Genius Moisturizer",
            "category": "Hydratation",
            "price": "24.99 EUR",
            "benefits": ["Hydratant", "Léger", "SPF 25"],
            "url": "https://www.loreal-paris.fr/hydra-genius.html",
            "ingredients": ["Hyaluronic acid", "Aloe vera"]
        },
        {
            "id": "revitalift",
            "name": "Revitalift Classic Cream",
            "category": "Anti-âge",
            "price": "29.99 EUR",
            "benefits": ["Raffermissant", "Anti-rides", "Nourrissant"],
            "url": "https://www.loreal-paris.fr/revitalift.html",
            "ingredients": ["Pro-retinol", "Pro-calcium"]
        },
    ],
    "sensible": [
        {
            "id": "toleriane-cleanser",
            "name": "Toleriane Purifying Foaming Cleanser",
            "category": "Nettoyage",
            "price": "14.99 EUR",
            "benefits": ["Doux", "Hypoallergénique", "Sans savon"],
            "url": "https://www.loreal-paris.fr/toleriane-cleanser.html",
            "ingredients": ["Prebiotic thermal water"]
        },
    ]
}

# Skin Types & Concerns Map
SKIN_TYPES = {
    "grasse": "peau_grasse",
    "gras": "peau_grasse",
    "oily": "peau_grasse",
    "seche": "peau_seche",
    "dry": "peau_seche",
    "sensible": "sensible",
    "sensitive": "sensible",
    "mixte": "peau_grasse",
    "combination": "peau_grasse",
}

class SkinGeniusAnalysis(BaseModel):
    skin_type: str
    concerns: List[str]
    recommendations: List[Dict]
    routine: Dict
    virtual_try_on_url: Optional[str] = None

class LoreaToolService:
    """L'Oréal integrated tools service"""
    
    async def skin_genius_analysis(self, user_response: Dict) -> SkinGeniusAnalysis:
        """
        Skin Genius Diagnostic - Analyze skin and provide personalized routine
        Based on: https://www.loreal-paris.fr/skin-genius.html
        """
        try:
            # Extract skin info from user response
            skin_type = user_response.get("skin_type", "").lower()
            concerns = user_response.get("concerns", [])
            
            # Map to L'Oréal categories
            category = SKIN_TYPES.get(skin_type, "peau_grasse")
            
            # Get products
            products = LOREAL_PRODUCTS.get(category, [])
            
            # Create routine
            routine = {
                "morning": [
                    "Cleanse with Toleriane or Pure Zone",
                    "Apply toner if needed",
                    "Apply moisturizer with SPF"
                ],
                "evening": [
                    "Cleanse",
                    "Apply treatment serum",
                    "Apply night cream"
                ],
                "weekly": [
                    "Clay mask (Peel Mud or similar)",
                    "Gentle exfoliation"
                ]
            }
            
            # Add virtual try-on link
            virtual_try_on = "https://www.loreal-paris.fr/realite-virtuelle.html"
            
            analysis = SkinGeniusAnalysis(
                skin_type=skin_type,
                concerns=concerns,
                recommendations=products[:3],
                routine=routine,
                virtual_try_on_url=virtual_try_on
            )
            
            logger.info(f"✅ Skin Genius Analysis: {skin_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Skin Genius error: {e}")
            raise
    
    async def virtual_try_on(self, product_id: str, user_profile: Dict) -> Dict:
        """
        Virtual Try-On Tool
        Based on: https://www.loreal-paris.fr/realite-virtuelle.html
        """
        try:
            # Find product
            product = None
            for category_products in LOREAL_PRODUCTS.values():
                for p in category_products:
                    if p["id"] == product_id:
                        product = p
                        break
            
            if not product:
                return {"error": "Product not found"}
            
            # Simulate virtual try-on
            simulation = {
                "product": product,
                "try_on_url": f"https://www.loreal-paris.fr/realite-virtuelle.html?product={product_id}",
                "results": {
                    "texture_feel": "Léger, non-gras",
                    "skin_improvement": "Appearance améliore en 7 jours",
                    "compatibility_score": 0.92
                },
                "success": True
            }
            
            logger.info(f"✅ Virtual Try-On: {product['name']}")
            return simulation
            
        except Exception as e:
            logger.error(f"❌ Virtual Try-On error: {e}")
            return {"error": str(e)}
    
    async def personalized_routine(self, skin_type: str, concerns: List[str]) -> Dict:
        """Create personalized skincare routine with L'Oréal products"""
        try:
            category = SKIN_TYPES.get(skin_type.lower(), "peau_grasse")
            products = LOREAL_PRODUCTS.get(category, [])
            
            routine = {
                "skin_profile": {
                    "type": skin_type,
                    "concerns": concerns
                },
                "morning_routine": {
                    "step_1": "Cleanse with " + (products[0]["name"] if products else "Cleanser"),
                    "step_2": "Apply hydrating toner",
                    "step_3": "Moisturize with SPF protection"
                },
                "evening_routine": {
                    "step_1": "Remove makeup with micellar water",
                    "step_2": "Cleanse with " + (products[0]["name"] if products else "Cleanser"),
                    "step_3": "Apply treatment serum",
                    "step_4": "Night moisturizer"
                },
                "weekly_treatment": {
                    "mask": "Clay mask for deep cleansing",
                    "frequency": "1-2 times per week"
                },
                "recommended_products": [p["name"] for p in products[:3]],
                "skin_genius_link": "https://www.loreal-paris.fr/skin-genius.html"
            }
            
            logger.info(f"✅ Created personalized routine for: {skin_type}")
            return routine
            
        except Exception as e:
            logger.error(f"❌ Routine creation error: {e}")
            return {}
    
    async def product_recommendation(self, concern: str) -> List[Dict]:
        """Recommend products for specific concern"""
        try:
            concern_map = {
                "acne": "peau_grasse",
                "imperfections": "peau_grasse",
                "dryness": "peau_seche",
                "wrinkles": "peau_seche",
                "sensitivity": "sensible",
            }
            
            category = concern_map.get(concern.lower(), "peau_grasse")
            products = LOREAL_PRODUCTS.get(category, [])
            
            logger.info(f"✅ Recommended {len(products)} products for: {concern}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Product recommendation error: {e}")
            return []
    
    async def ingredient_search(self, ingredient: str) -> List[Dict]:
        """Search products containing specific ingredient"""
        try:
            matching_products = []
            ingredient_lower = ingredient.lower()
            
            for category_products in LOREAL_PRODUCTS.values():
                for p in category_products:
                    if any(ingredient_lower in ing.lower() for ing in p.get("ingredients", [])):
                        matching_products.append(p)
            
            logger.info(f"✅ Found {len(matching_products)} products with {ingredient}")
            return matching_products
            
        except Exception as e:
            logger.error(f"❌ Ingredient search error: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        """Get detailed product information"""
        try:
            for category_products in LOREAL_PRODUCTS.values():
                for p in category_products:
                    if p["id"] == product_id:
                        return {
                            **p,
                            "details": {
                                "how_to_use": "Apply morning and evening to clean skin",
                                "benefits_detailed": p.get("benefits", []),
                                "reviews_url": p.get("url"),
                                "where_to_buy": "https://www.loreal-paris.fr"
                            }
                        }
            return None
        except Exception as e:
            logger.error(f"❌ Product details error: {e}")
            return None

