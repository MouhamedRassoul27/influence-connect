"""
Influencer Detection and Ambassador Scoring Service
"""

import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class InfluencerProfile(BaseModel):
    user_id: str
    username: str
    followers_count: int
    engagement_rate: float  # 0-1
    content_categories: List[str]
    avg_likes_per_post: int
    avg_comments_per_post: int
    last_active: datetime
    ambassador_score: float  # 0-100

class AmbassadorProposal(BaseModel):
    influencer_id: str
    username: str
    proposal_reason: str
    benefits_summary: str
    commission_offer: str
    acceptance_probability: float  # 0-1

class InfluencerScoringService:
    """Score users and propose ambassador programs"""
    
    # Thresholds for ambassador program
    MIN_FOLLOWERS = 1000
    MIN_ENGAGEMENT_RATE = 0.03  # 3%
    MIN_AMBASSADOR_SCORE = 60
    
    async def analyze_user_profile(self, user_id: str, user_data: Dict) -> InfluencerProfile:
        """Analyze user data to create influencer profile"""
        try:
            followers = user_data.get("followers_count", 0)
            engagement_rate = user_data.get("engagement_rate", 0)
            content_categories = user_data.get("content_categories", [])
            likes = user_data.get("avg_likes_per_post", 0)
            comments = user_data.get("avg_comments_per_post", 0)
            
            # Calculate ambassador score
            score = self._calculate_ambassador_score(
                followers=followers,
                engagement_rate=engagement_rate,
                likes=likes,
                comments=comments,
                categories=content_categories
            )
            
            profile = InfluencerProfile(
                user_id=user_id,
                username=user_data.get("username", "unknown"),
                followers_count=followers,
                engagement_rate=engagement_rate,
                content_categories=content_categories,
                avg_likes_per_post=likes,
                avg_comments_per_post=comments,
                last_active=datetime.now(),
                ambassador_score=score
            )
            
            logger.info(f"✅ Analyzed influencer {user_data.get('username')}: score={score:.1f}")
            return profile
        except Exception as e:
            logger.error(f"❌ Profile analysis error: {e}")
            raise
    
    def _calculate_ambassador_score(
        self,
        followers: int,
        engagement_rate: float,
        likes: int,
        comments: int,
        categories: List[str]
    ) -> float:
        """Calculate ambassador score (0-100)"""
        score = 0
        
        # Followers (max 40 points)
        if followers > 100000:
            score += 40
        elif followers > 50000:
            score += 35
        elif followers > 10000:
            score += 25
        elif followers > 5000:
            score += 15
        elif followers > 1000:
            score += 10
        
        # Engagement rate (max 30 points)
        if engagement_rate > 0.08:
            score += 30
        elif engagement_rate > 0.05:
            score += 25
        elif engagement_rate > 0.03:
            score += 20
        elif engagement_rate > 0.02:
            score += 10
        
        # Comments (high engagement = good) (max 15 points)
        if comments > 100:
            score += 15
        elif comments > 50:
            score += 10
        elif comments > 20:
            score += 5
        
        # Beauty/Wellness related categories (max 15 points)
        beauty_keywords = ["beauty", "skincare", "makeup", "wellness", "lifestyle", "fashion"]
        beauty_matches = sum(1 for cat in categories if any(kw in cat.lower() for kw in beauty_keywords))
        if beauty_matches > 0:
            score += min(15, beauty_matches * 5)
        
        return min(100, score)
    
    async def propose_ambassador(
        self,
        profile: InfluencerProfile,
        existing_ambassadors: List[str] = None
    ) -> Optional[AmbassadorProposal]:
        """Propose ambassador program if criteria met"""
        try:
            if existing_ambassadors and profile.user_id in existing_ambassadors:
                logger.info(f"⚠️  User already an ambassador: {profile.username}")
                return None
            
            # Check if meets minimum criteria
            if profile.followers_count < self.MIN_FOLLOWERS:
                logger.info(f"⚠️  Insufficient followers: {profile.followers_count}")
                return None
            
            if profile.engagement_rate < self.MIN_ENGAGEMENT_RATE:
                logger.info(f"⚠️  Low engagement: {profile.engagement_rate}")
                return None
            
            if profile.ambassador_score < self.MIN_AMBASSADOR_SCORE:
                logger.info(f"⚠️  Low ambassador score: {profile.ambassador_score}")
                return None
            
            # Generate proposal
            acceptance_prob = self._estimate_acceptance(profile)
            
            proposal = AmbassadorProposal(
                influencer_id=profile.user_id,
                username=profile.username,
                proposal_reason=self._generate_reason(profile),
                benefits_summary=self._generate_benefits(profile),
                commission_offer=self._generate_commission_offer(profile),
                acceptance_probability=acceptance_prob
            )
            
            logger.info(f"✅ Generated ambassador proposal for: {profile.username}")
            return proposal
        except Exception as e:
            logger.error(f"❌ Proposal generation error: {e}")
            return None
    
    def _estimate_acceptance(self, profile: InfluencerProfile) -> float:
        """Estimate probability of accepting ambassador offer"""
        # Factors that increase acceptance
        acceptance = 0.5  # Base probability
        
        if profile.ambassador_score > 80:
            acceptance += 0.2
        
        if "beauty" in " ".join(profile.content_categories).lower():
            acceptance += 0.15
        
        if profile.engagement_rate > 0.05:
            acceptance += 0.1
        
        return min(0.95, max(0.3, acceptance))
    
    def _generate_reason(self, profile: InfluencerProfile) -> str:
        """Generate reason for ambassador proposal"""
        reasons = []
        
        if profile.followers_count > 10000:
            reasons.append(f"Strong audience of {profile.followers_count:,} followers")
        
        if profile.engagement_rate > 0.05:
            reasons.append(f"Excellent engagement rate ({profile.engagement_rate*100:.1f}%)")
        
        if "beauty" in " ".join(profile.content_categories).lower():
            reasons.append("Active in beauty & skincare content")
        
        return "; ".join(reasons) if reasons else "Strong community influence"
    
    def _generate_benefits(self, profile: InfluencerProfile) -> str:
        """Generate benefits summary"""
        benefits = [
            "Exclusive access to new L'Oréal products",
            "Monthly ambassador stipend",
            "Free product shipments",
            "Co-creation opportunities",
            "Exclusive events & workshops"
        ]
        
        if profile.followers_count > 50000:
            benefits.append("Premium partnership tier")
        
        return ", ".join(benefits[:4])
    
    def _generate_commission_offer(self, profile: InfluencerProfile) -> str:
        """Generate commission offer based on profile"""
        # Commission tiers based on followers and engagement
        if profile.followers_count > 100000:
            tier = "GOLD: 15% commission + monthly stipend"
        elif profile.followers_count > 50000:
            tier = "SILVER: 12% commission + monthly stipend"
        elif profile.followers_count > 10000:
            tier = "BRONZE: 10% commission + product benefits"
        else:
            tier = "STARTER: 8% commission + product benefits"
        
        return tier
    
    async def batch_analyze_users(self, users: List[Dict]) -> List[AmbassadorProposal]:
        """Analyze batch of users and generate proposals"""
        proposals = []
        
        for user in users:
            try:
                profile = await self.analyze_user_profile(user.get("id"), user)
                proposal = await self.propose_ambassador(profile)
                if proposal:
                    proposals.append(proposal)
            except Exception as e:
                logger.warning(f"⚠️  Skipped user {user.get('username')}: {e}")
        
        logger.info(f"✅ Generated {len(proposals)} ambassador proposals")
        return proposals
