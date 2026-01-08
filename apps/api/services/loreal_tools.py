"""
L'Oréal Tools Service - Virtual try-on, product matching, etc.
"""

import logging
from typing import List, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# L'Oréal Product Database (mock)
LOREAL_PRODUCTS = {
    "peau_grasse": [
        {"id": 1, "name": "Pure Zone Gel Purifiant", "category": "Cleansing", "price": "18.99 EUR", "benefits": ["Oil control", "Lightweight", "Purifying"]},
        {"id": 2, "name": "Pure Zone Mattifying Toner", "category": "Toner", "price": "15.99 EUR", "benefits": ["Mattifying", "Pore minimizing"]},
        {"id": 3, "name": "Effaclar Duo+", "category": "Moisturizer", "price": "22.99 EUR", "benefits": ["Oil-free", "Anti-blemish", "Fast-absorbing"]},
    ],
    "peau_seche": [
        {"id": 4, "name": "Hydra Genius Daily Moisturizer", "category": "Moisturizer", "price": "24.99 EUR", "benefits": ["Hydrating", "Lightweight", "SPF 25"]},
        {"id": 5, "name": "Revitalift Classic Cream", "category": "Anti-age", "price": "29.99 EUR", "benefits": ["Firming", "Anti-wrinkle", "Nourishing"]},
    ],
    "sensible": [
        {"id": 6, "name": "Toleriane Purifying Foaming Cleanser", "category": "Cleansing", "price": "14.99 EUR", "benefits": ["Gentle", "Hypoallergenic", "Soap-free"]},
        {"id": 7, "name": "La Roche Posay Toleriane Moisturizer", "category": "Moisturizer", "price": "19.99 EUR", "benefits": ["Gentle", "Soothing", "Dermatologist-tested"]},
    ],
}

class VirtualTryOnRequest(BaseModel):
    product_id: int
    skin_concern: str
    current_routine: Optional[List[str]] = None

class ProductMatch(BaseModel):
    product_id: int
    name: str
    category: str
    price: str
    benefits: List[str]
    match_score: float  # 0-1

class LoreaToolService:
    """L'Oréal virtual tools and recommendations"""
    
    def __init__(self):
        self.products = LOREAL_PRODUCTS
    
    async def recommend_products(self, skin_concern: str, skin_type: Optional[str] = None) -> List[Dict]:
        """Recommend products based on skin concern"""
        try:
            # Normalize concern
            concern_map = {
                "gras": "peau_grasse",
                "grasse": "peau_grasse",
                "grasse": "peau_grasse",
                "oily": "peau_grasse",
                "sec": "peau_seche",
                "seche": "peau_seche",
                "dry": "peau_seche",
                "sensible": "sensible",
                "sensitive": "sensible",
            }
            
            key = concern_map.get(skin_concern.lower(), "peau_grasse")
            products = self.products.get(key, [])
            
            logger.info(f"✅ Recommended {len(products)} products for: {skin_concern}")
            return products
        except Exception as e:
            logger.error(f"❌ Product recommendation error: {e}")
            return []
    
    async def virtual_try_on(self, product_id: int, user_profile: Dict) -> Dict:
        """Simulate trying on a product virtually"""
        try:
            # Find product
            product = None
            for category_products in self.products.values():
                for p in category_products:
                    if p["id"] == product_id:
                        product = p
                        break
            
            if not product:
                return {"success": False, "message": "Product not found"}
            
            # Simulate virtual try-on results
            simulation = {
                "product": product,
                "simulation_results": {
                    "texture_feel": "light, non-greasy",
                    "skin_improvement": "mattifying, pores appear smaller",
                    "compatibility": "excellent for oily skin",
                    "estimated_improvement_days": 7,
                },
                "success": True
            }
            
            logger.info(f"✅ Virtual try-on completed for product: {product['name']}")
            return simulation
        except Exception as e:
            logger.error(f"❌ Virtual try-on error: {e}")
            return {"success": False, "message": str(e)}
    
    async def create_routine(self, skin_type: str, concerns: List[str]) -> Dict:
        """Create a personalized routine"""
        try:
            routine = {
                "morning": await self.recommend_products(concerns[0], skin_type) if concerns else [],
                "evening": await self.recommend_products(concerns[0], skin_type) if concerns else [],
                "weekly_treatment": await self.recommend_products("sensible", skin_type) if skin_type == "sensible" else [],
            }
            
            logger.info(f"✅ Created routine for skin type: {skin_type}")
            return routine
        except Exception as e:
            logger.error(f"❌ Routine creation error: {e}")
            return {}
    
    async def match_product_to_routine(self, new_product_id: int, current_products: List[str]) -> ProductMatch:
        """Check if product matches existing routine"""
        try:
            # Find product
            product = None
            for category_products in self.products.values():
                for p in category_products:
                    if p["id"] == new_product_id:
                        product = p
                        break
            
            if not product:
                return {"success": False}
            
            # Calculate match score based on category
            match_score = 0.8  # Default
            if any("cleansing" in p.lower() for p in current_products) and product["category"] == "Cleansing":
                match_score = 0.6  # Overlap
            elif product["category"] in ["Moisturizer", "Toner"]:
                match_score = 0.95  # Good addition
            
            return ProductMatch(
                product_id=product["id"],
                name=product["name"],
                category=product["category"],
                price=product["price"],
                benefits=product["benefits"],
                match_score=match_score
            )
        except Exception as e:
            logger.error(f"❌ Product matching error: {e}")
            return {}
