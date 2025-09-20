"""
Email utilities for SkillForge AI User Service
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

from app.core.config import get_settings
from fastapi import Request

logger = logging.getLogger(__name__)
settings = get_settings()

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailService:
    """Email service for sending multilingual emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.from_email = settings.EMAILS_FROM_EMAIL or "sah@emacsah.com"
        self.from_name = settings.EMAILS_FROM_NAME or "SkillForge AI"
        
        # Supported languages with French as default
        self.supported_languages = ["fr", "en"]
        self.default_language = "fr"
        
        # Setup Jinja2 environment for multilingual email templates
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR))
            )
            # Verify language directories exist
            for lang in self.supported_languages:
                lang_dir = TEMPLATES_DIR / lang
                if not lang_dir.exists():
                    logger.warning(f"Language directory {lang} not found in templates")
        except Exception:
            # If templates directory doesn't exist, use string templates
            self.jinja_env = None
            logger.warning("Email templates directory not found, using fallback templates")
    
    def _get_smtp_connection(self):
        """Get SMTP connection."""
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            raise ValueError("SMTP configuration is incomplete")
        
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_tls:
                server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            raise
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    # This would be implemented based on attachment requirements
                    pass
            
            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def detect_language(self, request: Optional[Request] = None, accept_language: Optional[str] = None) -> str:
        """Detect user's preferred language from HTTP headers."""
        try:
            # Use accept_language parameter if provided
            if accept_language:
                lang_header = accept_language
            # Extract from request if available
            elif request and hasattr(request, 'headers'):
                lang_header = request.headers.get('Accept-Language', '')
            else:
                return self.default_language
            
            # Parse Accept-Language header (e.g., "fr-FR,fr;q=0.9,en;q=0.8")
            if lang_header:
                # Extract language codes and their quality values
                languages = []
                for lang_part in lang_header.split(','):
                    lang_part = lang_part.strip()
                    if ';q=' in lang_part:
                        lang, quality = lang_part.split(';q=')
                        quality = float(quality)
                    else:
                        lang, quality = lang_part, 1.0
                    
                    # Extract primary language code (e.g., "fr" from "fr-FR")
                    primary_lang = lang.split('-')[0].lower()
                    languages.append((primary_lang, quality))
                
                # Sort by quality and find first supported language
                languages.sort(key=lambda x: x[1], reverse=True)
                for lang_code, _ in languages:
                    if lang_code in self.supported_languages:
                        return lang_code
            
            return self.default_language
            
        except Exception as e:
            logger.warning(f"Failed to detect language from headers: {str(e)}")
            return self.default_language
    
    def render_template(self, template_name: str, language: str = None, **kwargs) -> str:
        """Render multilingual email template."""
        if language is None:
            language = self.default_language
        
        # Ensure language is supported, fallback to French if not
        if language not in self.supported_languages:
            language = self.default_language
            
        if self.jinja_env:
            try:
                # Try to get language-specific template
                lang_template_path = f"{language}/{template_name}"
                template = self.jinja_env.get_template(lang_template_path)
                return template.render(**kwargs)
            except Exception as e:
                logger.warning(f"Failed to render template {lang_template_path}: {str(e)}")
                # Fallback to default language if specific language fails
                if language != self.default_language:
                    try:
                        fallback_template_path = f"{self.default_language}/{template_name}"
                        template = self.jinja_env.get_template(fallback_template_path)
                        return template.render(**kwargs)
                    except Exception as fallback_e:
                        logger.error(f"Failed to render fallback template {fallback_template_path}: {str(fallback_e)}")
                
                return self._get_fallback_template(template_name, language, **kwargs)
        else:
            return self._get_fallback_template(template_name, language, **kwargs)
    
    def _get_fallback_template(self, template_name: str, language: str = None, **kwargs) -> str:
        """Get fallback template if Jinja2 templates are not available."""
        if language is None:
            language = self.default_language
            
        # French templates (default)
        fr_templates = {
            "verification_email.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Bienvenue sur SkillForge AI !</h2>
                <p>Bonjour {kwargs.get('first_name', '')},</p>
                <p>Veuillez cliquer sur le lien ci-dessous pour vérifier votre adresse email :</p>
                <p><a href="{kwargs.get('verification_url', '#')}">Vérifier mon email</a></p>
                <p>Ce lien expirera dans 24 heures.</p>
                <p>Si vous n'avez pas créé ce compte, ignorez cet email.</p>
                <p>Cordialement,<br>L'équipe SkillForge AI</p>
            </body>
            </html>
            """,
            "password_reset.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Demande de réinitialisation du mot de passe</h2>
                <p>Bonjour {kwargs.get('first_name', '')},</p>
                <p>Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous :</p>
                <p><a href="{kwargs.get('reset_url', '#')}">Réinitialiser le mot de passe</a></p>
                <p>Ce lien expirera dans 1 heure.</p>
                <p>Si vous n'avez pas fait cette demande, ignorez cet email.</p>
                <p>Cordialement,<br>L'équipe SkillForge AI</p>
            </body>
            </html>
            """,
            "team_invitation.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Invitation à rejoindre une équipe</h2>
                <p>Bonjour {kwargs.get('first_name', '')},</p>
                <p>Vous avez été invité(e) à rejoindre <strong>{kwargs.get('company_name', 'une entreprise')}</strong> sur SkillForge AI.</p>
                <p>Message : {kwargs.get('message', 'Aucun message fourni.')}</p>
                <p><a href="{kwargs.get('invitation_url', '#')}">Accepter l'invitation</a></p>
                <p>Cordialement,<br>L'équipe SkillForge AI</p>
            </body>
            </html>
            """
        }
        
        # English templates
        en_templates = {
            "verification_email.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Welcome to SkillForge AI!</h2>
                <p>Hi {kwargs.get('first_name', '')},</p>
                <p>Please click the link below to verify your email address:</p>
                <p><a href="{kwargs.get('verification_url', '#')}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
                <p>Best regards,<br>The SkillForge AI Team</p>
            </body>
            </html>
            """,
            "password_reset.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hi {kwargs.get('first_name', '')},</p>
                <p>You requested to reset your password. Click the link below:</p>
                <p><a href="{kwargs.get('reset_url', '#')}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>Best regards,<br>The SkillForge AI Team</p>
            </body>
            </html>
            """,
            "team_invitation.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Team Invitation</h2>
                <p>Hi {kwargs.get('first_name', '')},</p>
                <p>You've been invited to join <strong>{kwargs.get('company_name', 'a company')}</strong> on SkillForge AI.</p>
                <p>Message: {kwargs.get('message', 'No message provided.')}</p>
                <p><a href="{kwargs.get('invitation_url', '#')}">Accept Invitation</a></p>
                <p>Best regards,<br>The SkillForge AI Team</p>
            </body>
            </html>
            """
        }
        
        # Select templates based on language
        templates = fr_templates if language == "fr" else en_templates
        fallback_templates = fr_templates  # Always fallback to French
        
        # Try to get template in requested language, fallback to French
        template_content = templates.get(template_name) or fallback_templates.get(template_name)
        return template_content or f"<p>Email template for {template_name} not found.</p>"


# Global email service instance
email_service = EmailService()


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """Send email using global email service."""
    return email_service.send_email(to_email, subject, html_content, text_content)


def send_verification_email(
    to_email: str,
    first_name: str,
    verification_token: str,
    request: Optional[Request] = None,
    language: Optional[str] = None
) -> bool:
    """Send email verification email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        verification_url = f"{base_url}/verify-email?token={verification_token}"
        
        # Detect language or use provided language
        if language is None:
            language = email_service.detect_language(request)
        
        # Multilingual subjects
        subjects = {
            "fr": "Vérification de votre compte SkillForge AI",
            "en": "Verify your SkillForge AI account"
        }
        subject = subjects.get(language, subjects["fr"])
        
        html_content = email_service.render_template(
            "verification_email.html",
            language=language,
            first_name=first_name,
            verification_url=verification_url
        )
        
        # Multilingual text content
        if language == "fr":
            text_content = f"""
            Bonjour {first_name},
            
            Bienvenue sur SkillForge AI !
            
            Veuillez visiter l'URL suivante pour vérifier votre adresse email :
            {verification_url}
            
            Ce lien expirera dans 24 heures.
            
            Si vous n'avez pas créé ce compte, ignorez cet email.
            
            Cordialement,
            L'équipe SkillForge AI
            """
        else:
            text_content = f"""
            Hi {first_name},
            
            Welcome to SkillForge AI!
            
            Please visit the following URL to verify your email address:
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            The SkillForge AI Team
            """
        
        return email_service.send_email(to_email, subject, html_content, text_content)
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        return False


def send_password_reset_email(
    to_email: str,
    first_name: str,
    reset_token: str,
    request: Optional[Request] = None,
    language: Optional[str] = None
) -> bool:
    """Send password reset email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        reset_url = f"{base_url}/reset-password?token={reset_token}"
        
        # Detect language or use provided language
        if language is None:
            language = email_service.detect_language(request)
        
        # Multilingual subjects
        subjects = {
            "fr": "Réinitialisation de votre mot de passe - SkillForge AI",
            "en": "Reset your SkillForge AI password"
        }
        subject = subjects.get(language, subjects["fr"])
        
        html_content = email_service.render_template(
            "password_reset.html",
            language=language,
            first_name=first_name,
            reset_url=reset_url
        )
        
        # Multilingual text content
        if language == "fr":
            text_content = f"""
            Bonjour {first_name},
            
            Vous avez demandé à réinitialiser votre mot de passe SkillForge AI.
            
            Veuillez visiter l'URL suivante pour réinitialiser votre mot de passe :
            {reset_url}
            
            Ce lien expirera dans 1 heure.
            
            Si vous n'avez pas fait cette demande, ignorez cet email.
            
            Cordialement,
            L'équipe SkillForge AI
            """
        else:
            text_content = f"""
            Hi {first_name},
            
            You requested to reset your SkillForge AI password.
            
            Please visit the following URL to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            The SkillForge AI Team
            """
        
        return email_service.send_email(to_email, subject, html_content, text_content)
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return False


def send_team_invitation_email(
    to_email: str,
    first_name: str,
    company_name: str,
    message: Optional[str] = None,
    request: Optional[Request] = None,
    language: Optional[str] = None
) -> bool:
    """Send team invitation email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        invitation_url = f"{base_url}/team-invitation"
        
        # Detect language or use provided language
        if language is None:
            language = email_service.detect_language(request)
        
        # Multilingual subjects and default messages
        if language == "fr":
            subject = f"Invitation à rejoindre {company_name} - SkillForge AI"
            default_message = "Vous avez été invité(e) à rejoindre l'équipe !"
        else:
            subject = f"Invitation to join {company_name} on SkillForge AI"
            default_message = "You've been invited to join the team!"
        
        html_content = email_service.render_template(
            "team_invitation.html",
            language=language,
            first_name=first_name,
            company_name=company_name,
            message=message or default_message,
            invitation_url=invitation_url
        )
        
        # Multilingual text content
        if language == "fr":
            default_msg = "Vous avez été invité(e) à rejoindre l'équipe !"
            text_content = f"""
            Bonjour {first_name},
            
            Vous avez été invité(e) à rejoindre {company_name} sur SkillForge AI.
            
            Message : {message or default_msg}
            
            Veuillez visiter l'URL suivante pour accepter l'invitation :
            {invitation_url}
            
            Cordialement,
            L'équipe SkillForge AI
            """
        else:
            default_msg = "You've been invited to join the team!"
            text_content = f"""
            Hi {first_name},
            
            You've been invited to join {company_name} on SkillForge AI.
            
            Message: {message or default_msg}
            
            Please visit the following URL to accept the invitation:
            {invitation_url}
            
            Best regards,
            The SkillForge AI Team
            """
        
        return email_service.send_email(to_email, subject, html_content, text_content)
        
    except Exception as e:
        logger.error(f"Failed to send team invitation email: {str(e)}")
        return False


def send_welcome_email(to_email: str, first_name: str) -> bool:
    """Send welcome email to new users."""
    try:
        subject = "Welcome to SkillForge AI!"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Welcome to SkillForge AI!</h2>
            <p>Hi {first_name},</p>
            <p>Welcome to SkillForge AI! We're excited to have you join our community.</p>
            <p>Here are some things you can do to get started:</p>
            <ul>
                <li>Complete your profile</li>
                <li>Add your skills and interests</li>
                <li>Explore learning opportunities</li>
                <li>Connect with companies</li>
            </ul>
            <p>If you have any questions, feel free to contact our support team.</p>
            <p>Best regards,<br>The SkillForge AI Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {first_name},
        
        Welcome to SkillForge AI! We're excited to have you join our community.
        
        Here are some things you can do to get started:
        - Complete your profile
        - Add your skills and interests
        - Explore learning opportunities
        - Connect with companies
        
        If you have any questions, feel free to contact our support team.
        
        Best regards,
        The SkillForge AI Team
        """
        
        return email_service.send_email(to_email, subject, html_content, text_content)
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False