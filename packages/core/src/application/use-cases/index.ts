// This file exports use cases as they are added
// For now, this is a placeholder to maintain Clean Architecture structure

// Base use case interface that all use cases should implement
export interface BaseUseCase<TInput = any, TOutput = any> {
  execute(input: TInput): Promise<TOutput> | TOutput;
}

// Placeholder exports to make this a proper TypeScript module
export const APPLICATION_USE_CASES = {
  version: '1.0.0',
  type: 'application-use-cases'
} as const;

export type ApplicationUseCasesType = typeof APPLICATION_USE_CASES;