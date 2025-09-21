#!/usr/bin/env python3
"""
Create test users for SkillForge AI according to the correct business model
B2B2C platform: Companies propose projects, Learners work on them, AI evaluates deliverables
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.user import UserRegister
from app.models.user_simple import UserRole, UserSkillLevel
from app.models.company_simple import CompanySize, IndustryType

# Test users following SkillForge AI business model
SKILLFORGE_TEST_USERS = [
    # === PLATFORM ADMINISTRATORS ===
    {
        'email': 'admin@skillforge.ai',
        'username': 'admin_platform',
        'password': 'AdminPass123!',
        'confirm_password': 'AdminPass123!',
        'first_name': 'Platform',
        'last_name': 'Administrator',
        'bio': 'Platform administrator responsible for company validation and global moderation',
        'job_title': 'Platform Administrator',
        'location': 'Remote',
        'timezone': 'UTC',
        'experience_level': UserSkillLevel.EXPERT,
        'skills': ['platform_management', 'business_validation', 'content_moderation'],
        'interests': ['ai_education', 'business_development', 'platform_growth'],
        'role_context': UserRole.ADMIN,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    
    # === COMPANY CONTACTS (Representatives who create projects) ===
    {
        'email': 'contact@techcorp.ai',
        'username': 'techcorp_ai',
        'password': 'TechPass123!',
        'confirm_password': 'TechPass123!',
        'first_name': 'Sarah',
        'last_name': 'Wilson',
        'bio': 'HR Director at TechCorp AI, responsible for talent acquisition and skill development programs',
        'job_title': 'HR Director',
        'location': 'Paris, France',
        'timezone': 'Europe/Paris',
        'experience_level': UserSkillLevel.ADVANCED,
        'skills': ['talent_acquisition', 'hr_management', 'ai_strategy'],
        'interests': ['talent_development', 'ai_innovation', 'workforce_planning'],
        'role_context': UserRole.COMPANY_CONTACT,
        'company_info': {
            'name': 'TechCorp AI',
            'industry': IndustryType.TECHNOLOGY,
            'size': CompanySize.MEDIUM,
            'description': 'AI consulting company specializing in machine learning solutions for enterprises'
        },
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    {
        'email': 'projects@financeplus.com',
        'username': 'financeplus_projects',
        'password': 'FinancePass123!',
        'confirm_password': 'FinancePass123!',
        'first_name': 'Michel',
        'last_name': 'Dubois',
        'bio': 'CTO at FinancePlus, leading digital transformation and AI adoption initiatives',
        'job_title': 'Chief Technology Officer',
        'location': 'Lyon, France',
        'timezone': 'Europe/Paris',
        'experience_level': UserSkillLevel.EXPERT,
        'skills': ['fintech', 'ai_strategy', 'digital_transformation'],
        'interests': ['financial_ai', 'risk_management', 'innovation'],
        'role_context': UserRole.COMPANY_CONTACT,
        'company_info': {
            'name': 'FinancePlus',
            'industry': IndustryType.FINANCE,
            'size': CompanySize.LARGE,
            'description': 'Leading financial services company implementing AI for risk assessment and customer insights'
        },
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    {
        'email': 'innovation@healthtech.fr',
        'username': 'healthtech_innovation',
        'password': 'HealthPass123!',
        'confirm_password': 'HealthPass123!',
        'first_name': 'Dr. Marie',
        'last_name': 'Laurent',
        'bio': 'Head of Innovation at HealthTech France, driving AI adoption in healthcare solutions',
        'job_title': 'Head of Innovation',
        'location': 'Marseille, France',
        'timezone': 'Europe/Paris',
        'experience_level': UserSkillLevel.EXPERT,
        'skills': ['healthcare_ai', 'medical_innovation', 'regulatory_compliance'],
        'interests': ['medical_ai', 'patient_care', 'health_innovation'],
        'role_context': UserRole.COMPANY_CONTACT,
        'company_info': {
            'name': 'HealthTech France',
            'industry': IndustryType.HEALTHCARE,
            'size': CompanySize.SMALL,
            'description': 'Healthcare technology startup developing AI-powered diagnostic tools'
        },
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    
    # === LEARNERS (Different experience levels working on company projects) ===
    {
        'email': 'student.beginner@gmail.com',
        'username': 'jean_beginner',
        'password': 'StudentPass123!',
        'confirm_password': 'StudentPass123!',
        'first_name': 'Jean',
        'last_name': 'Martin',
        'bio': 'Computer science student eager to learn AI through real-world projects',
        'job_title': 'Computer Science Student',
        'location': 'Toulouse, France',
        'timezone': 'Europe/Paris',
        'experience_level': UserSkillLevel.BEGINNER,
        'skills': ['python_basics', 'mathematics', 'programming_fundamentals'],
        'interests': ['machine_learning', 'data_science', 'career_development'],
        'role_context': UserRole.USER,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    {
        'email': 'dev.intermediate@outlook.com',
        'username': 'alice_developer',
        'password': 'DevPass123!',
        'confirm_password': 'DevPass123!',
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'bio': 'Full-stack developer transitioning to AI/ML to enhance career prospects',
        'job_title': 'Full-Stack Developer',
        'location': 'Montreal, Canada',
        'timezone': 'America/Montreal',
        'experience_level': UserSkillLevel.INTERMEDIATE,
        'skills': ['web_development', 'python', 'databases', 'basic_ml'],
        'interests': ['machine_learning', 'ai_applications', 'career_transition'],
        'role_context': UserRole.USER,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    {
        'email': 'data.analyst@yahoo.com',
        'username': 'carlos_analyst',
        'password': 'AnalystPass123!',
        'confirm_password': 'AnalystPass123!',
        'first_name': 'Carlos',
        'last_name': 'Rodriguez',
        'bio': 'Data analyst looking to advance skills in advanced AI techniques through practical projects',
        'job_title': 'Data Analyst',
        'location': 'Barcelona, Spain',
        'timezone': 'Europe/Madrid',
        'experience_level': UserSkillLevel.ADVANCED,
        'skills': ['data_analysis', 'statistics', 'python', 'sql', 'visualization'],
        'interests': ['deep_learning', 'nlp', 'computer_vision'],
        'role_context': UserRole.USER,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    {
        'email': 'expert.researcher@protonmail.com',
        'username': 'dr_chen_researcher',
        'password': 'ResearchPass123!',
        'confirm_password': 'ResearchPass123!',
        'first_name': 'Dr. Robert',
        'last_name': 'Chen',
        'bio': 'AI researcher seeking to apply cutting-edge research to real business problems',
        'job_title': 'AI Research Scientist',
        'location': 'Singapore',
        'timezone': 'Asia/Singapore',
        'experience_level': UserSkillLevel.EXPERT,
        'skills': ['deep_learning', 'research', 'tensorflow', 'pytorch', 'nlp'],
        'interests': ['applied_research', 'industry_collaboration', 'innovation'],
        'role_context': UserRole.USER,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    
    # === PREMIUM LEARNERS (Advanced access to exclusive features) ===
    {
        'email': 'premium.consultant@icloud.com',
        'username': 'premium_consultant',
        'password': 'PremiumPass123!',
        'confirm_password': 'PremiumPass123!',
        'first_name': 'Emma',
        'last_name': 'Thompson',
        'bio': 'Independent AI consultant using SkillForge to stay current with industry trends and expand skillset',
        'job_title': 'AI Consultant',
        'location': 'London, UK',
        'timezone': 'Europe/London',
        'experience_level': UserSkillLevel.EXPERT,
        'skills': ['ai_consulting', 'business_strategy', 'machine_learning', 'client_management'],
        'interests': ['emerging_ai_trends', 'business_applications', 'professional_development'],
        'role_context': UserRole.PREMIUM_USER,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    },
    
    # === COMMUNITY MODERATORS ===
    {
        'email': 'moderator@skillforge.ai',
        'username': 'community_moderator',
        'password': 'ModeratorPass123!',
        'confirm_password': 'ModeratorPass123!',
        'first_name': 'Sophie',
        'last_name': 'Moreau',
        'bio': 'Community moderator ensuring quality interactions between learners and companies',
        'job_title': 'Community Manager',
        'location': 'Nice, France',
        'timezone': 'Europe/Paris',
        'experience_level': UserSkillLevel.ADVANCED,
        'skills': ['community_management', 'content_moderation', 'communication'],
        'interests': ['community_building', 'education', 'platform_quality'],
        'role_context': UserRole.MODERATOR,
        'terms_accepted': True,
        'privacy_policy_accepted': True,
        'newsletter_subscribed': True
    }
]

async def validate_skillforge_users():
    """Validate test users according to SkillForge AI business model"""
    
    print("Validating SkillForge AI Test Users")
    print("Business Model: B2B2C AI Education Platform")
    print("=" * 60)
    
    valid_users = []
    invalid_users = []
    
    role_counts = {
        UserRole.ADMIN: 0,
        UserRole.COMPANY_CONTACT: 0,
        UserRole.USER: 0,
        UserRole.PREMIUM_USER: 0,
        UserRole.MODERATOR: 0
    }
    
    for user_data in SKILLFORGE_TEST_USERS:
        try:
            # Extract role context for validation (keep copy for later use)
            role_context = user_data['role_context']
            company_info = user_data.get('company_info', None)
            
            # Create copy for validation without role_context
            validation_data = user_data.copy()
            validation_data.pop('role_context')
            validation_data.pop('company_info', None)
            
            # Validate using UserRegister schema
            user_register = UserRegister(**validation_data)
            valid_users.append((user_data['email'], user_register, role_context, company_info))
            role_counts[role_context] += 1
            
            role_icon = {
                UserRole.ADMIN: "[ADMIN]",
                UserRole.COMPANY_CONTACT: "[COMPANY]", 
                UserRole.USER: "[USER]",
                UserRole.PREMIUM_USER: "[PREMIUM]",
                UserRole.MODERATOR: "[MOD]"
            }
            
            print(f"{role_icon[role_context]} {user_data['email']} ({role_context.value}) - {user_data['experience_level'].value}")
            if company_info:
                print(f"   Company: {company_info['name']} ({company_info['industry'].value})")
                
        except Exception as e:
            invalid_users.append((user_data['email'], str(e)))
            print(f"[ERROR] Invalid: {user_data['email']} - {e}")
    
    print(f"\nValidation Results:")
    print(f"[OK] Valid users: {len(valid_users)}")
    print(f"[ERROR] Invalid users: {len(invalid_users)}")
    
    print(f"\nRole Distribution (SkillForge AI Business Model):")
    print(f"[ADMIN] Administrators: {role_counts[UserRole.ADMIN]} (validate companies, moderate platform)")
    print(f"[COMPANY] Company Contacts: {role_counts[UserRole.COMPANY_CONTACT]} (create projects, evaluate talents)")
    print(f"[USER] Learners: {role_counts[UserRole.USER]} (work on company projects)")
    print(f"[PREMIUM] Premium Learners: {role_counts[UserRole.PREMIUM_USER]} (advanced features access)")
    print(f"[MOD] Moderators: {role_counts[UserRole.MODERATOR]} (community management)")
    
    if invalid_users:
        print("\nInvalid users details:")
        for email, error in invalid_users:
            print(f"- {email}: {error}")
        return False, []
    
    return True, valid_users

def generate_skillforge_data():
    """Generate data files for SkillForge AI testing"""
    
    # Prepare JSON-serializable data
    json_users = []
    companies = []
    
    for user_data in SKILLFORGE_TEST_USERS:
        # User data
        json_user = user_data.copy()
        json_user['experience_level'] = user_data['experience_level'].value
        json_user['role_context'] = user_data['role_context'].value
        
        # Extract company info if present
        if 'company_info' in json_user:
            company_info = json_user.pop('company_info')
            company_info['contact_email'] = user_data['email']
            company_info['industry'] = company_info['industry'].value
            company_info['size'] = company_info['size'].value
            companies.append(company_info)
        
        json_users.append(json_user)
    
    # Save users data
    with open('skillforge_test_users.json', 'w', encoding='utf-8') as f:
        json.dump(json_users, f, indent=2, ensure_ascii=False)
    
    # Save companies data
    with open('skillforge_test_companies.json', 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] SkillForge test data saved:")
    print(f"   - skillforge_test_users.json ({len(json_users)} users)")
    print(f"   - skillforge_test_companies.json ({len(companies)} companies)")

def generate_api_commands():
    """Generate API commands for SkillForge AI testing"""
    
    print(f"\n[API] API Commands for SkillForge AI Testing:")
    print("=" * 60)
    
    for i, user_data in enumerate(SKILLFORGE_TEST_USERS, 1):
        # Prepare API data (remove non-API fields)
        api_data = user_data.copy()
        api_data['experience_level'] = user_data['experience_level'].value
        api_data.pop('role_context', None)
        api_data.pop('company_info', None)
        
        role_context = user_data['role_context']
        role_icon = {
            UserRole.ADMIN: "[ADMIN]",
            UserRole.COMPANY_CONTACT: "[COMPANY]", 
            UserRole.USER: "[USER]",
            UserRole.PREMIUM_USER: "[PREMIUM]",
            UserRole.MODERATOR: "[MOD]"
        }
        
        print(f"\n# {role_icon[role_context]} User {i}: {user_data['email']} ({role_context.value})")
        print("curl -X POST \"http://localhost:8000/api/v1/auth/register\" \\")
        print("  -H \"Content-Type: application/json\" \\")
        print(f"  -d '{json.dumps(api_data, ensure_ascii=False)}'")

def main():
    """Main function"""
    print("[TARGET] SkillForge AI - Correct Business Model Test Users")
    print("B2B2C Platform: Companies -> Projects -> Learners -> AI Evaluation")
    print("=" * 80)
    print("")
    
    # Validate users
    success, valid_users = asyncio.run(validate_skillforge_users())
    
    if success:
        print("\n[OK] All SkillForge AI test users are valid!")
        
        # Generate data files
        generate_skillforge_data()
        
        # Generate API commands
        generate_api_commands()
        
        print(f"\n[SUMMARY] SkillForge AI Business Model Summary:")
        print("-" * 50)
        print("[COMPANY] Companies create projects requiring specific skills")
        print("[USER] Learners work on real company projects")
        print("[AI] AI agents evaluate deliverables automatically")
        print("[DATA] Learners build validated skill portfolios")
        print("[TARGET] Companies identify and recruit top talents")
        
        print(f"\n[CREDENTIALS] Test Credentials Pattern:")
        print("- Company contacts: [Company]Pass123!")
        print("- Learners: [Role]Pass123!")
        print("- Platform staff: [Role]Pass123!")
        
        return True
    else:
        print("\n❌ Some SkillForge AI test users failed validation!")
        return False

if __name__ == "__main__":
    if main():
        print("\n[SUCCESS] SkillForge AI test users ready!")
        sys.exit(0)
    else:
        print("\n[FAILED] Validation failed!")
        sys.exit(1)