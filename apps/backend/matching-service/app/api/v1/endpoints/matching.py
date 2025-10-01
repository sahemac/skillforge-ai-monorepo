"""
Matching endpoints for SkillForge AI Matching Service
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.core.database import get_session
from app.core.matching_engine import matching_engine
from app.core.cache import cache_service
from app.models import (
    MatchingProfile,
    MatchResult,
    MatchResultCreate,
    MatchResultResponse,
    MatchBatch,
    MatchBatchResponse,
    MatchingType
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


@router.post("/find-matches", response_model=List[MatchResultResponse])
@limiter.limit("10/minute")
async def find_matches(
    user_id: str,
    target_type: str = "project",
    matching_types: List[str] = Query(default=[MatchingType.USER_TO_PROJECT]),
    max_results: int = Query(default=20, ge=1, le=100),
    min_score: float = Query(default=0.1, ge=0.0, le=1.0),
    session: Session = Depends(get_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Find matches for a user against available targets.

    This endpoint performs real-time matching using multiple algorithms:
    - Skill-based matching with cosine similarity
    - Experience level compatibility
    - Location and work mode preferences
    - Semantic similarity using NLP
    """

    try:
        # Get user profile
        user_profile = session.exec(
            select(MatchingProfile).where(MatchingProfile.user_id == user_id)
        ).first()

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail=f"User profile not found for user_id: {user_id}"
            )

        if not user_profile.is_active:
            raise HTTPException(
                status_code=400,
                detail="User profile is inactive for matching"
            )

        # Get target profiles
        target_profiles = session.exec(
            select(MatchingProfile).where(
                MatchingProfile.user_type == target_type,
                MatchingProfile.is_active == True,
                MatchingProfile.user_id != user_id  # Exclude self
            )
        ).all()

        if not target_profiles:
            return []

        # Initialize matching engine if needed
        if not matching_engine._model_loaded:
            await matching_engine.initialize()

        # Find matches for each matching type
        all_matches = []
        for matching_type in matching_types:
            matches = await matching_engine.find_matches(
                user_profile=user_profile,
                target_profiles=target_profiles,
                matching_type=matching_type,
                max_results=max_results
            )

            # Filter by minimum score
            filtered_matches = [
                match for match in matches
                if match.overall_score >= min_score
            ]

            all_matches.extend(filtered_matches)

        # Remove duplicates and sort by score
        unique_matches = {}
        for match in all_matches:
            key = f"{match.target_id}_{match.matching_type}"
            if key not in unique_matches or match.overall_score > unique_matches[key].overall_score:
                unique_matches[key] = match

        final_matches = list(unique_matches.values())
        final_matches.sort(key=lambda x: x.overall_score, reverse=True)
        final_matches = final_matches[:max_results]

        # Save results to database in background
        background_tasks.add_task(
            save_match_results,
            session,
            final_matches
        )

        # Convert to response format
        return [
            MatchResultResponse(
                id=match.user_id + "_" + match.target_id,  # Temporary ID
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
                is_mutual=match.is_mutual,
                user_feedback=None,
                feedback_score=None,
                is_active=True,
                created_at="", # Will be set when saved
                updated_at=None
            )
            for match in final_matches
        ]

    except Exception as e:
        logger.error(f"Error finding matches for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error finding matches: {str(e)}"
        )


@router.post("/batch-matching", response_model=MatchBatchResponse)
@limiter.limit("5/minute")
async def batch_matching(
    batch_request: MatchBatch,
    session: Session = Depends(get_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Perform batch matching for multiple users.

    Efficient for processing multiple users at once with optimized algorithms.
    """

    try:
        import time
        start_time = time.time()

        # Validate batch size
        if len(batch_request.user_ids) > 50:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 50 users"
            )

        # Get user profiles
        user_profiles = session.exec(
            select(MatchingProfile).where(
                MatchingProfile.user_id.in_(batch_request.user_ids),
                MatchingProfile.is_active == True
            )
        ).all()

        if not user_profiles:
            raise HTTPException(
                status_code=404,
                detail="No active user profiles found"
            )

        # Get target profiles
        if batch_request.target_ids:
            target_profiles = session.exec(
                select(MatchingProfile).where(
                    MatchingProfile.user_id.in_(batch_request.target_ids),
                    MatchingProfile.is_active == True
                )
            ).all()
        else:
            # Match against all available profiles
            target_profiles = session.exec(
                select(MatchingProfile).where(
                    MatchingProfile.is_active == True,
                    ~MatchingProfile.user_id.in_(batch_request.user_ids)
                )
            ).all()

        # Initialize matching engine
        if not matching_engine._model_loaded:
            await matching_engine.initialize()

        # Process matches for each user
        matches_by_user = {}
        total_matches = 0

        # Use asyncio to process users concurrently
        async def process_user(user_profile):
            user_matches = []
            for matching_type in batch_request.matching_types:
                matches = await matching_engine.find_matches(
                    user_profile=user_profile,
                    target_profiles=target_profiles,
                    matching_type=matching_type,
                    max_results=batch_request.max_results_per_user
                )

                # Filter by threshold
                filtered_matches = [
                    match for match in matches
                    if match.overall_score >= batch_request.min_score_threshold
                ]

                user_matches.extend(filtered_matches)

            # Remove duplicates and limit results
            unique_matches = {}
            for match in user_matches:
                key = f"{match.target_id}_{match.matching_type}"
                if key not in unique_matches or match.overall_score > unique_matches[key].overall_score:
                    unique_matches[key] = match

            final_matches = list(unique_matches.values())
            final_matches.sort(key=lambda x: x.overall_score, reverse=True)
            final_matches = final_matches[:batch_request.max_results_per_user]

            return user_profile.user_id, final_matches

        # Process all users concurrently
        tasks = [process_user(profile) for profile in user_profiles]
        results = await asyncio.gather(*tasks)

        # Compile results
        for user_id, matches in results:
            total_matches += len(matches)
            matches_by_user[user_id] = [
                MatchResultResponse(
                    id=match.user_id + "_" + match.target_id,
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
                    is_mutual=match.is_mutual,
                    user_feedback=None,
                    feedback_score=None,
                    is_active=True,
                    created_at="",
                    updated_at=None
                )
                for match in matches
            ]

        processing_time_ms = (time.time() - start_time) * 1000

        # Generate summary
        summary = {
            "total_users_processed": len(user_profiles),
            "total_targets_available": len(target_profiles),
            "average_matches_per_user": total_matches / len(user_profiles) if user_profiles else 0,
            "processing_time_per_user_ms": processing_time_ms / len(user_profiles) if user_profiles else 0,
            "matching_types_used": batch_request.matching_types
        }

        return MatchBatchResponse(
            total_matches=total_matches,
            processing_time_ms=processing_time_ms,
            matches_by_user=matches_by_user,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch matching: {str(e)}"
        )


@router.get("/mutual-matches/{user_id}", response_model=List[MatchResultResponse])
@limiter.limit("20/minute")
async def get_mutual_matches(
    user_id: str,
    session: Session = Depends(get_session)
):
    """Get mutual matches where both parties have high compatibility."""

    try:
        # Get matches where user matched with targets
        user_matches = session.exec(
            select(MatchResult).where(
                MatchResult.user_id == user_id,
                MatchResult.is_active == True,
                MatchResult.overall_score >= 0.6  # High compatibility threshold
            )
        ).all()

        # Find mutual matches
        mutual_matches = []
        for match in user_matches:
            # Check if target also has a match back to user
            reverse_match = session.exec(
                select(MatchResult).where(
                    MatchResult.user_id == match.target_id,
                    MatchResult.target_id == user_id,
                    MatchResult.is_active == True,
                    MatchResult.overall_score >= 0.6
                )
            ).first()

            if reverse_match:
                # Mark as mutual
                match.is_mutual = True
                mutual_matches.append(match)

        # Convert to response format
        return [
            MatchResultResponse.model_validate(match)
            for match in mutual_matches
        ]

    except Exception as e:
        logger.error(f"Error getting mutual matches for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting mutual matches: {str(e)}"
        )


@router.post("/feedback/{match_id}")
@limiter.limit("30/minute")
async def provide_feedback(
    match_id: str,
    feedback: str,
    rating: int = Query(ge=1, le=5),
    session: Session = Depends(get_session)
):
    """Provide feedback on a match to improve algorithm."""

    try:
        match = session.exec(
            select(MatchResult).where(MatchResult.id == match_id)
        ).first()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Match not found"
            )

        # Update feedback
        match.user_feedback = feedback
        match.feedback_score = rating

        session.add(match)
        session.commit()
        session.refresh(match)

        # TODO: Use feedback to retrain algorithms

        return {"message": "Feedback recorded successfully"}

    except Exception as e:
        logger.error(f"Error recording feedback for match {match_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recording feedback: {str(e)}"
        )


async def save_match_results(session: Session, matches: List[MatchResultCreate]):
    """Background task to save match results to database."""

    try:
        for match_data in matches:
            match = MatchResult(**match_data.model_dump())
            session.add(match)

        session.commit()
        logger.info(f"Saved {len(matches)} match results to database")

    except Exception as e:
        logger.error(f"Error saving match results: {e}")
        session.rollback()