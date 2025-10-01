"""
Tests for the matching engine core functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

from app.core.matching_engine import MatchingEngine, MatchingConfig
from app.models import MatchingProfile, MatchingType
from tests.conftest import ProfileFactory, TestUtils


class TestMatchingEngine:
    """Test suite for the MatchingEngine class."""

    @pytest.fixture
    def matching_engine(self):
        """Create a matching engine for testing."""
        config = MatchingConfig(
            skill_weight=0.3,
            experience_weight=0.2,
            location_weight=0.15,
            preference_weight=0.15,
            semantic_weight=0.2,
            min_score_threshold=0.1,
            max_results=50,
            use_cache=False  # Disable cache for tests
        )
        return MatchingEngine(config)

    @pytest.fixture
    def sample_profiles(self):
        """Create sample profiles for testing."""
        user_profile = ProfileFactory.create_learner_profile(
            user_id="user-1",
            skills=["python", "javascript", "react", "nodejs"],
            experience_level="intermediate"
        )

        target_profiles = [
            ProfileFactory.create_company_profile(
                user_id="company-1",
                skills=["python", "react", "aws", "docker"],
                experience_level="intermediate"
            ),
            ProfileFactory.create_company_profile(
                user_id="company-2",
                skills=["java", "spring", "microservices"],
                experience_level="advanced"
            ),
            ProfileFactory.create_learner_profile(
                user_id="learner-2",
                skills=["python", "machine learning", "tensorflow"],
                experience_level="beginner"
            )
        ]

        return user_profile, target_profiles

    @pytest.mark.asyncio
    async def test_initialization(self, matching_engine):
        """Test matching engine initialization."""
        assert matching_engine.config is not None
        assert matching_engine.sentence_model is None
        assert not matching_engine._model_loaded

        # Test initialization
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            mock_transformer.return_value = Mock()
            await matching_engine.initialize()

            assert matching_engine._model_loaded
            mock_transformer.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_matches_empty_targets(self, matching_engine, sample_profiles):
        """Test find_matches with empty target list."""
        user_profile, _ = sample_profiles

        matches = await matching_engine.find_matches(
            user_profile=user_profile,
            target_profiles=[],
            matching_type=MatchingType.USER_TO_PROJECT
        )

        assert matches == []

    @pytest.mark.asyncio
    async def test_find_matches_basic(self, matching_engine, sample_profiles):
        """Test basic matching functionality."""
        user_profile, target_profiles = sample_profiles

        # Mock the sentence transformer
        with patch.object(matching_engine, 'sentence_model', Mock()):
            with patch.object(matching_engine, '_model_loaded', True):
                with patch.object(matching_engine, '_calculate_semantic_score', return_value=0.6):
                    matches = await matching_engine.find_matches(
                        user_profile=user_profile,
                        target_profiles=target_profiles,
                        matching_type=MatchingType.USER_TO_PROJECT,
                        max_results=10
                    )

        assert len(matches) > 0
        assert all(match.overall_score >= matching_engine.config.min_score_threshold for match in matches)

        # Check that matches are sorted by score
        scores = [match.overall_score for match in matches]
        assert scores == sorted(scores, reverse=True)

        # Verify match structure
        for match in matches:
            TestUtils.assert_valid_uuid(match.user_id)
            TestUtils.assert_score_in_range(match.overall_score)
            assert match.matching_type == MatchingType.USER_TO_PROJECT
            assert isinstance(match.match_reasons, list)
            assert isinstance(match.skill_overlaps, list)

    @pytest.mark.asyncio
    async def test_calculate_skill_score(self, matching_engine):
        """Test skill score calculation."""
        user_profile = ProfileFactory.create_learner_profile(
            skills=["python", "javascript", "react"]
        )
        target_profile = ProfileFactory.create_company_profile(
            skills=["python", "react", "aws", "docker"]
        )

        score = await matching_engine._calculate_skill_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        assert score > 0  # Should have some overlap (python, react)

    def test_calculate_experience_score(self, matching_engine):
        """Test experience level compatibility calculation."""
        user_profile = ProfileFactory.create_learner_profile(experience_level="intermediate")
        target_profile = ProfileFactory.create_company_profile(experience_level="intermediate")

        score = matching_engine._calculate_experience_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        assert score == 1.0  # Perfect match

        # Test different experience levels
        target_profile.experience_level = "advanced"
        score = matching_engine._calculate_experience_score(user_profile, target_profile)
        assert 0 <= score < 1.0

    def test_calculate_location_score(self, matching_engine):
        """Test location compatibility calculation."""
        user_profile = ProfileFactory.create_learner_profile()
        user_profile.preferred_work_mode = "remote"

        target_profile = ProfileFactory.create_company_profile()
        target_profile.preferred_work_mode = "remote"

        score = matching_engine._calculate_location_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        assert score == 1.0  # Both prefer remote

    def test_calculate_preference_score(self, matching_engine):
        """Test preference compatibility calculation."""
        user_profile = ProfileFactory.create_learner_profile()
        user_profile.preferred_work_mode = "hybrid"
        user_profile.salary_expectations = {"min_salary": 80000, "max_salary": 120000}

        target_profile = ProfileFactory.create_company_profile()
        target_profile.preferred_work_mode = "hybrid"
        target_profile.salary_expectations = {"min_salary": 90000, "max_salary": 130000}

        score = matching_engine._calculate_preference_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        assert score > 0.5  # Should have good compatibility

    @pytest.mark.asyncio
    async def test_calculate_semantic_score(self, matching_engine):
        """Test semantic similarity calculation."""
        user_profile = ProfileFactory.create_learner_profile()
        user_profile.interests = ["web development", "backend systems"]

        target_profile = ProfileFactory.create_company_profile()
        target_profile.interests = ["web applications", "scalable systems"]

        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.15, 0.25, 0.35]])

        with patch.object(matching_engine, 'sentence_model', mock_model):
            with patch.object(matching_engine, '_model_loaded', True):
                score = await matching_engine._calculate_semantic_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        mock_model.encode.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_semantic_score_no_model(self, matching_engine):
        """Test semantic score when model is not available."""
        user_profile = ProfileFactory.create_learner_profile()
        target_profile = ProfileFactory.create_company_profile()

        # No model loaded
        matching_engine.sentence_model = None
        matching_engine._model_loaded = False

        with patch.object(matching_engine, 'initialize') as mock_init:
            mock_init.return_value = None  # Initialization fails
            score = await matching_engine._calculate_semantic_score(user_profile, target_profile)

        assert score == 0.0

    def test_calculate_confidence(self, matching_engine):
        """Test confidence calculation."""
        user_profile = ProfileFactory.create_learner_profile()
        user_profile.profile_completeness_score = 0.8
        user_profile.skills = ["python", "javascript"]
        user_profile.experience_level = "intermediate"
        user_profile.preferred_location = "San Francisco"

        target_profile = ProfileFactory.create_company_profile()
        target_profile.profile_completeness_score = 0.9
        target_profile.skills = ["python", "react"]
        target_profile.experience_level = "intermediate"
        target_profile.preferred_location = "San Francisco"

        confidence = matching_engine._calculate_confidence(user_profile, target_profile)

        TestUtils.assert_score_in_range(confidence)
        assert confidence > 0.5  # Should have reasonable confidence

    def test_generate_match_reasons(self, matching_engine):
        """Test match reasons generation."""
        user_profile = ProfileFactory.create_learner_profile()
        target_profile = ProfileFactory.create_company_profile()

        reasons = matching_engine._generate_match_reasons(
            user_profile, target_profile,
            skill_score=0.8,
            experience_score=0.9,
            location_score=0.7,
            preference_score=0.6,
            semantic_score=0.5
        )

        assert isinstance(reasons, list)
        assert len(reasons) > 0
        assert all(isinstance(reason, str) for reason in reasons)

    def test_analyze_skills(self, matching_engine):
        """Test skill analysis."""
        user_profile = ProfileFactory.create_learner_profile(
            skills=["python", "javascript", "react"]
        )
        target_profile = ProfileFactory.create_company_profile(
            skills=["python", "react", "aws", "docker"]
        )

        overlaps, missing = matching_engine._analyze_skills(user_profile, target_profile)

        assert isinstance(overlaps, list)
        assert isinstance(missing, list)
        assert "python" in overlaps
        assert "react" in overlaps
        assert "aws" in missing
        assert "docker" in missing

    def test_generate_cache_key(self, matching_engine):
        """Test cache key generation."""
        user_id = "test-user"
        target_profiles = [
            ProfileFactory.create_company_profile(user_id="comp-1"),
            ProfileFactory.create_company_profile(user_id="comp-2")
        ]
        matching_type = MatchingType.USER_TO_PROJECT

        cache_key = matching_engine._generate_cache_key(user_id, target_profiles, matching_type)

        assert isinstance(cache_key, str)
        assert "match:" in cache_key
        assert user_id in cache_key
        assert matching_type in cache_key

    def test_extract_profile_text(self, matching_engine):
        """Test profile text extraction."""
        profile = ProfileFactory.create_learner_profile()
        profile.skills = ["python", "javascript"]
        profile.interests = ["web development", "machine learning"]
        profile.profile_data = {
            "bio": "Experienced developer",
            "short": "x",  # Too short, should be ignored
            "number": 123  # Non-string, should be ignored
        }

        text = matching_engine._extract_profile_text(profile)

        assert isinstance(text, str)
        assert "python" in text
        assert "javascript" in text
        assert "web development" in text
        assert "machine learning" in text
        assert "Experienced developer" in text
        assert "x" not in text  # Too short
        assert "123" not in text  # Not a string

    @pytest.mark.asyncio
    async def test_matching_with_embeddings(self, matching_engine):
        """Test matching when profiles have embeddings."""
        user_profile = ProfileFactory.create_learner_profile()
        user_profile.skills_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        target_profile = ProfileFactory.create_company_profile()
        target_profile.skills_embedding = [0.15, 0.25, 0.35, 0.45, 0.55]

        score = await matching_engine._calculate_skill_score(user_profile, target_profile)

        TestUtils.assert_score_in_range(score)
        assert score > 0.5  # Should be high similarity due to close embeddings

    @pytest.mark.asyncio
    async def test_matching_performance(self, matching_engine):
        """Test matching performance with multiple profiles."""
        import time

        user_profile = ProfileFactory.create_learner_profile()
        target_profiles = [
            ProfileFactory.create_company_profile(user_id=f"company-{i}")
            for i in range(50)
        ]

        start_time = time.time()

        with patch.object(matching_engine, 'sentence_model', Mock()):
            with patch.object(matching_engine, '_model_loaded', True):
                with patch.object(matching_engine, '_calculate_semantic_score', return_value=0.6):
                    matches = await matching_engine.find_matches(
                        user_profile=user_profile,
                        target_profiles=target_profiles,
                        matching_type=MatchingType.USER_TO_PROJECT
                    )

        execution_time = time.time() - start_time

        assert len(matches) > 0
        assert execution_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_error_handling_in_matching(self, matching_engine):
        """Test error handling during matching process."""
        user_profile = ProfileFactory.create_learner_profile()
        target_profiles = [ProfileFactory.create_company_profile()]

        # Mock a method to raise an exception
        with patch.object(matching_engine, '_calculate_skill_score', side_effect=Exception("Test error")):
            matches = await matching_engine.find_matches(
                user_profile=user_profile,
                target_profiles=target_profiles,
                matching_type=MatchingType.USER_TO_PROJECT
            )

            # Should handle error gracefully and return empty results
            assert matches == []

    def test_matching_config_defaults(self):
        """Test matching configuration defaults."""
        config = MatchingConfig()

        assert config.skill_weight == 0.3
        assert config.experience_weight == 0.2
        assert config.location_weight == 0.15
        assert config.preference_weight == 0.15
        assert config.semantic_weight == 0.2
        assert config.min_score_threshold == 0.1
        assert config.max_results == 50
        assert config.use_cache is True
        assert config.cache_ttl == 3600

        # Verify weights sum to 1.0
        total_weight = (
            config.skill_weight +
            config.experience_weight +
            config.location_weight +
            config.preference_weight +
            config.semantic_weight
        )
        assert abs(total_weight - 1.0) < 0.01  # Allow for floating point precision

    @pytest.mark.asyncio
    async def test_matching_score_ranges(self, matching_engine):
        """Test that all matching scores are within valid ranges."""
        user_profile = ProfileFactory.create_learner_profile()
        target_profile = ProfileFactory.create_company_profile()

        # Test individual score methods
        skill_score = await matching_engine._calculate_skill_score(user_profile, target_profile)
        experience_score = matching_engine._calculate_experience_score(user_profile, target_profile)
        location_score = matching_engine._calculate_location_score(user_profile, target_profile)
        preference_score = matching_engine._calculate_preference_score(user_profile, target_profile)

        # All scores should be in valid range
        TestUtils.assert_score_in_range(skill_score)
        TestUtils.assert_score_in_range(experience_score)
        TestUtils.assert_score_in_range(location_score)
        TestUtils.assert_score_in_range(preference_score)

        # Test complete matching
        with patch.object(matching_engine, 'sentence_model', Mock()):
            with patch.object(matching_engine, '_model_loaded', True):
                with patch.object(matching_engine, '_calculate_semantic_score', return_value=0.6):
                    match_result = await matching_engine._calculate_match(
                        user_profile, target_profile, MatchingType.USER_TO_PROJECT
                    )

        assert match_result is not None
        TestUtils.assert_score_in_range(match_result.overall_score)
        TestUtils.assert_score_in_range(match_result.confidence_level)