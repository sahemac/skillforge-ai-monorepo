// This file exports repository interfaces as they are added
// For now, this is a placeholder to maintain Clean Architecture structure

// Base repository interface that all repositories should extend
export interface BaseRepository<TEntity, TId = string> {
  findById(id: TId): Promise<TEntity | null>;
  save(entity: TEntity): Promise<TEntity>;
  delete(id: TId): Promise<void>;
}

// Placeholder exports to make this a proper TypeScript module
export const DOMAIN_REPOSITORIES = {
  version: '1.0.0',
  type: 'domain-repositories'
} as const;

export type DomainRepositoriesType = typeof DOMAIN_REPOSITORIES;