import { ValueObject } from '@skillforge-ai/core';

export class Password extends ValueObject {
  private readonly value: string;

  constructor(password: string) {
    super();
    
    if (!password) {
      throw new Error('Password cannot be empty');
    }

    this.validatePassword(password);
    this.value = password;
  }

  private validatePassword(password: string): void {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    const errors: string[] = [];

    if (password.length < minLength) {
      errors.push(`Password must be at least ${minLength} characters long`);
    }

    if (!hasUpperCase) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (!hasLowerCase) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (!hasNumbers) {
      errors.push('Password must contain at least one number');
    }

    if (!hasSpecialChar) {
      errors.push('Password must contain at least one special character');
    }

    if (errors.length > 0) {
      throw new Error(`Password validation failed: ${errors.join(', ')}`);
    }
  }

  public getValue(): string {
    return this.value;
  }

  public getStrength(): 'weak' | 'medium' | 'strong' {
    let score = 0;
    
    if (this.value.length >= 8) score++;
    if (this.value.length >= 12) score++;
    if (/[A-Z]/.test(this.value)) score++;
    if (/[a-z]/.test(this.value)) score++;
    if (/\d/.test(this.value)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(this.value)) score++;

    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
  }

  protected getEqualityComponents(): any[] {
    return [this.value];
  }
}