"""
Helper utilities for SkillForge AI User Service
"""

import re
import unicodedata
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import string


def generate_slug(text: str, max_length: int = 100) -> str:
    """Generate a URL-safe slug from text."""
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rstrip('-')
    
    return text


def format_name(first_name: Optional[str], last_name: Optional[str]) -> str:
    """Format first and last name into full name."""
    parts = []
    if first_name and first_name.strip():
        parts.append(first_name.strip())
    if last_name and last_name.strip():
        parts.append(last_name.strip())
    
    return " ".join(parts)


def parse_skills(skills_input: Any) -> List[str]:
    """Parse skills input into a clean list."""
    if not skills_input:
        return []
    
    if isinstance(skills_input, str):
        # Split by comma, semicolon, or newline
        skills = re.split(r'[,;\n]+', skills_input)
    elif isinstance(skills_input, list):
        skills = skills_input
    else:
        return []
    
    # Clean and deduplicate
    clean_skills = []
    seen = set()
    
    for skill in skills:
        if isinstance(skill, str):
            clean_skill = skill.strip()
            if clean_skill and clean_skill.lower() not in seen:
                clean_skills.append(clean_skill)
                seen.add(clean_skill.lower())
    
    return clean_skills


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization (remove all HTML tags)."""
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    return clean_text.strip()


def generate_random_string(length: int = 32, include_symbols: bool = False) -> str:
    """Generate a random string."""
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.now().date()
    birth_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def is_valid_timezone(timezone_str: str) -> bool:
    """Check if timezone string is valid."""
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(timezone_str)
        return True
    except Exception:
        # Fallback for older Python versions or invalid timezones
        import pytz
        try:
            pytz.timezone(timezone_str)
            return True
        except:
            return False


def get_time_ago(dt: datetime) -> str:
    """Get human readable time ago string."""
    now = datetime.utcnow()
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=None)
        now = now.replace(tzinfo=None)
    
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def extract_domain_from_email(email: str) -> str:
    """Extract domain from email address."""
    if '@' not in email:
        return ""
    
    return email.split('@')[1].lower()


def mask_email(email: str) -> str:
    """Mask email for privacy (show first 2 chars and domain)."""
    if '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[:2] + '*' * (len(username) - 2)
    
    return f"{masked_username}@{domain}"


def mask_phone_number(phone: str) -> str:
    """Mask phone number for privacy."""
    if not phone:
        return phone
    
    # Remove non-digits except +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if len(clean_phone) < 4:
        return phone
    
    # Show first 2 and last 2 digits
    if clean_phone.startswith('+'):
        visible_start = clean_phone[:3]  # +XX
        visible_end = clean_phone[-2:]
        masked_middle = '*' * (len(clean_phone) - 5)
        return f"{visible_start}{masked_middle}{visible_end}"
    else:
        visible_start = clean_phone[:2]
        visible_end = clean_phone[-2:]
        masked_middle = '*' * (len(clean_phone) - 4)
        return f"{visible_start}{masked_middle}{visible_end}"


def parse_user_agent(user_agent: str) -> Dict[str, str]:
    """Parse user agent string to extract browser and OS info."""
    if not user_agent:
        return {"browser": "Unknown", "os": "Unknown", "device": "Unknown"}
    
    browser = "Unknown"
    os = "Unknown"
    device = "Desktop"
    
    # Browser detection
    if "Chrome" in user_agent and "Edg" not in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser = "Safari"
    elif "Edg" in user_agent:
        browser = "Edge"
    elif "Opera" in user_agent or "OPR" in user_agent:
        browser = "Opera"
    
    # OS detection
    if "Windows" in user_agent:
        os = "Windows"
    elif "Mac OS" in user_agent or "macOS" in user_agent:
        os = "macOS"
    elif "Linux" in user_agent:
        os = "Linux"
    elif "Android" in user_agent:
        os = "Android"
        device = "Mobile"
    elif "iOS" in user_agent or "iPhone" in user_agent or "iPad" in user_agent:
        os = "iOS"
        device = "Mobile" if "iPhone" in user_agent else "Tablet"
    
    # Device type detection
    if "Mobile" in user_agent and device == "Desktop":
        device = "Mobile"
    elif "Tablet" in user_agent or "iPad" in user_agent:
        device = "Tablet"
    
    return {"browser": browser, "os": os, "device": device}


def generate_username_suggestions(base_name: str, count: int = 5) -> List[str]:
    """Generate username suggestions based on a base name."""
    if not base_name:
        return []
    
    # Clean base name
    clean_base = re.sub(r'[^\w]', '', base_name.lower())
    if not clean_base:
        clean_base = "user"
    
    suggestions = []
    
    # Add base name variations
    suggestions.append(clean_base)
    
    # Add with numbers
    for i in range(2, count + 2):
        suggestions.append(f"{clean_base}{i}")
    
    # Add with underscores
    suggestions.append(f"{clean_base}_")
    suggestions.append(f"_{clean_base}")
    
    # Add with year
    current_year = datetime.now().year
    suggestions.append(f"{clean_base}{current_year}")
    
    # Add random suffix
    random_suffix = generate_random_string(4)
    suggestions.append(f"{clean_base}{random_suffix}")
    
    return suggestions[:count]


def validate_and_format_location(location: str) -> str:
    """Validate and format location string."""
    if not location:
        return ""
    
    # Basic cleaning
    location = location.strip()
    
    # Remove extra spaces
    location = re.sub(r'\s+', ' ', location)
    
    # Capitalize first letter of each word
    location = ' '.join(word.capitalize() for word in location.split())
    
    return location


def calculate_password_strength_score(password: str) -> Dict[str, Any]:
    """Calculate password strength score (0-100)."""
    if not password:
        return {"score": 0, "strength": "very weak"}
    
    score = 0
    length = len(password)
    
    # Length scoring
    if length >= 8:
        score += 20
    if length >= 12:
        score += 10
    if length >= 16:
        score += 10
    
    # Character variety scoring
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+=\-\[\]{}|;:,.<>?]', password))
    
    char_types = sum([has_lower, has_upper, has_digit, has_special])
    score += char_types * 10
    
    # Pattern checks (deduct points for common patterns)
    if re.search(r'(.)\1{2,}', password):  # Repeated characters
        score -= 10
    if re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # Sequential numbers
        score -= 10
    if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):  # Sequential letters
        score -= 10
    
    # Common patterns
    common_patterns = ['password', '123456', 'qwerty', 'admin', 'login']
    for pattern in common_patterns:
        if pattern in password.lower():
            score -= 20
            break
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, score))
    
    # Determine strength level
    if score >= 80:
        strength = "very strong"
    elif score >= 60:
        strength = "strong"
    elif score >= 40:
        strength = "moderate"
    elif score >= 20:
        strength = "weak"
    else:
        strength = "very weak"
    
    return {
        "score": score,
        "strength": strength,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_special": has_special,
        "length": length
    }