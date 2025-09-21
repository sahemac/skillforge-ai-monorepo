/**
 * Input component - A versatile input field with multiple variants and states
 * Supports various input types, icons, and form integration
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';
import { cn } from '../../utils';
import type { InputProps } from '../../types';

// Input variants
const inputVariants = cva(
  [
    // Base styles
    'flex w-full rounded-lg border px-3 py-2 text-sm transition-all duration-200',
    'placeholder:text-neutral-500',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
    'file:border-0 file:bg-transparent file:text-sm file:font-medium',
  ],
  {
    variants: {
      variant: {
        default: 'border-neutral-300 bg-white focus:border-primary-500 focus:ring-primary-500',
        filled: 'border-transparent bg-neutral-100 focus:bg-white focus:border-primary-500 focus:ring-primary-500',
        flushed: 'border-0 border-b-2 border-neutral-300 rounded-none px-0 focus:border-primary-500 focus:ring-0 focus:ring-offset-0',
      },
      size: {
        xs: 'h-6 px-2 text-xs',
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-3 text-base',
        lg: 'h-12 px-4 text-lg',
        xl: 'h-14 px-4 text-xl',
      },
      state: {
        default: '',
        error: 'border-error-500 focus:border-error-500 focus:ring-error-500',
        success: 'border-success-500 focus:border-success-500 focus:ring-success-500',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      state: 'default',
    },
  }
);

// Container for input with icons
const inputContainerVariants = cva(
  'relative flex items-center',
  {
    variants: {
      size: {
        xs: 'text-xs',
        sm: 'text-sm',
        md: 'text-base',
        lg: 'text-lg',
        xl: 'text-xl',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

interface BaseInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size' | 'color'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  description?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  isLoading?: boolean;
  allowClear?: boolean;
  onClear?: () => void;
}

/**
 * Input component with support for various types, icons, and validation states
 */
export const Input = React.forwardRef<HTMLInputElement, BaseInputProps>(
  (
    {
      className,
      variant,
      size,
      state,
      type = 'text',
      label,
      description,
      error,
      leftIcon,
      rightIcon,
      isLoading,
      allowClear,
      onClear,
      disabled,
      value,
      id,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const [internalValue, setInternalValue] = React.useState(value || '');
    const inputId = id || React.useId();
    const descriptionId = `${inputId}-description`;
    const errorId = `${inputId}-error`;

    // Handle controlled/uncontrolled state
    const inputValue = value !== undefined ? value : internalValue;
    const isPasswordType = type === 'password';
    const inputType = isPasswordType && showPassword ? 'text' : type;
    
    // Determine the current state based on error
    const currentState = error ? 'error' : state;
    
    // Handle password visibility toggle
    const togglePasswordVisibility = () => {
      setShowPassword(!showPassword);
    };

    // Handle clear functionality
    const handleClear = () => {
      if (value === undefined) {
        setInternalValue('');
      }
      onClear?.();
    };

    // Handle input change
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (value === undefined) {
        setInternalValue(e.target.value);
      }
      props.onChange?.(e);
    };

    const showClearButton = allowClear && inputValue && !disabled;
    const showPasswordToggle = isPasswordType && !disabled;
    const hasRightContent = rightIcon || showClearButton || showPasswordToggle || isLoading;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-2 block text-sm font-medium text-neutral-700"
          >
            {label}
            {props.required && (
              <span className="ml-1 text-error-500" aria-label="required">
                *
              </span>
            )}
          </label>
        )}

        <div className={cn(inputContainerVariants({ size }))}>
          {leftIcon && (
            <div className="absolute left-3 z-10 flex items-center text-neutral-500">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            type={inputType}
            value={inputValue}
            onChange={handleChange}
            disabled={disabled || isLoading}
            aria-describedby={cn(
              description && descriptionId,
              error && errorId
            )}
            aria-invalid={!!error}
            className={cn(
              inputVariants({ variant, size, state: currentState }),
              leftIcon && 'pl-10',
              hasRightContent && 'pr-10',
              className
            )}
            {...props}
          />

          {hasRightContent && (
            <div className="absolute right-3 z-10 flex items-center gap-1 text-neutral-500">
              {isLoading && (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
              )}
              
              {showClearButton && !isLoading && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="flex h-4 w-4 items-center justify-center rounded-full hover:bg-neutral-200"
                  aria-label="Clear input"
                >
                  ×
                </button>
              )}

              {showPasswordToggle && !isLoading && (
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="flex h-4 w-4 items-center justify-center rounded-full hover:bg-neutral-200"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              )}

              {rightIcon && !isLoading && !showClearButton && !showPasswordToggle && (
                <div>{rightIcon}</div>
              )}
            </div>
          )}
        </div>

        {description && !error && (
          <p id={descriptionId} className="mt-1 text-xs text-neutral-600">
            {description}
          </p>
        )}

        {error && (
          <p
            id={errorId}
            className="mt-1 flex items-center gap-1 text-xs text-error-600"
            role="alert"
          >
            <AlertCircle size={12} />
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Specialized input components
export const PasswordInput = React.forwardRef<
  HTMLInputElement,
  Omit<BaseInputProps, 'type'>
>((props, ref) => <Input ref={ref} type="password" {...props} />);

PasswordInput.displayName = 'PasswordInput';

export const EmailInput = React.forwardRef<
  HTMLInputElement,
  Omit<BaseInputProps, 'type'>
>((props, ref) => <Input ref={ref} type="email" {...props} />);

EmailInput.displayName = 'EmailInput';

export const NumberInput = React.forwardRef<
  HTMLInputElement,
  Omit<BaseInputProps, 'type'>
>((props, ref) => <Input ref={ref} type="number" {...props} />);

NumberInput.displayName = 'NumberInput';

export const SearchInput = React.forwardRef<
  HTMLInputElement,
  Omit<BaseInputProps, 'type'>
>((props, ref) => <Input ref={ref} type="search" {...props} />);

SearchInput.displayName = 'SearchInput';

// Export types
export type InputVariants = VariantProps<typeof inputVariants>;
export type { BaseInputProps as InputComponentProps };