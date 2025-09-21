/**
 * Badge component - Small status and labeling component
 * Supports various colors, sizes, and visual styles
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils';

// Badge variants
const badgeVariants = cva(
  [
    // Base styles
    'inline-flex items-center gap-1 font-medium transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
  ],
  {
    variants: {
      variant: {
        solid: 'text-white shadow-sm',
        outline: 'border-2 bg-transparent',
        soft: 'bg-opacity-10',
        dot: 'pl-0',
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
        xs: 'px-1.5 py-0.5 text-xs rounded',
        sm: 'px-2 py-1 text-xs rounded-md',
        md: 'px-2.5 py-1 text-sm rounded-md',
        lg: 'px-3 py-1.5 text-sm rounded-lg',
      },
      shape: {
        rounded: '',
        pill: 'rounded-full',
      },
    },
    compoundVariants: [
      // Primary variants
      {
        variant: 'solid',
        color: 'primary',
        className: 'bg-primary-500 hover:bg-primary-600',
      },
      {
        variant: 'outline',
        color: 'primary',
        className: 'border-primary-500 text-primary-500 hover:bg-primary-50',
      },
      {
        variant: 'soft',
        color: 'primary',
        className: 'bg-primary-500 text-primary-700 hover:bg-primary-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'primary',
        className: 'text-primary-700',
      },

      // Secondary variants
      {
        variant: 'solid',
        color: 'secondary',
        className: 'bg-secondary-500 hover:bg-secondary-600',
      },
      {
        variant: 'outline',
        color: 'secondary',
        className: 'border-secondary-500 text-secondary-500 hover:bg-secondary-50',
      },
      {
        variant: 'soft',
        color: 'secondary',
        className: 'bg-secondary-500 text-secondary-700 hover:bg-secondary-600 hover:bg-opacity-20',
      },

      // Success variants
      {
        variant: 'solid',
        color: 'success',
        className: 'bg-success-500 hover:bg-success-600',
      },
      {
        variant: 'outline',
        color: 'success',
        className: 'border-success-500 text-success-500 hover:bg-success-50',
      },
      {
        variant: 'soft',
        color: 'success',
        className: 'bg-success-500 text-success-700 hover:bg-success-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'success',
        className: 'text-success-700',
      },

      // Warning variants
      {
        variant: 'solid',
        color: 'warning',
        className: 'bg-warning-500 hover:bg-warning-600',
      },
      {
        variant: 'outline',
        color: 'warning',
        className: 'border-warning-500 text-warning-500 hover:bg-warning-50',
      },
      {
        variant: 'soft',
        color: 'warning',
        className: 'bg-warning-500 text-warning-700 hover:bg-warning-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'warning',
        className: 'text-warning-700',
      },

      // Error variants
      {
        variant: 'solid',
        color: 'error',
        className: 'bg-error-500 hover:bg-error-600',
      },
      {
        variant: 'outline',
        color: 'error',
        className: 'border-error-500 text-error-500 hover:bg-error-50',
      },
      {
        variant: 'soft',
        color: 'error',
        className: 'bg-error-500 text-error-700 hover:bg-error-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'error',
        className: 'text-error-700',
      },

      // Info variants
      {
        variant: 'solid',
        color: 'info',
        className: 'bg-info-500 hover:bg-info-600',
      },
      {
        variant: 'outline',
        color: 'info',
        className: 'border-info-500 text-info-500 hover:bg-info-50',
      },
      {
        variant: 'soft',
        color: 'info',
        className: 'bg-info-500 text-info-700 hover:bg-info-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'info',
        className: 'text-info-700',
      },

      // Neutral variants
      {
        variant: 'solid',
        color: 'neutral',
        className: 'bg-neutral-500 hover:bg-neutral-600',
      },
      {
        variant: 'outline',
        color: 'neutral',
        className: 'border-neutral-300 text-neutral-600 hover:bg-neutral-50',
      },
      {
        variant: 'soft',
        color: 'neutral',
        className: 'bg-neutral-500 text-neutral-700 hover:bg-neutral-600 hover:bg-opacity-20',
      },
      {
        variant: 'dot',
        color: 'neutral',
        className: 'text-neutral-700',
      },

      // Dot variant padding adjustments
      {
        variant: 'dot',
        size: 'xs',
        className: 'pl-0 pr-1.5',
      },
      {
        variant: 'dot',
        size: 'sm',
        className: 'pl-0 pr-2',
      },
      {
        variant: 'dot',
        size: 'md',
        className: 'pl-0 pr-2.5',
      },
      {
        variant: 'dot',
        size: 'lg',
        className: 'pl-0 pr-3',
      },
    ],
    defaultVariants: {
      variant: 'solid',
      color: 'primary',
      size: 'md',
      shape: 'rounded',
    },
  }
);

// Dot indicator variants
const dotVariants = cva(
  'rounded-full',
  {
    variants: {
      size: {
        xs: 'h-1.5 w-1.5',
        sm: 'h-2 w-2',
        md: 'h-2 w-2',
        lg: 'h-2.5 w-2.5',
      },
      color: {
        primary: 'bg-primary-500',
        secondary: 'bg-secondary-500',
        success: 'bg-success-500',
        warning: 'bg-warning-500',
        error: 'bg-error-500',
        info: 'bg-info-500',
        neutral: 'bg-neutral-500',
      },
      ping: {
        true: 'animate-ping',
        false: '',
      },
    },
    defaultVariants: {
      size: 'md',
      color: 'primary',
      ping: false,
    },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
  ping?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  closable?: boolean;
  onClose?: () => void;
}

/**
 * Badge component with various styles and optional dot indicator
 */
export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  (
    {
      className,
      variant,
      color,
      size,
      shape,
      dot,
      ping,
      leftIcon,
      rightIcon,
      closable,
      onClose,
      children,
      ...props
    },
    ref
  ) => {
    const badgeVariant = dot ? 'dot' : variant;

    return (
      <div
        ref={ref}
        className={cn(
          badgeVariants({
            variant: badgeVariant,
            color,
            size,
            shape,
          }),
          className
        )}
        {...props}
      >
        {dot && (
          <div
            className={cn(
              dotVariants({
                size,
                color,
                ping,
              })
            )}
          />
        )}
        
        {leftIcon && !dot && (
          <span className="flex-shrink-0" aria-hidden="true">
            {leftIcon}
          </span>
        )}
        
        {children && <span>{children}</span>}
        
        {rightIcon && !closable && (
          <span className="flex-shrink-0" aria-hidden="true">
            {rightIcon}
          </span>
        )}
        
        {closable && (
          <button
            type="button"
            onClick={onClose}
            className="ml-1 flex-shrink-0 rounded-full p-0.5 hover:bg-black hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-1"
            aria-label="Remove badge"
          >
            <svg
              className="h-3 w-3"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        )}
      </div>
    );
  }
);

Badge.displayName = 'Badge';

/**
 * Notification Badge - Shows count with optional max value
 */
export const NotificationBadge = React.forwardRef<
  HTMLDivElement,
  Omit<BadgeProps, 'children'> & {
    count: number;
    max?: number;
    showZero?: boolean;
  }
>(
  (
    {
      count,
      max = 99,
      showZero = false,
      className,
      ...props
    },
    ref
  ) => {
    if (count === 0 && !showZero) {
      return null;
    }

    const displayCount = count > max ? `${max}+` : count.toString();

    return (
      <Badge
        ref={ref}
        size="xs"
        shape="pill"
        className={cn('min-w-[1.25rem] justify-center px-1', className)}
        {...props}
      >
        {displayCount}
      </Badge>
    );
  }
);

NotificationBadge.displayName = 'NotificationBadge';

/**
 * Status Badge - Predefined badges for common statuses
 */
interface StatusBadgeProps extends Omit<BadgeProps, 'color' | 'children'> {
  status: 'active' | 'inactive' | 'pending' | 'success' | 'error' | 'warning';
}

export const StatusBadge = React.forwardRef<HTMLDivElement, StatusBadgeProps>(
  ({ status, ...props }, ref) => {
    const statusConfig = {
      active: { color: 'success' as const, text: 'Active' },
      inactive: { color: 'neutral' as const, text: 'Inactive' },
      pending: { color: 'warning' as const, text: 'Pending' },
      success: { color: 'success' as const, text: 'Success' },
      error: { color: 'error' as const, text: 'Error' },
      warning: { color: 'warning' as const, text: 'Warning' },
    };

    const config = statusConfig[status];

    return (
      <Badge ref={ref} color={config.color} {...props}>
        {config.text}
      </Badge>
    );
  }
);

StatusBadge.displayName = 'StatusBadge';

/**
 * Priority Badge - For task/issue priority levels
 */
interface PriorityBadgeProps extends Omit<BadgeProps, 'color' | 'children'> {
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export const PriorityBadge = React.forwardRef<HTMLDivElement, PriorityBadgeProps>(
  ({ priority, ...props }, ref) => {
    const priorityConfig = {
      low: { color: 'neutral' as const, text: 'Low' },
      medium: { color: 'info' as const, text: 'Medium' },
      high: { color: 'warning' as const, text: 'High' },
      urgent: { color: 'error' as const, text: 'Urgent' },
    };

    const config = priorityConfig[priority];

    return (
      <Badge ref={ref} color={config.color} {...props}>
        {config.text}
      </Badge>
    );
  }
);

PriorityBadge.displayName = 'PriorityBadge';

// Export types
export type BadgeVariants = VariantProps<typeof badgeVariants>;