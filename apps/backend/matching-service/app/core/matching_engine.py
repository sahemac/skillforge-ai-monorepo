"""
Core matching engine for SkillForge AI Matching Service
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from app.models import (
    MatchingProfile,
    MatchResult,
    MatchResultCreate,
    MatchingType,
    MatchingStatus
)
from app.core.cache import cache_service

logger = logging.getLogger(__name__)


@dataclass
class MatchingConfig:
    """Configuration for matching algorithms."""

    skill_weight: float = 0.3
    experience_weight: float = 0.2
    location_weight: float = 0.15
    preference_weight: float = 0.15
    semantic_weight: float = 0.2

    min_score_threshold: float = 0.1
    max_results: int = 50
    use_cache: bool = True
    cache_ttl: int = 3600  # 1 hour


class MatchingEngine:
    """Advanced matching engine with multiple algorithms."""

    def __init__(self, config: MatchingConfig = None):
        """Initialize the matching engine."""
        self.config = config or MatchingConfig()
        self.sentence_model = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self._model_loaded = False

    async def initialize(self):
        """Initialize ML models asynchronously."""
        if not self._model_loaded:
            try:
                # Load sentence transformer in a separate thread to avoid blocking
                loop = asyncio.get_event_loop()
                self.sentence_model = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer('all-MiniLM-L6-v2')
                )
                self._model_loaded = True
                logger.info("Matching engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize sentence transformer: {e}")
                self.sentence_model = None

    async def find_matches(
        self,
        user_profile: MatchingProfile,
        target_profiles: List[MatchingProfile],
        matching_type: str = MatchingType.USER_TO_PROJECT,
        max_results: Optional[int] = None
    ) -> List[MatchResultCreate]:
        """Find matches for a user against target profiles."""

        if not target_profiles:
            return []

        max_results = max_results or self.config.max_results
        start_time = time.time()

        # Check cache first
        cache_key = self._generate_cache_key(user_profile.id, target_profiles, matching_type)
        if self.config.use_cache:
            cached_results = await cache_service.get(cache_key)
            if cached_results:
                logger.info(f"Retrieved {len(cached_results)} matches from cache")
                return cached_results

        matches = []

        for target_profile in target_profiles:
            try:
                match_result = await self._calculate_match(
                    user_profile,
                    target_profile,
                    matching_type
                )

                if match_result and match_result.overall_score >= self.config.min_score_threshold:
                    matches.append(match_result)

            except Exception as e:
                logger.error(f"Error calculating match for target {target_profile.id}: {e}")
                continue

        # Sort by overall score descending
        matches.sort(key=lambda x: x.overall_score, reverse=True)

        # Limit results
        matches = matches[:max_results]

        # Add ranking position
        for i, match in enumerate(matches):
            match.rank_position = i + 1
            match.computation_time_ms = (time.time() - start_time) * 1000

        # Cache results
        if self.config.use_cache and matches:
            await cache_service.set(cache_key, matches, self.config.cache_ttl)

        logger.info(f"Found {len(matches)} matches in {time.time() - start_time:.2f}s")
        return matches

    async def _calculate_match(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile,
        matching_type: str
    ) -> Optional[MatchResultCreate]:
        """Calculate detailed match score between two profiles."""

        try:
            # Calculate individual scores
            skill_score = await self._calculate_skill_score(user_profile, target_profile)
            experience_score = self._calculate_experience_score(user_profile, target_profile)
            location_score = self._calculate_location_score(user_profile, target_profile)
            preference_score = self._calculate_preference_score(user_profile, target_profile)
            semantic_score = await self._calculate_semantic_score(user_profile, target_profile)

            # Calculate weighted overall score
            overall_score = (
                skill_score * self.config.skill_weight +
                experience_score * self.config.experience_weight +
                location_score * self.config.location_weight +
                preference_score * self.config.preference_weight +
                semantic_score * self.config.semantic_weight
            )

            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(user_profile, target_profile)

            # Generate match reasons
            match_reasons = self._generate_match_reasons(
                user_profile, target_profile, skill_score, experience_score,
                location_score, preference_score, semantic_score
            )

            # Find skill overlaps and gaps
            skill_overlaps, missing_skills = self._analyze_skills(user_profile, target_profile)

            return MatchResultCreate(
                user_id=user_profile.user_id,
                target_id=target_profile.user_id,
                target_type=target_profile.user_type,
                matching_type=matching_type,
                overall_score=min(1.0, max(0.0, overall_score)),
                skill_score=skill_score,
                experience_score=experience_score,
                location_score=location_score,
                preference_score=preference_score,
                semantic_score=semantic_score,
                confidence_level=confidence,
                match_reasons=match_reasons,
                skill_overlaps=skill_overlaps,
                missing_skills=missing_skills,
                match_metadata={
                    "algorithm_version": "1.0.0",
                    "weights": {
                        "skill": self.config.skill_weight,
                        "experience": self.config.experience_weight,
                        "location": self.config.location_weight,
                        "preference": self.config.preference_weight,
                        "semantic": self.config.semantic_weight
                    }
                }
            )

        except Exception as e:
            logger.error(f"Error calculating match: {e}")
            return None

    async def _calculate_skill_score(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate skill compatibility score using cosine similarity."""

        user_skills = set(skill.lower() for skill in user_profile.skills)
        target_skills = set(skill.lower() for skill in target_profile.skills)

        if not user_skills or not target_skills:
            return 0.0

        # If we have embeddings, use them
        if (user_profile.skills_embedding and target_profile.skills_embedding and
            len(user_profile.skills_embedding) == len(target_profile.skills_embedding)):

            user_embedding = np.array(user_profile.skills_embedding).reshape(1, -1)
            target_embedding = np.array(target_profile.skills_embedding).reshape(1, -1)

            similarity = cosine_similarity(user_embedding, target_embedding)[0][0]
            return max(0.0, min(1.0, similarity))

        # Fallback to Jaccard similarity
        intersection = len(user_skills & target_skills)
        union = len(user_skills | target_skills)

        return intersection / union if union > 0 else 0.0

    def _calculate_experience_score(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate experience level compatibility score."""

        experience_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }

        user_level = experience_levels.get(user_profile.experience_level, 2)
        target_level = experience_levels.get(target_profile.experience_level, 2)

        # Calculate compatibility (closer levels = higher score)
        level_diff = abs(user_level - target_level)
        max_diff = max(experience_levels.values()) - min(experience_levels.values())

        return 1.0 - (level_diff / max_diff) if max_diff > 0 else 1.0

    def _calculate_location_score(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate location compatibility score."""

        # If both prefer remote work, perfect match
        if (user_profile.preferred_work_mode == "remote" and
            target_profile.preferred_work_mode == "remote"):
            return 1.0

        # If one prefers remote and other is flexible, good match
        if ("remote" in [user_profile.preferred_work_mode, target_profile.preferred_work_mode] and
            "hybrid" in [user_profile.preferred_work_mode, target_profile.preferred_work_mode]):
            return 0.8

        # Simple location matching (in real implementation, use geospatial calculations)
        if (user_profile.preferred_location and target_profile.preferred_location):
            if user_profile.preferred_location.lower() == target_profile.preferred_location.lower():
                return 1.0
            else:
                return 0.3  # Different locations but might be acceptable

        return 0.5  # Neutral if location info is missing

    def _calculate_preference_score(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate preference compatibility score."""

        score = 0.0
        factors = 0

        # Work mode preference
        if user_profile.preferred_work_mode and target_profile.preferred_work_mode:
            work_modes = [user_profile.preferred_work_mode, target_profile.preferred_work_mode]
            if "remote" in work_modes and len(set(work_modes)) <= 2:
                score += 1.0 if work_modes[0] == work_modes[1] else 0.7
            else:
                score += 1.0 if work_modes[0] == work_modes[1] else 0.3
            factors += 1

        # Salary expectations (simplified)
        if (user_profile.salary_expectations and target_profile.salary_expectations):
            # In a real implementation, this would compare salary ranges
            score += 0.7  # Placeholder
            factors += 1

        return score / factors if factors > 0 else 0.5

    async def _calculate_semantic_score(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate semantic similarity using sentence transformers."""

        if not self.sentence_model:
            await self.initialize()
            if not self.sentence_model:
                return 0.0

        try:
            # Combine profile text data
            user_text = self._extract_profile_text(user_profile)
            target_text = self._extract_profile_text(target_profile)

            if not user_text or not target_text:
                return 0.0

            # Get embeddings
            embeddings = self.sentence_model.encode([user_text, target_text])

            # Calculate cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.error(f"Error calculating semantic score: {e}")
            return 0.0

    def _extract_profile_text(self, profile: MatchingProfile) -> str:
        """Extract text data from profile for semantic analysis."""

        text_parts = []

        # Add skills
        text_parts.extend(profile.skills)

        # Add interests
        text_parts.extend(profile.interests)

        # Add profile data text fields
        if profile.profile_data:
            for key, value in profile.profile_data.items():
                if isinstance(value, str) and len(value) > 10:
                    text_parts.append(value)

        return " ".join(text_parts)

    def _calculate_confidence(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate confidence in the match based on data completeness."""

        user_completeness = user_profile.profile_completeness_score
        target_completeness = target_profile.profile_completeness_score

        # Average completeness affects confidence
        avg_completeness = (user_completeness + target_completeness) / 2

        # Additional factors
        has_skills = bool(user_profile.skills and target_profile.skills)
        has_experience = bool(user_profile.experience_level and target_profile.experience_level)
        has_location = bool(user_profile.preferred_location and target_profile.preferred_location)

        bonus_factors = sum([has_skills, has_experience, has_location]) / 3

        return min(1.0, avg_completeness * 0.7 + bonus_factors * 0.3)

    def _generate_match_reasons(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile,
        skill_score: float,
        experience_score: float,
        location_score: float,
        preference_score: float,
        semantic_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the match."""

        reasons = []

        if skill_score > 0.7:
            reasons.append("Strong skill compatibility")
        elif skill_score > 0.4:
            reasons.append("Good skill overlap")

        if experience_score > 0.8:
            reasons.append("Perfect experience level match")
        elif experience_score > 0.6:
            reasons.append("Compatible experience levels")

        if location_score > 0.8:
            reasons.append("Excellent location match")
        elif location_score > 0.6:
            reasons.append("Good location compatibility")

        if preference_score > 0.7:
            reasons.append("Aligned work preferences")

        if semantic_score > 0.6:
            reasons.append("Similar interests and goals")

        # Add specific skill overlaps
        skill_overlaps, _ = self._analyze_skills(user_profile, target_profile)
        if len(skill_overlaps) > 2:
            reasons.append(f"Shared expertise in {', '.join(skill_overlaps[:3])}")

        return reasons if reasons else ["Basic compatibility match"]

    def _analyze_skills(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> Tuple[List[str], List[str]]:
        """Analyze skill overlaps and gaps."""

        user_skills = set(skill.lower() for skill in user_profile.skills)
        target_skills = set(skill.lower() for skill in target_profile.skills)

        overlaps = list(user_skills & target_skills)
        missing = list(target_skills - user_skills)

        return overlaps[:10], missing[:10]  # Limit to prevent huge lists

    def _generate_cache_key(
        self,
        user_id: str,
        target_profiles: List[MatchingProfile],
        matching_type: str
    ) -> str:
        """Generate cache key for matching results."""

        target_ids = sorted([p.id for p in target_profiles])
        return f"match:{user_id}:{matching_type}:{hash(tuple(target_ids))}"


# Global matching engine instance
matching_engine = MatchingEngine()