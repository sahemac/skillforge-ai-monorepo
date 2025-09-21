import { ValueObject } from '../../shared/value-object';

export class Email extends ValueObject {
  private readonly value: string;

  constructor(email: string) {
    super();
    
    if (!email) {
      throw new Error('Email cannot be empty');
    }

    if (!this.isValidEmail(email)) {
      throw new Error('Invalid email format');
    }

    this.value = email.toLowerCase().trim();
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  public toString(): string {
    return this.value;
  }

  public getValue(): string {
    return this.value;
  }

  protected getEqualityComponents(): any[] {
    return [this.value];
  }
}