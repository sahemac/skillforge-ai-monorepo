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

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailService:
    """Email service for sending emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.EMAILS_FROM_NAME or "SkillForge AI"
        
        # Setup Jinja2 environment for email templates
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR))
            )
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
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render email template."""
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template(template_name)
                return template.render(**kwargs)
            except Exception as e:
                logger.error(f"Failed to render template {template_name}: {str(e)}")
                return self._get_fallback_template(template_name, **kwargs)
        else:
            return self._get_fallback_template(template_name, **kwargs)
    
    def _get_fallback_template(self, template_name: str, **kwargs) -> str:
        """Get fallback template if Jinja2 templates are not available."""
        templates = {
            "verification_email.html": f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Welcome to SkillForge AI!</h2>
                <p>Hi {kwargs.get('first_name', 'there')},</p>
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
                <p>Hi {kwargs.get('first_name', 'there')},</p>
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
                <p>Hi {kwargs.get('first_name', 'there')},</p>
                <p>You've been invited to join <strong>{kwargs.get('company_name', 'a company')}</strong> on SkillForge AI.</p>
                <p>Message: {kwargs.get('message', 'No message provided.')}</p>
                <p><a href="{kwargs.get('invitation_url', '#')}">Accept Invitation</a></p>
                <p>Best regards,<br>The SkillForge AI Team</p>
            </body>
            </html>
            """
        }
        
        return templates.get(template_name, f"<p>Email template for {template_name} not found.</p>")


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
    verification_token: str
) -> bool:
    """Send email verification email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        verification_url = f"{base_url}/verify-email?token={verification_token}"
        
        subject = "Verify your SkillForge AI account"
        html_content = email_service.render_template(
            "verification_email.html",
            first_name=first_name,
            verification_url=verification_url
        )
        
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
    reset_token: str
) -> bool:
    """Send password reset email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        reset_url = f"{base_url}/reset-password?token={reset_token}"
        
        subject = "Reset your SkillForge AI password"
        html_content = email_service.render_template(
            "password_reset.html",
            first_name=first_name,
            reset_url=reset_url
        )
        
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
    message: Optional[str] = None
) -> bool:
    """Send team invitation email."""
    try:
        base_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        invitation_url = f"{base_url}/team-invitation"
        
        subject = f"Invitation to join {company_name} on SkillForge AI"
        html_content = email_service.render_template(
            "team_invitation.html",
            first_name=first_name,
            company_name=company_name,
            message=message or "You've been invited to join the team!",
            invitation_url=invitation_url
        )
        
        text_content = f"""
        Hi {first_name},
        
        You've been invited to join {company_name} on SkillForge AI.
        
        Message: {message or "You've been invited to join the team!"}
        
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