"""
Validation utilities for SkillForge AI User Service
"""

import re
from typing import Dict, Any, Optional, List


def validate_slug(slug: str) -> Dict[str, Any]:
    """Validate slug format."""
    if not slug:
        return {"is_valid": False, "error": "Slug cannot be empty"}
    
    if len(slug) < 3:
        return {"is_valid": False, "error": "Slug must be at least 3 characters long"}
    
    if len(slug) > 100:
        return {"is_valid": False, "error": "Slug cannot exceed 100 characters"}
    
    # Check if slug contains only allowed characters
    if not re.match(r'^[a-z0-9-]+$', slug):
        return {"is_valid": False, "error": "Slug can only contain lowercase letters, numbers, and hyphens"}
    
    # Check if slug starts or ends with hyphen
    if slug.startswith('-') or slug.endswith('-'):
        return {"is_valid": False, "error": "Slug cannot start or end with a hyphen"}
    
    # Check for consecutive hyphens
    if '--' in slug:
        return {"is_valid": False, "error": "Slug cannot contain consecutive hyphens"}
    
    # Reserved slugs
    reserved_slugs = [
        'api', 'www', 'mail', 'admin', 'support', 'help', 'blog', 'docs',
        'app', 'mobile', 'web', 'public', 'private', 'test', 'dev', 'staging',
        'production', 'auth', 'login', 'register', 'signup', 'signin', 'logout',
        'dashboard', 'profile', 'settings', 'account', 'billing', 'payment',
        'about', 'contact', 'terms', 'privacy', 'legal', 'security'
    ]
    
    if slug.lower() in reserved_slugs:
        return {"is_valid": False, "error": f"'{slug}' is a reserved slug"}
    
    return {"is_valid": True, "error": None}


def validate_username(username: str) -> Dict[str, Any]:
    """Validate username format."""
    if not username:
        return {"is_valid": False, "error": "Username cannot be empty"}
    
    if len(username) < 3:
        return {"is_valid": False, "error": "Username must be at least 3 characters long"}
    
    if len(username) > 50:
        return {"is_valid": False, "error": "Username cannot exceed 50 characters"}
    
    # Check if username contains only allowed characters
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return {"is_valid": False, "error": "Username can only contain letters, numbers, underscores, periods, and hyphens"}
    
    # Check if username starts with a letter
    if not username[0].isalpha():
        return {"is_valid": False, "error": "Username must start with a letter"}
    
    # Check for consecutive special characters
    if re.search(r'[_.-]{2,}', username):
        return {"is_valid": False, "error": "Username cannot contain consecutive special characters"}
    
    # Reserved usernames
    reserved_usernames = [
        'admin', 'administrator', 'root', 'system', 'support', 'help', 'api',
        'www', 'mail', 'email', 'user', 'users', 'test', 'demo', 'guest',
        'anonymous', 'null', 'undefined', 'skillforge', 'skillforgeai',
        'bot', 'service', 'account', 'accounts', 'profile', 'profiles'
    ]
    
    if username.lower() in reserved_usernames:
        return {"is_valid": False, "error": f"'{username}' is a reserved username"}
    
    return {"is_valid": True, "error": None}


def validate_phone_number(phone: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """Validate phone number format."""
    if not phone:
        return {"is_valid": True, "error": None}  # Phone is optional
    
    # Remove all non-digit characters except + at the beginning
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Remove + from anywhere except the beginning
    if clean_phone.startswith('+'):
        clean_phone = '+' + re.sub(r'[^0-9]', '', clean_phone[1:])
    else:
        clean_phone = re.sub(r'[^0-9]', '', clean_phone)
    
    if not clean_phone:
        return {"is_valid": False, "error": "Phone number cannot be empty"}
    
    # Check length (international format)
    if clean_phone.startswith('+'):
        if len(clean_phone) < 8 or len(clean_phone) > 17:
            return {"is_valid": False, "error": "International phone number must be between 7-16 digits"}
    else:
        if len(clean_phone) < 7 or len(clean_phone) > 15:
            return {"is_valid": False, "error": "Phone number must be between 7-15 digits"}
    
    # Basic format validation
    if clean_phone.startswith('+'):
        if not re.match(r'^\+[1-9]\d{6,15}$', clean_phone):
            return {"is_valid": False, "error": "Invalid international phone number format"}
    else:
        if not re.match(r'^[0-9]{7,15}$', clean_phone):
            return {"is_valid": False, "error": "Invalid phone number format"}
    
    return {
        "is_valid": True,
        "error": None,
        "formatted": clean_phone
    }


def validate_name(name: str, field_name: str = "Name") -> Dict[str, Any]:
    """Validate name fields (first_name, last_name, etc.)."""
    if not name:
        return {"is_valid": True, "error": None}  # Names are optional
    
    if len(name) > 100:
        return {"is_valid": False, "error": f"{field_name} cannot exceed 100 characters"}
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", name):
        return {"is_valid": False, "error": f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"}
    
    # Check for excessive consecutive spaces
    if re.search(r'\s{3,}', name):
        return {"is_valid": False, "error": f"{field_name} cannot contain more than two consecutive spaces"}
    
    # Check if it starts or ends with special characters
    if re.match(r'^[\s\'-]|[\s\'-]$', name):
        return {"is_valid": False, "error": f"{field_name} cannot start or end with spaces, hyphens, or apostrophes"}
    
    return {"is_valid": True, "error": None}


def validate_bio(bio: str) -> Dict[str, Any]:
    """Validate bio/description field."""
    if not bio:
        return {"is_valid": True, "error": None}  # Bio is optional
    
    if len(bio) > 1000:
        return {"is_valid": False, "error": "Bio cannot exceed 1000 characters"}
    
    # Check for excessive line breaks
    if bio.count('\n') > 10:
        return {"is_valid": False, "error": "Bio cannot contain more than 10 line breaks"}
    
    # Check for potential spam patterns
    if re.search(r'https?://\S+', bio, re.IGNORECASE):
        return {"is_valid": False, "error": "Bio cannot contain URLs"}
    
    # Check for excessive repetition
    if re.search(r'(.)\1{10,}', bio):
        return {"is_valid": False, "error": "Bio cannot contain excessive character repetition"}
    
    return {"is_valid": True, "error": None}


def validate_url(url: str, field_name: str = "URL") -> Dict[str, Any]:
    """Validate URL format."""
    if not url:
        return {"is_valid": True, "error": None}  # URL is optional
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return {"is_valid": False, "error": f"Invalid {field_name} format"}
    
    if len(url) > 500:
        return {"is_valid": False, "error": f"{field_name} cannot exceed 500 characters"}
    
    return {"is_valid": True, "error": None}


def validate_skills_list(skills: List[str]) -> Dict[str, Any]:
    """Validate skills list."""
    if not skills:
        return {"is_valid": True, "error": None}
    
    if len(skills) > 50:
        return {"is_valid": False, "error": "Cannot have more than 50 skills"}
    
    # Validate each skill
    for skill in skills:
        if not skill or not skill.strip():
            return {"is_valid": False, "error": "Skills cannot be empty"}
        
        if len(skill.strip()) > 100:
            return {"is_valid": False, "error": "Each skill cannot exceed 100 characters"}
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9\s+#\-.()]+$', skill.strip()):
            return {"is_valid": False, "error": "Skills can only contain letters, numbers, spaces, and common programming symbols"}
    
    # Check for duplicates (case insensitive)
    normalized_skills = [skill.strip().lower() for skill in skills]
    if len(normalized_skills) != len(set(normalized_skills)):
        return {"is_valid": False, "error": "Duplicate skills are not allowed"}
    
    return {"is_valid": True, "error": None}


def validate_company_name(name: str) -> Dict[str, Any]:
    """Validate company name."""
    if not name or not name.strip():
        return {"is_valid": False, "error": "Company name is required"}
    
    name = name.strip()
    
    if len(name) < 2:
        return {"is_valid": False, "error": "Company name must be at least 2 characters long"}
    
    if len(name) > 200:
        return {"is_valid": False, "error": "Company name cannot exceed 200 characters"}
    
    # Allow letters, numbers, spaces, and common business symbols
    if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s&.,\'-()]+$', name):
        return {"is_valid": False, "error": "Company name contains invalid characters"}
    
    return {"is_valid": True, "error": None}


def validate_address(address: str) -> Dict[str, Any]:
    """Validate address field."""
    if not address:
        return {"is_valid": True, "error": None}  # Address is optional
    
    if len(address) > 500:
        return {"is_valid": False, "error": "Address cannot exceed 500 characters"}
    
    # Check for valid characters (letters, numbers, spaces, common punctuation)
    if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s,.\'-#/]+$', address):
        return {"is_valid": False, "error": "Address contains invalid characters"}
    
    return {"is_valid": True, "error": None}


def validate_postal_code(postal_code: str, country: Optional[str] = None) -> Dict[str, Any]:
    """Validate postal code based on country."""
    if not postal_code:
        return {"is_valid": True, "error": None}  # Postal code is optional
    
    postal_code = postal_code.strip().upper()
    
    # Basic length check
    if len(postal_code) > 20:
        return {"is_valid": False, "error": "Postal code cannot exceed 20 characters"}
    
    # Country-specific validation
    patterns = {
        'US': r'^\d{5}(-\d{4})?$',  # 12345 or 12345-6789
        'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',  # K1A 0A6 or K1A0A6
        'UK': r'^[A-Z]{1,2}[0-9R][0-9A-Z]?\s?[0-9][A-Z]{2}$',  # SW1A 1AA
        'DE': r'^\d{5}$',  # 12345
        'FR': r'^\d{5}$',  # 12345
        'AU': r'^\d{4}$',  # 1234
        'JP': r'^\d{3}-?\d{4}$',  # 123-4567 or 1234567
    }
    
    if country and country.upper() in patterns:
        pattern = patterns[country.upper()]
        if not re.match(pattern, postal_code):
            return {"is_valid": False, "error": f"Invalid postal code format for {country}"}
    else:
        # Generic validation for unknown countries
        if not re.match(r'^[A-Z0-9\s-]+$', postal_code):
            return {"is_valid": False, "error": "Postal code can only contain letters, numbers, spaces, and hyphens"}
    
    return {"is_valid": True, "error": None}


def validate_file_upload(filename: str, allowed_extensions: List[str]) -> Dict[str, Any]:
    """Validate file upload."""
    if not filename:
        return {"is_valid": False, "error": "Filename is required"}
    
    # Check file extension
    if '.' not in filename:
        return {"is_valid": False, "error": "File must have an extension"}
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in [ext.lower() for ext in allowed_extensions]:
        return {"is_valid": False, "error": f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"}
    
    # Check filename length
    if len(filename) > 255:
        return {"is_valid": False, "error": "Filename too long"}
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in filename for char in dangerous_chars):
        return {"is_valid": False, "error": "Filename contains invalid characters"}
    
    return {"is_valid": True, "error": None}