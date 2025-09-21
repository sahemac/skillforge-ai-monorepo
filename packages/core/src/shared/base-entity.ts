/**
 * Base Entity class following DDD patterns
 * Provides common functionality for all domain entities
 */
export abstract class BaseEntity<T> {
  protected readonly _id: T;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(id: T, createdAt?: Date) {
    this._id = id;
    this._createdAt = createdAt || new Date();
    this._updatedAt = this._createdAt;
  }

  get id(): T {
    return this._id;
  }

  get createdAt(): Date {
    return this._createdAt;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  protected touch(): void {
    this._updatedAt = new Date();
  }

  public equals(other: BaseEntity<T>): boolean {
    if (this === other) return true;
    if (!(other instanceof BaseEntity)) return false;
    return this._id === other._id;
  }

  public toJSON(): Record<string, any> {
    return {
      id: this._id,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}