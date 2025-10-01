"""
AI Recommendations endpoints for SkillForge AI Matching Service
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_session
from app.core.matching_engine import matching_engine
from app.core.algorithms.skill_matcher import SkillMatcher
from app.models import (
    MatchingProfile,
    MatchResult,
    MatchResultResponse,
    UserPreference
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Initialize skill matcher
skill_matcher = SkillMatcher()


@router.get("/for-user/{user_id}", response_model=List[MatchResultResponse])
@limiter.limit("20/minute")
async def get_personalized_recommendations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    recommendation_type: str = Query(default="all", regex="^(all|projects|users|skills|opportunities)$"),
    session: Session = Depends(get_session)
):
    """
    Get personalized AI recommendations for a user.

    Uses machine learning algorithms to suggest:
    - Best matching projects/opportunities
    - Compatible users for collaboration
    - Skill development suggestions
    - Career advancement opportunities
    """

    try:
        # Get user profile
        user_profile = session.exec(
            select(MatchingProfile).where(
                MatchingProfile.user_id == user_id,
                MatchingProfile.is_active == True
            )
        ).first()

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found or inactive"
            )

        # Get user preferences for personalization
        user_preferences = session.exec(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.is_active == True
            )
        ).all()

        recommendations = []

        if recommendation_type in ["all", "projects"]:
            project_recs = await _get_project_recommendations(
                user_profile, user_preferences, session, limit
            )
            recommendations.extend(project_recs)

        if recommendation_type in ["all", "users"]:
            user_recs = await _get_user_recommendations(
                user_profile, user_preferences, session, limit
            )
            recommendations.extend(user_recs)

        # Sort by overall score and limit results
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        return recommendations[:limit]

    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/skill-development/{user_id}")
@limiter.limit("20/minute")
async def get_skill_development_recommendations(
    user_id: str,
    focus_area: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get AI-powered skill development recommendations."""

    try:
        user_profile = session.exec(
            select(MatchingProfile).where(MatchingProfile.user_id == user_id)
        ).first()

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Initialize skill matcher if needed
        if not skill_matcher._initialized:
            await skill_matcher.initialize()

        # Get high-demand skills from successful matches
        successful_matches = session.exec(
            select(MatchResult).where(
                MatchResult.user_id == user_id,
                MatchResult.overall_score >= 0.7,
                MatchResult.is_active == True
            ).limit(20)
        ).all()

        # Analyze skill gaps across successful matches
        all_missing_skills = []
        skill_frequency = {}

        for match in successful_matches:
            for skill in match.missing_skills:
                all_missing_skills.append(skill)
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

        # Get top missing skills
        top_missing_skills = sorted(
            skill_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Generate skill development path
        current_skills = [skill.lower() for skill in user_profile.skills]

        # Use skill matcher to generate suggestions
        skill_suggestions = await skill_matcher._generate_skill_suggestions(
            user_profile.skills,
            [skill for skill, _ in top_missing_skills]
        )

        # Create learning path with priorities
        learning_path = []
        for i, skill in enumerate(skill_suggestions):
            priority = "high" if i < 3 else "medium" if i < 6 else "low"
            difficulty = _estimate_skill_difficulty(skill, current_skills)
            estimated_time = _estimate_learning_time(skill, user_profile.experience_level)

            learning_path.append({
                "skill": skill,
                "priority": priority,
                "difficulty": difficulty,
                "estimated_learning_time_weeks": estimated_time,
                "frequency_in_matches": skill_frequency.get(skill, 0),
                "related_skills": _get_related_skills(skill),
                "resources": _get_learning_resources(skill)
            })

        # Career advancement suggestions
        career_suggestions = await _generate_career_suggestions(user_profile)

        return {
            "user_id": user_id,
            "current_skills": user_profile.skills,
            "experience_level": user_profile.experience_level,
            "skill_development_path": learning_path,
            "career_advancement_suggestions": career_suggestions,
            "market_demand_insights": {
                "top_demanded_skills": [skill for skill, freq in top_missing_skills[:5]],
                "skill_gap_analysis": {
                    "total_gaps_identified": len(set(all_missing_skills)),
                    "most_common_gap": top_missing_skills[0][0] if top_missing_skills else None,
                    "gap_frequency": dict(top_missing_skills[:5])
                }
            },
            "personalized_recommendations": {
                "quick_wins": [item for item in learning_path if item["difficulty"] == "easy"][:3],
                "strategic_investments": [item for item in learning_path if item["priority"] == "high"],
                "long_term_goals": [item for item in learning_path if item["difficulty"] == "hard"][:2]
            }
        }

    except Exception as e:
        logger.error(f"Error getting skill recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting skill recommendations: {str(e)}"
        )


@router.get("/trending")
@limiter.limit("30/minute")
async def get_trending_opportunities(
    category: str = Query(default="all", regex="^(all|skills|projects|locations|roles)$"),
    time_range: str = Query(default="week", regex="^(day|week|month|quarter)$"),
    session: Session = Depends(get_session)
):
    """Get trending opportunities and market insights."""

    try:
        # Analyze recent matching patterns
        recent_matches = session.exec(
            select(MatchResult).where(
                MatchResult.is_active == True,
                MatchResult.overall_score >= 0.5
            ).limit(1000)
        ).all()

        if not recent_matches:
            return {"message": "Insufficient data for trending analysis"}

        trending_data = {}

        if category in ["all", "skills"]:
            # Analyze skill trends
            skill_mentions = {}
            for match in recent_matches:
                for skill in match.skill_overlaps:
                    skill_mentions[skill] = skill_mentions.get(skill, 0) + 1

            trending_skills = sorted(
                skill_mentions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]

            trending_data["skills"] = [
                {
                    "skill": skill,
                    "mention_count": count,
                    "growth_indicator": "high" if count > 50 else "medium" if count > 20 else "low"
                }
                for skill, count in trending_skills
            ]

        if category in ["all", "locations"]:
            # Analyze location trends (simplified)
            location_data = {}
            for match in recent_matches:
                # This would be more sophisticated with actual location data
                location_data["remote"] = location_data.get("remote", 0) + 1

            trending_data["locations"] = [
                {"location": "Remote Work", "popularity": location_data.get("remote", 0)}
            ]

        # Market insights
        market_insights = {
            "total_active_matches": len(recent_matches),
            "average_match_score": sum(m.overall_score for m in recent_matches) / len(recent_matches),
            "match_success_rate": len([m for m in recent_matches if m.overall_score >= 0.7]) / len(recent_matches),
            "most_competitive_skills": trending_data.get("skills", [])[:5],
            "emerging_opportunities": _identify_emerging_opportunities(recent_matches)
        }

        return {
            "category": category,
            "time_range": time_range,
            "trending_data": trending_data,
            "market_insights": market_insights,
            "recommendations": {
                "for_learners": _generate_learner_market_recommendations(trending_data),
                "for_companies": _generate_company_market_recommendations(trending_data)
            }
        }

    except Exception as e:
        logger.error(f"Error getting trending opportunities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting trending opportunities: {str(e)}"
        )


@router.get("/similar-users/{user_id}")
@limiter.limit("20/minute")
async def get_similar_users(
    user_id: str,
    similarity_threshold: float = Query(default=0.6, ge=0.0, le=1.0),
    limit: int = Query(default=10, ge=1, le=50),
    session: Session = Depends(get_session)
):
    """Find users with similar profiles for networking and collaboration."""

    try:
        user_profile = session.exec(
            select(MatchingProfile).where(MatchingProfile.user_id == user_id)
        ).first()

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Get all other active profiles
        other_profiles = session.exec(
            select(MatchingProfile).where(
                MatchingProfile.user_id != user_id,
                MatchingProfile.is_active == True
            )
        ).all()

        if not other_profiles:
            return []

        # Initialize matching engine
        if not matching_engine._model_loaded:
            await matching_engine.initialize()

        # Calculate similarities
        similar_users = []

        for profile in other_profiles:
            try:
                # Calculate skill similarity
                if not skill_matcher._initialized:
                    await skill_matcher.initialize()

                skill_similarity, _ = await skill_matcher.calculate_skill_similarity(
                    user_profile.skills,
                    profile.skills,
                    method="hybrid"
                )

                if skill_similarity >= similarity_threshold:
                    # Calculate additional similarities
                    experience_similarity = matching_engine._calculate_experience_score(
                        user_profile, profile
                    )

                    overall_similarity = (skill_similarity * 0.6 + experience_similarity * 0.4)

                    similar_users.append({
                        "user_id": profile.user_id,
                        "user_type": profile.user_type,
                        "similarity_score": overall_similarity,
                        "skill_similarity": skill_similarity,
                        "experience_similarity": experience_similarity,
                        "common_skills": list(
                            set(s.lower() for s in user_profile.skills) &
                            set(s.lower() for s in profile.skills)
                        ),
                        "complementary_skills": list(
                            set(s.lower() for s in profile.skills) -
                            set(s.lower() for s in user_profile.skills)
                        )[:5],
                        "profile_completeness": profile.profile_completeness_score,
                        "last_activity": profile.last_activity
                    })

            except Exception as e:
                logger.warning(f"Error calculating similarity with user {profile.user_id}: {e}")
                continue

        # Sort by similarity and limit
        similar_users.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_users[:limit]

    except Exception as e:
        logger.error(f"Error finding similar users for {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar users: {str(e)}"
        )


# Helper functions

async def _get_project_recommendations(
    user_profile: MatchingProfile,
    user_preferences: List[UserPreference],
    session: Session,
    limit: int
) -> List[MatchResultResponse]:
    """Get project recommendations for user."""

    # Get project profiles (companies offering projects)
    project_profiles = session.exec(
        select(MatchingProfile).where(
            MatchingProfile.user_type == "company",
            MatchingProfile.is_active == True
        ).limit(100)
    ).all()

    if not project_profiles:
        return []

    # Find matches
    matches = await matching_engine.find_matches(
        user_profile=user_profile,
        target_profiles=project_profiles,
        matching_type="user_to_project",
        max_results=limit
    )

    return [
        MatchResultResponse(
            id=f"{match.user_id}_{match.target_id}",
            user_id=match.user_id,
            target_id=match.target_id,
            target_type=match.target_type,
            matching_type=match.matching_type,
            overall_score=match.overall_score,
            skill_score=match.skill_score,
            experience_score=match.experience_score,
            location_score=match.location_score,
            preference_score=match.preference_score,
            semantic_score=match.semantic_score,
            rank_position=match.rank_position,
            confidence_level=match.confidence_level,
            match_reasons=match.match_reasons,
            skill_overlaps=match.skill_overlaps,
            missing_skills=match.missing_skills,
            computation_time_ms=match.computation_time_ms,
            is_mutual=False,
            user_feedback=None,
            feedback_score=None,
            is_active=True,
            created_at="",
            updated_at=None
        )
        for match in matches
    ]


async def _get_user_recommendations(
    user_profile: MatchingProfile,
    user_preferences: List[UserPreference],
    session: Session,
    limit: int
) -> List[MatchResultResponse]:
    """Get user collaboration recommendations."""

    # Get other user profiles
    other_profiles = session.exec(
        select(MatchingProfile).where(
            MatchingProfile.user_id != user_profile.user_id,
            MatchingProfile.is_active == True
        ).limit(100)
    ).all()

    if not other_profiles:
        return []

    matches = await matching_engine.find_matches(
        user_profile=user_profile,
        target_profiles=other_profiles,
        matching_type="user_to_user",
        max_results=limit
    )

    return [
        MatchResultResponse(
            id=f"{match.user_id}_{match.target_id}",
            user_id=match.user_id,
            target_id=match.target_id,
            target_type=match.target_type,
            matching_type=match.matching_type,
            overall_score=match.overall_score,
            skill_score=match.skill_score,
            experience_score=match.experience_score,
            location_score=match.location_score,
            preference_score=match.preference_score,
            semantic_score=match.semantic_score,
            rank_position=match.rank_position,
            confidence_level=match.confidence_level,
            match_reasons=match.match_reasons,
            skill_overlaps=match.skill_overlaps,
            missing_skills=match.missing_skills,
            computation_time_ms=match.computation_time_ms,
            is_mutual=False,
            user_feedback=None,
            feedback_score=None,
            is_active=True,
            created_at="",
            updated_at=None
        )
        for match in matches
    ]


def _estimate_skill_difficulty(skill: str, current_skills: List[str]) -> str:
    """Estimate difficulty of learning a skill based on current skills."""

    skill_lower = skill.lower()
    current_lower = [s.lower() for s in current_skills]

    # Skill difficulty mapping (simplified)
    easy_skills = ["html", "css", "git", "agile", "scrum"]
    hard_skills = ["machine learning", "kubernetes", "blockchain", "ai", "deep learning"]

    if skill_lower in easy_skills:
        return "easy"
    elif skill_lower in hard_skills:
        return "hard"
    else:
        return "medium"


def _estimate_learning_time(skill: str, experience_level: str) -> int:
    """Estimate learning time in weeks."""

    base_times = {
        "beginner": 12,
        "intermediate": 8,
        "advanced": 4,
        "expert": 2
    }

    skill_multipliers = {
        "html": 0.5,
        "css": 0.7,
        "javascript": 1.2,
        "python": 1.0,
        "machine learning": 2.0,
        "kubernetes": 1.8
    }

    base_time = base_times.get(experience_level, 8)
    multiplier = skill_multipliers.get(skill.lower(), 1.0)

    return int(base_time * multiplier)


def _get_related_skills(skill: str) -> List[str]:
    """Get skills related to the given skill."""

    skill_relations = {
        "python": ["django", "flask", "pandas", "numpy"],
        "javascript": ["react", "vue", "node.js", "typescript"],
        "react": ["redux", "jsx", "javascript", "html"],
        "machine learning": ["python", "tensorflow", "scikit-learn", "pandas"]
    }

    return skill_relations.get(skill.lower(), [])


def _get_learning_resources(skill: str) -> List[Dict[str, str]]:
    """Get learning resources for a skill."""

    return [
        {"type": "course", "name": f"Complete {skill} Course", "url": "#"},
        {"type": "documentation", "name": f"Official {skill} Docs", "url": "#"},
        {"type": "practice", "name": f"{skill} Practice Projects", "url": "#"}
    ]


async def _generate_career_suggestions(profile: MatchingProfile) -> List[Dict[str, Any]]:
    """Generate career advancement suggestions."""

    suggestions = []

    if profile.user_type == "learner":
        if profile.experience_level == "beginner":
            suggestions.extend([
                {"type": "role", "title": "Junior Developer", "match_probability": 0.8},
                {"type": "skill", "title": "Focus on core programming languages", "priority": "high"}
            ])
        elif profile.experience_level == "intermediate":
            suggestions.extend([
                {"type": "role", "title": "Senior Developer", "match_probability": 0.6},
                {"type": "specialization", "title": "Consider specializing in AI/ML", "priority": "medium"}
            ])

    return suggestions


def _identify_emerging_opportunities(matches: List[MatchResult]) -> List[Dict[str, Any]]:
    """Identify emerging opportunities from match data."""

    # Analyze skill combinations that are becoming popular
    skill_combinations = {}
    for match in matches:
        if len(match.skill_overlaps) >= 2:
            combo = tuple(sorted(match.skill_overlaps[:3]))
            skill_combinations[combo] = skill_combinations.get(combo, 0) + 1

    emerging = [
        {"skills": list(combo), "frequency": freq}
        for combo, freq in sorted(skill_combinations.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return emerging


def _generate_learner_market_recommendations(trending_data: Dict) -> List[str]:
    """Generate market recommendations for learners."""

    recommendations = []

    if "skills" in trending_data:
        top_skills = trending_data["skills"][:3]
        for skill_data in top_skills:
            recommendations.append(f"Consider learning {skill_data['skill']} - high demand in market")

    recommendations.append("Focus on remote-friendly skills as remote work continues to grow")
    recommendations.append("Develop both technical and soft skills for better matching")

    return recommendations


def _generate_company_market_recommendations(trending_data: Dict) -> List[str]:
    """Generate market recommendations for companies."""

    recommendations = [
        "Consider offering remote/hybrid work options to attract top talent",
        "Focus on skills-based hiring rather than just experience",
        "Invest in continuous learning programs for employees"
    ]

    if "skills" in trending_data:
        top_skills = trending_data["skills"][:2]
        for skill_data in top_skills:
            recommendations.append(f"High demand for {skill_data['skill']} skills in candidate pool")

    return recommendations