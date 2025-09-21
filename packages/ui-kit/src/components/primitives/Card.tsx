/**
 * Card component - A flexible container component with various styles
 * Provides elevation, borders, and hover effects
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils';

// Card variants
const cardVariants = cva(
  [
    // Base styles
    'rounded-lg transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
  ],
  {
    variants: {
      variant: {
        elevated: 'bg-white shadow-md hover:shadow-lg',
        outlined: 'bg-white border border-neutral-200 hover:border-neutral-300',
        filled: 'bg-neutral-50 border border-neutral-100 hover:bg-neutral-100',
      },
      padding: {
        none: 'p-0',
        xs: 'p-2',
        sm: 'p-3',
        md: 'p-4',
        lg: 'p-6',
        xl: 'p-8',
      },
      hover: {
        true: 'cursor-pointer hover:scale-[1.02]',
        false: '',
      },
      clickable: {
        true: 'cursor-pointer active:scale-[0.98]',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'elevated',
      padding: 'md',
      hover: false,
      clickable: false,
    },
  }
);

interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  asChild?: boolean;
}

/**
 * Main Card component
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant,
      padding,
      hover,
      clickable,
      children,
      onClick,
      tabIndex,
      role,
      ...props
    },
    ref
  ) => {
    const isInteractive = clickable || onClick;
    const shouldHover = hover || isInteractive;

    return (
      <div
        ref={ref}
        className={cn(
          cardVariants({
            variant,
            padding,
            hover: shouldHover,
            clickable: isInteractive,
          }),
          className
        )}
        onClick={onClick}
        tabIndex={isInteractive ? tabIndex ?? 0 : tabIndex}
        role={isInteractive ? role ?? 'button' : role}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

/**
 * Card Header component
 */
export const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));

CardHeader.displayName = 'CardHeader';

/**
 * Card Title component
 */
export const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('font-semibold leading-none tracking-tight', className)}
    {...props}
  >
    {children}
  </h3>
));

CardTitle.displayName = 'CardTitle';

/**
 * Card Description component
 */
export const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-neutral-600', className)}
    {...props}
  />
));

CardDescription.displayName = 'CardDescription';

/**
 * Card Content component
 */
export const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));

CardContent.displayName = 'CardContent';

/**
 * Card Footer component
 */
export const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
));

CardFooter.displayName = 'CardFooter';

/**
 * Specialized Card variants for common use cases
 */

// Product Card
export const ProductCard = React.forwardRef<
  HTMLDivElement,
  CardProps & {
    image?: string;
    title?: string;
    description?: string;
    price?: string;
    onAddToCart?: () => void;
  }
>(
  (
    {
      image,
      title,
      description,
      price,
      onAddToCart,
      children,
      ...props
    },
    ref
  ) => (
    <Card ref={ref} hover clickable {...props}>
      {image && (
        <div className="aspect-square overflow-hidden rounded-t-lg">
          <img
            src={image}
            alt={title}
            className="h-full w-full object-cover transition-transform duration-200 hover:scale-105"
          />
        </div>
      )}
      <CardContent>
        {title && <CardTitle className="mb-2">{title}</CardTitle>}
        {description && (
          <CardDescription className="mb-4">{description}</CardDescription>
        )}
        {price && <p className="text-lg font-bold text-primary-600">{price}</p>}
        {children}
      </CardContent>
      {onAddToCart && (
        <CardFooter>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAddToCart();
            }}
            className="w-full rounded-md bg-primary-500 px-4 py-2 text-white hover:bg-primary-600"
          >
            Add to Cart
          </button>
        </CardFooter>
      )}
    </Card>
  )
);

ProductCard.displayName = 'ProductCard';

// Stats Card
export const StatsCard = React.forwardRef<
  HTMLDivElement,
  CardProps & {
    title: string;
    value: string | number;
    change?: string;
    changeType?: 'positive' | 'negative' | 'neutral';
    icon?: React.ReactNode;
  }
>(
  (
    {
      title,
      value,
      change,
      changeType = 'neutral',
      icon,
      className,
      ...props
    },
    ref
  ) => {
    const changeColor = {
      positive: 'text-success-600',
      negative: 'text-error-600',
      neutral: 'text-neutral-600',
    }[changeType];

    return (
      <Card ref={ref} className={cn('p-6', className)} {...props}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-neutral-600">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {change && (
              <p className={cn('text-xs', changeColor)}>
                {change}
              </p>
            )}
          </div>
          {icon && (
            <div className="text-2xl text-neutral-400">
              {icon}
            </div>
          )}
        </div>
      </Card>
    );
  }
);

StatsCard.displayName = 'StatsCard';

// Feature Card
export const FeatureCard = React.forwardRef<
  HTMLDivElement,
  CardProps & {
    icon?: React.ReactNode;
    title: string;
    description: string;
    href?: string;
  }
>(({ icon, title, description, href, className, ...props }, ref) => {
  const Component = href ? 'a' : 'div';
  
  return (
    <Card
      ref={ref}
      as={Component}
      href={href}
      className={cn('text-center', className)}
      hover={!!href}
      clickable={!!href}
      {...props}
    >
      <CardContent className="pt-6">
        {icon && (
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
            {icon}
          </div>
        )}
        <CardTitle className="mb-2">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardContent>
    </Card>
  );
});

FeatureCard.displayName = 'FeatureCard';

// Export types
export type CardVariants = VariantProps<typeof cardVariants>;

// Export compound component
export const CardCompound = Object.assign(Card, {
  Header: CardHeader,
  Title: CardTitle,
  Description: CardDescription,
  Content: CardContent,
  Footer: CardFooter,
});