"""
Advanced skill matching algorithms for SkillForge AI
"""

import asyncio
import logging
from typing import List, Dict, Set, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from app.models import MatchingProfile

logger = logging.getLogger(__name__)


class SkillMatcher:
    """Advanced skill matching with multiple algorithms."""

    def __init__(self):
        """Initialize the skill matcher."""
        self.skill_embeddings_cache: Dict[str, np.ndarray] = {}
        self.sentence_model: Optional[SentenceTransformer] = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self._initialized = False

    async def initialize(self):
        """Initialize ML models."""
        if not self._initialized:
            try:
                loop = asyncio.get_event_loop()
                self.sentence_model = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer('all-MiniLM-L6-v2')
                )
                self._initialized = True
                logger.info("SkillMatcher initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SkillMatcher: {e}")

    async def calculate_skill_similarity(
        self,
        user_skills: List[str],
        target_skills: List[str],
        method: str = "hybrid"
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate skill similarity using multiple methods.

        Args:
            user_skills: List of user skills
            target_skills: List of target skills
            method: Similarity method ('jaccard', 'cosine', 'semantic', 'hybrid')

        Returns:
            Tuple of (overall_score, method_scores)
        """

        if not user_skills or not target_skills:
            return 0.0, {}

        method_scores = {}

        if method in ["jaccard", "hybrid"]:
            method_scores["jaccard"] = self._jaccard_similarity(user_skills, target_skills)

        if method in ["cosine", "hybrid"]:
            method_scores["cosine"] = await self._cosine_skill_similarity(user_skills, target_skills)

        if method in ["semantic", "hybrid"]:
            method_scores["semantic"] = await self._semantic_skill_similarity(user_skills, target_skills)

        if method == "hybrid":
            # Weighted combination of methods
            overall_score = (
                method_scores.get("jaccard", 0) * 0.3 +
                method_scores.get("cosine", 0) * 0.35 +
                method_scores.get("semantic", 0) * 0.35
            )
        else:
            overall_score = method_scores.get(method, 0.0)

        return overall_score, method_scores

    def _jaccard_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """Calculate Jaccard similarity between skill sets."""

        set1 = set(skill.lower().strip() for skill in skills1)
        set2 = set(skill.lower().strip() for skill in skills2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    async def _cosine_skill_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """Calculate cosine similarity using TF-IDF vectors."""

        try:
            # Combine skills into documents
            skill_docs = [" ".join(skills1), " ".join(skills2)]

            # Fit and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(skill_docs)

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.error(f"Error in cosine skill similarity: {e}")
            return 0.0

    async def _semantic_skill_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """Calculate semantic similarity using sentence transformers."""

        if not self.sentence_model:
            await self.initialize()
            if not self.sentence_model:
                return 0.0

        try:
            # Create skill descriptions
            skills1_text = ", ".join(skills1)
            skills2_text = ", ".join(skills2)

            # Get embeddings
            embeddings = self.sentence_model.encode([skills1_text, skills2_text])

            # Calculate similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.error(f"Error in semantic skill similarity: {e}")
            return 0.0

    async def find_skill_gaps(
        self,
        user_skills: List[str],
        target_skills: List[str]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Find skill overlaps, gaps, and suggestions.

        Returns:
            Tuple of (overlaps, gaps, suggestions)
        """

        user_set = set(skill.lower().strip() for skill in user_skills)
        target_set = set(skill.lower().strip() for skill in target_skills)

        overlaps = list(user_set & target_set)
        gaps = list(target_set - user_set)

        # Generate skill suggestions based on common patterns
        suggestions = await self._generate_skill_suggestions(user_skills, gaps)

        return overlaps, gaps, suggestions

    async def _generate_skill_suggestions(
        self,
        current_skills: List[str],
        missing_skills: List[str]
    ) -> List[str]:
        """Generate skill learning suggestions."""

        suggestions = []

        # Skill progression patterns
        skill_progressions = {
            "python": ["django", "flask", "fastapi", "pandas", "numpy"],
            "javascript": ["react", "vue", "angular", "node.js", "typescript"],
            "react": ["redux", "next.js", "react native", "jest"],
            "sql": ["postgresql", "mysql", "mongodb", "redis"],
            "machine learning": ["tensorflow", "pytorch", "scikit-learn", "keras"],
            "docker": ["kubernetes", "helm", "jenkins", "gitlab ci"],
        }

        current_lower = [skill.lower() for skill in current_skills]

        for skill in current_lower:
            if skill in skill_progressions:
                for progression in skill_progressions[skill]:
                    if progression not in current_lower and progression not in suggestions:
                        suggestions.append(progression)

        # Add missing skills that are commonly learned together
        for missing in missing_skills[:5]:  # Limit suggestions
            if missing not in suggestions:
                suggestions.append(missing)

        return suggestions[:10]  # Limit to top 10 suggestions

    def calculate_skill_level_compatibility(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> float:
        """Calculate compatibility based on skill levels and experience."""

        experience_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }

        user_level = experience_levels.get(user_profile.experience_level, 2)
        target_level = experience_levels.get(target_profile.experience_level, 2)

        # Different matching strategies based on context
        if user_profile.user_type == "learner" and target_profile.user_type == "company":
            # Learners can grow into roles
            if target_level - user_level <= 1:
                return 1.0
            elif target_level - user_level == 2:
                return 0.7
            else:
                return 0.3

        elif user_profile.user_type == "company" and target_profile.user_type == "learner":
            # Companies prefer exact or higher levels
            if user_level <= target_level:
                return 1.0
            else:
                return 0.5

        else:
            # Peer-to-peer matching prefers similar levels
            level_diff = abs(user_level - target_level)
            return max(0.0, 1.0 - (level_diff * 0.25))

    async def generate_skill_report(
        self,
        user_profile: MatchingProfile,
        target_profile: MatchingProfile
    ) -> Dict[str, any]:
        """Generate comprehensive skill matching report."""

        similarity_score, method_scores = await self.calculate_skill_similarity(
            user_profile.skills,
            target_profile.skills,
            method="hybrid"
        )

        overlaps, gaps, suggestions = await self.find_skill_gaps(
            user_profile.skills,
            target_profile.skills
        )

        level_compatibility = self.calculate_skill_level_compatibility(
            user_profile,
            target_profile
        )

        return {
            "overall_skill_score": similarity_score,
            "method_scores": method_scores,
            "skill_overlaps": overlaps,
            "skill_gaps": gaps,
            "skill_suggestions": suggestions,
            "level_compatibility": level_compatibility,
            "skill_analysis": {
                "user_skill_count": len(user_profile.skills),
                "target_skill_count": len(target_profile.skills),
                "overlap_percentage": len(overlaps) / len(target_profile.skills) * 100 if target_profile.skills else 0,
                "gap_count": len(gaps),
                "experience_gap": abs(
                    {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}.get(user_profile.experience_level, 2) -
                    {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}.get(target_profile.experience_level, 2)
                )
            }
        }