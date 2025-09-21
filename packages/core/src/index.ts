// Shared base classes
export { BaseEntity } from './shared/base-entity';
export { ValueObject } from './shared/value-object';

// Domain entities
export { User, UserRole, UserStatus } from './domain/entities/user';

// Value objects
export { Email } from './domain/value-objects/email';

// Domain repositories interfaces
export * from './domain/repositories';

// Application use cases
export * from './application/use-cases';

// Application ports
export * from './application/ports';