# SkillForge AI - Matching Service

**Version:** 1.0.0
**Status:** Production Ready
**Business Critical:** ✅ Core Business Logic

## Overview

The Matching Service is the **core business logic** component of SkillForge AI, responsible for intelligent matching between learners, companies, and projects using advanced machine learning algorithms.

### Key Features

🔍 **Advanced Matching Algorithms**
- Skill-based matching with cosine similarity
- Semantic similarity using NLP transformers
- Experience level compatibility scoring
- Location and work mode preferences
- Collaborative filtering for recommendations

🤖 **AI-Powered Intelligence**
- Sentence transformers for semantic analysis
- Real-time embeddings generation
- Personalized recommendation engine
- Learning path suggestions

⚡ **High Performance**
- Redis caching for sub-second responses
- Batch processing capabilities
- Async/await architecture
- Optimized database queries with proper indexing

📊 **Production Monitoring**
- Prometheus metrics for all operations
- Performance tracking and alerting
- Error tracking and debugging
- Cache hit ratio monitoring

## Architecture

```
matching-service/
├── app/
│   ├── api/v1/endpoints/          # FastAPI endpoints
│   │   ├── matching.py            # Core matching operations
│   │   ├── preferences.py         # User preference management
│   │   └── recommendations.py     # AI recommendations
│   ├── core/
│   │   ├── matching_engine.py     # Main matching logic
│   │   ├── matching_metrics.py    # Prometheus metrics
│   │   ├── algorithms/            # ML algorithms
│   │   ├── config.py              # Service configuration
│   │   ├── database.py            # Database connections
│   │   ├── cache.py               # Redis operations
│   │   └── monitoring.py          # Health checks
│   ├── models/                    # SQLModel data models
│   │   ├── matching_profile.py    # User profiles for matching
│   │   ├── match_result.py        # Match results and scores
│   │   └── preference.py          # User preferences
│   └── schemas/                   # Pydantic request/response schemas
├── alembic/                       # Database migrations
├── tests/                         # Comprehensive test suite
├── requirements.txt               # Dependencies
└── Dockerfile                     # Container configuration
```

## API Endpoints

### Core Matching

**POST `/api/v1/matching/find-matches`**
Find matches for a user against available targets
```json
{
  "user_id": "string",
  "target_type": "project|company|user",
  "matching_types": ["user_to_project"],
  "max_results": 20,
  "min_score": 0.1
}
```

**POST `/api/v1/matching/batch-matching`**
Process multiple users in batch for efficiency
```json
{
  "user_ids": ["user1", "user2"],
  "matching_types": ["user_to_project"],
  "max_results_per_user": 10
}
```

**GET `/api/v1/matching/mutual-matches/{user_id}`**
Get mutual matches where both parties have high compatibility

### User Preferences

**POST `/api/v1/preferences/`**
Create user matching preferences

**GET `/api/v1/preferences/user/{user_id}`**
Get all preferences for a user

**PUT `/api/v1/preferences/{preference_id}`**
Update existing preference

### AI Recommendations

**GET `/api/v1/recommendations/for-user/{user_id}`**
Get personalized AI recommendations

**GET `/api/v1/recommendations/skill-development/{user_id}`**
Get AI-powered skill development recommendations

**GET `/api/v1/recommendations/trending`**
Get trending opportunities and market insights

## Matching Algorithms

### 1. Skill-Based Matching
- **Jaccard Similarity**: Set intersection/union for exact matches
- **Cosine Similarity**: TF-IDF vectors for semantic skills
- **Embedding Similarity**: Pre-computed skill embeddings

### 2. Semantic Analysis
- **Model**: `all-MiniLM-L6-v2` Sentence Transformer
- **Input**: Combined profile text (skills, interests, bio)
- **Output**: Similarity score 0.0-1.0

### 3. Experience Compatibility
- **Levels**: beginner → intermediate → advanced → expert
- **Strategy**: Learners can grow, companies prefer exact/higher
- **Score**: Distance-based compatibility

### 4. Location & Preferences
- **Remote Work**: Perfect score for remote-remote matches
- **Location**: Geographic distance calculation
- **Work Mode**: Hybrid flexibility scoring

### 5. Overall Scoring
```
Overall Score = (
  Skills × 0.30 +
  Experience × 0.20 +
  Location × 0.15 +
  Preferences × 0.15 +
  Semantic × 0.20
)
```

## Data Models

### MatchingProfile
User profile optimized for matching algorithms
```python
- user_id: str                    # Reference to user service
- user_type: str                  # learner|company|mentor
- skills: List[str]               # Skill tags
- skills_embedding: List[float]   # Pre-computed embeddings
- experience_level: str           # Skill level
- preferred_location: str         # Location preference
- salary_expectations: Dict       # Salary range
```

### MatchResult
Results of matching with detailed scoring
```python
- user_id: str                    # Source user
- target_id: str                  # Matched target
- overall_score: float            # Combined score (0.0-1.0)
- skill_score: float              # Skills compatibility
- confidence_level: float         # Algorithm confidence
- match_reasons: List[str]        # Human-readable reasons
- skill_overlaps: List[str]       # Common skills
```

## Performance & Scaling

### Caching Strategy
- **Match Results**: 1 hour TTL
- **Profile Embeddings**: 24 hour TTL
- **Trending Data**: 30 minutes TTL

### Database Optimization
- **Indexes**: user_id, user_type, experience_level, is_active
- **Composite Indexes**: (user_id, target_type, matching_type)
- **Partitioning**: Future implementation for scale

### Batch Processing
- **Max Batch Size**: 50 users
- **Concurrent Processing**: asyncio.gather()
- **Memory Management**: Streaming results

## Monitoring & Observability

### Prometheus Metrics

**Business Metrics:**
- `matching_requests_total` - Total matching requests
- `matching_results_count` - Results per request
- `matching_scores_distribution` - Score distributions
- `recommendation_accuracy` - User feedback accuracy

**Performance Metrics:**
- `matching_algorithm_duration` - Algorithm execution time
- `cache_hit_ratio` - Cache effectiveness
- `skill_matcher_performance` - Skill matching performance
- `semantic_analysis_duration` - ML model performance

**System Health:**
- `active_matching_profiles_total` - Active user profiles
- `matching_errors_total` - Error tracking
- `ml_model_performance_score` - Model accuracy metrics

### Alerting Rules

**Critical Alerts:**
- Matching request success rate < 95%
- Average response time > 5 seconds
- Cache hit ratio < 50%
- Database connection failures

**Warning Alerts:**
- Match quality score trend declining
- High error rate on specific algorithms
- Memory usage > 80%

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test category
pytest tests/test_matching_engine.py -v

# Performance testing
pytest tests/test_performance.py --benchmark-only
```

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t skillforge-matching-service .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  skillforge-matching-service
```

### Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `DEBUG=false` - Production mode
- `LOG_LEVEL=INFO` - Logging level
- `CACHE_TTL=3600` - Cache TTL in seconds
- `MAX_RESULTS=50` - Default max results
- `ENABLE_METRICS=true` - Prometheus metrics

## API Integration

### Service Dependencies

**Consumes:**
- `user-service` - User profile data
- `project-service` - Project/job postings

**Provides:**
- Matching results to frontend applications
- Recommendation data for notifications
- Analytics data for reporting service

### Authentication
Uses Google IAP (Identity-Aware Proxy) for service-to-service authentication.

### Rate Limiting
- Matching endpoints: 10 requests/minute per user
- Batch processing: 5 requests/minute per user
- Recommendations: 20 requests/minute per user

## Machine Learning Pipeline

### Model Training
1. **Data Collection**: User interactions, feedback, successful matches
2. **Feature Engineering**: Skills embeddings, profile completeness
3. **Model Training**: Periodic retraining with new data
4. **Evaluation**: A/B testing for model improvements

### Embedding Management
- **Model**: Sentence Transformers all-MiniLM-L6-v2
- **Update Frequency**: Weekly batch processing
- **Storage**: PostgreSQL JSON columns + optional vector DB

### Feedback Loop
- User ratings on matches (1-5 stars)
- Implicit feedback from user actions
- Model improvement through supervised learning

## Security & Privacy

### Data Protection
- PII encryption in database
- Secure embedding storage
- GDPR compliance for EU users

### API Security
- Rate limiting per endpoint
- Input validation and sanitization
- SQL injection protection via SQLModel

## Performance Benchmarks

### Target Metrics
- **Response Time**: < 2 seconds for 95% of requests
- **Throughput**: 1000+ matches/second
- **Accuracy**: 85%+ user satisfaction
- **Cache Hit Rate**: > 70%

### Current Performance
- **Single Match**: ~150ms average
- **Batch Processing**: 50 users in ~3 seconds
- **Memory Usage**: < 512MB baseline
- **Database Queries**: < 10ms average

## Roadmap

### Version 1.1 (Next Quarter)
- [ ] Vector database integration (Pinecone/Weaviate)
- [ ] Advanced ML models (BERT, custom transformers)
- [ ] Real-time collaborative filtering
- [ ] GraphQL API support

### Version 1.2 (Future)
- [ ] Multi-lingual matching support
- [ ] Industry-specific algorithms
- [ ] Federated learning capabilities
- [ ] Advanced analytics dashboard

## Contributing

### Code Standards
- Follow PEP 8 style guidelines
- Maintain 90%+ test coverage
- Document all public methods
- Use type hints throughout

### Development Workflow
1. Create feature branch from `develop`
2. Write comprehensive tests
3. Update documentation
4. Submit PR with detailed description

## Support & Maintenance

### Logging
All operations logged with structured JSON format:
```json
{
  "timestamp": "2024-09-24T00:00:00Z",
  "level": "INFO",
  "service": "matching-service",
  "operation": "find_matches",
  "user_id": "user-123",
  "duration_ms": 150,
  "results_count": 12
}
```

### Error Handling
- Graceful degradation when ML models fail
- Retry logic for external service calls
- Detailed error tracking and alerting

### Health Checks
- `/health` - Service health status
- `/metrics` - Prometheus metrics endpoint
- `/cache/info` - Cache status information

---

**Contact**: SkillForge AI Team
**Documentation**: [Internal Wiki Link]
**Monitoring**: [Grafana Dashboard Link]