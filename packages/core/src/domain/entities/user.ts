import { BaseEntity } from '../../shared/base-entity';
import { Email } from '../value-objects/email';

export enum UserRole {
  ADMIN = 'admin',
  COMPANY = 'company',
  LEARNER = 'learner'
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING_VERIFICATION = 'pending_verification'
}

export interface UserProps {
  email: Email;
  firstName: string;
  lastName: string;
  role: UserRole;
  status: UserStatus;
  profilePicture?: string;
  lastLoginAt?: Date;
}

export class User extends BaseEntity<string> {
  private _email: Email;
  private _firstName: string;
  private _lastName: string;
  private _role: UserRole;
  private _status: UserStatus;
  private _profilePicture?: string;
  private _lastLoginAt?: Date;

  constructor(id: string, props: UserProps, createdAt?: Date) {
    super(id, createdAt);
    
    this._email = props.email;
    this._firstName = props.firstName;
    this._lastName = props.lastName;
    this._role = props.role;
    this._status = props.status;
    this._profilePicture = props.profilePicture;
    this._lastLoginAt = props.lastLoginAt;
  }

  // Getters
  get email(): Email {
    return this._email;
  }

  get firstName(): string {
    return this._firstName;
  }

  get lastName(): string {
    return this._lastName;
  }

  get fullName(): string {
    return `${this._firstName} ${this._lastName}`;
  }

  get role(): UserRole {
    return this._role;
  }

  get status(): UserStatus {
    return this._status;
  }

  get profilePicture(): string | undefined {
    return this._profilePicture;
  }

  get lastLoginAt(): Date | undefined {
    return this._lastLoginAt;
  }

  // Business methods
  public updateProfile(firstName: string, lastName: string, profilePicture?: string): void {
    this._firstName = firstName;
    this._lastName = lastName;
    this._profilePicture = profilePicture;
    this.touch();
  }

  public changeEmail(newEmail: Email): void {
    this._email = newEmail;
    this._status = UserStatus.PENDING_VERIFICATION;
    this.touch();
  }

  public activate(): void {
    if (this._status === UserStatus.SUSPENDED) {
      throw new Error('Cannot activate a suspended user');
    }
    this._status = UserStatus.ACTIVE;
    this.touch();
  }

  public suspend(): void {
    this._status = UserStatus.SUSPENDED;
    this.touch();
  }

  public recordLogin(): void {
    this._lastLoginAt = new Date();
    this.touch();
  }

  public isActive(): boolean {
    return this._status === UserStatus.ACTIVE;
  }

  public isAdmin(): boolean {
    return this._role === UserRole.ADMIN;
  }

  public isCompany(): boolean {
    return this._role === UserRole.COMPANY;
  }

  public isLearner(): boolean {
    return this._role === UserRole.LEARNER;
  }

  public toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      email: this._email.getValue(),
      firstName: this._firstName,
      lastName: this._lastName,
      fullName: this.fullName,
      role: this._role,
      status: this._status,
      profilePicture: this._profilePicture,
      lastLoginAt: this._lastLoginAt,
    };
  }
}