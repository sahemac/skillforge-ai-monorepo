/**
 * Button component - A versatile button primitive with multiple variants
 * Built on top of Radix UI for accessibility and behavior
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Slot } from '@radix-ui/react-slot';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils';
import type { ButtonProps } from '../../types';

// Button variants using class-variance-authority
const buttonVariants = cva(
  [
    // Base styles
    'inline-flex items-center justify-center gap-2',
    'rounded-lg font-medium transition-all duration-200',
    'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'active:scale-[0.98]',
  ],
  {
    variants: {
      variant: {
        solid: 'shadow-sm hover:shadow-md',
        outline: 'border-2 bg-transparent hover:bg-opacity-5',
        ghost: 'hover:bg-opacity-10',
        link: 'underline-offset-4 hover:underline p-0 h-auto',
        soft: 'bg-opacity-10 hover:bg-opacity-20',
      },
      color: {
        primary: '',
        secondary: '',
        success: '',
        warning: '',
        error: '',
        info: '',
        neutral: '',
      },
      size: {
        xs: 'h-6 px-2 text-xs',
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
        xl: 'h-14 px-8 text-xl',
      },
      fullWidth: {
        true: 'w-full',
        false: 'w-auto',
      },
    },
    compoundVariants: [
      // Primary solid
      {
        variant: 'solid',
        color: 'primary',
        className: 'bg-primary-500 text-white hover:bg-primary-600 focus-visible:outline-primary-500',
      },
      {
        variant: 'outline',
        color: 'primary',
        className: 'border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white focus-visible:outline-primary-500',
      },
      {
        variant: 'ghost',
        color: 'primary',
        className: 'text-primary-500 hover:bg-primary-500 focus-visible:outline-primary-500',
      },
      {
        variant: 'link',
        color: 'primary',
        className: 'text-primary-500 hover:text-primary-600 focus-visible:outline-primary-500',
      },
      {
        variant: 'soft',
        color: 'primary',
        className: 'bg-primary-500 text-primary-700 hover:bg-primary-500 focus-visible:outline-primary-500',
      },

      // Secondary variants
      {
        variant: 'solid',
        color: 'secondary',
        className: 'bg-secondary-500 text-white hover:bg-secondary-600 focus-visible:outline-secondary-500',
      },
      {
        variant: 'outline',
        color: 'secondary',
        className: 'border-secondary-500 text-secondary-500 hover:bg-secondary-500 hover:text-white focus-visible:outline-secondary-500',
      },

      // Success variants
      {
        variant: 'solid',
        color: 'success',
        className: 'bg-success-500 text-white hover:bg-success-600 focus-visible:outline-success-500',
      },
      {
        variant: 'outline',
        color: 'success',
        className: 'border-success-500 text-success-500 hover:bg-success-500 hover:text-white focus-visible:outline-success-500',
      },

      // Warning variants
      {
        variant: 'solid',
        color: 'warning',
        className: 'bg-warning-500 text-white hover:bg-warning-600 focus-visible:outline-warning-500',
      },
      {
        variant: 'outline',
        color: 'warning',
        className: 'border-warning-500 text-warning-500 hover:bg-warning-500 hover:text-white focus-visible:outline-warning-500',
      },

      // Error variants
      {
        variant: 'solid',
        color: 'error',
        className: 'bg-error-500 text-white hover:bg-error-600 focus-visible:outline-error-500',
      },
      {
        variant: 'outline',
        color: 'error',
        className: 'border-error-500 text-error-500 hover:bg-error-500 hover:text-white focus-visible:outline-error-500',
      },

      // Neutral variants
      {
        variant: 'solid',
        color: 'neutral',
        className: 'bg-neutral-900 text-white hover:bg-neutral-800 focus-visible:outline-neutral-500',
      },
      {
        variant: 'outline',
        color: 'neutral',
        className: 'border-neutral-300 text-neutral-700 hover:bg-neutral-50 focus-visible:outline-neutral-500',
      },
      {
        variant: 'ghost',
        color: 'neutral',
        className: 'text-neutral-700 hover:bg-neutral-100 focus-visible:outline-neutral-500',
      },
    ],
    defaultVariants: {
      variant: 'solid',
      color: 'primary',
      size: 'md',
      fullWidth: false,
    },
  }
);

interface BaseButtonProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'color' | 'disabled'>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean;
}

/**
 * Button component with support for multiple variants, sizes, and states
 */
export const Button = React.forwardRef<HTMLButtonElement, BaseButtonProps>(
  (
    {
      className,
      variant,
      color,
      size,
      fullWidth,
      asChild = false,
      isLoading = false,
      loadingText,
      leftIcon,
      rightIcon,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';
    const isDisabled = disabled || isLoading;

    return (
      <Comp
        className={cn(buttonVariants({ variant, color, size, fullWidth, className }))}
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        {...props}
      >
        {isLoading && (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        )}
        {!isLoading && leftIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {leftIcon}
          </span>
        )}
        <span>{isLoading && loadingText ? loadingText : children}</span>
        {!isLoading && rightIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

// Export types for external use
export type ButtonVariants = VariantProps<typeof buttonVariants>;
export type { BaseButtonProps as ButtonProps };