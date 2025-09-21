/**
 * TypeScript types for the UI Kit
 * Provides type definitions for component props, variants, and design tokens
 */

import React from 'react';
import type { VariantProps } from 'class-variance-authority';

// Base component props
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  id?: string;
  'data-testid'?: string;
}

// Polymorphic component types
export type PolymorphicAsProp<E extends React.ElementType> = {
  as?: E;
};

export type PolymorphicProps<E extends React.ElementType, P = {}> = P &
  PolymorphicAsProp<E> &
  Omit<React.ComponentPropsWithoutRef<E>, keyof (P & PolymorphicAsProp<E>)>;

// Size variants
export type SizeVariant = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Color variants
export type ColorVariant = 
  | 'primary' 
  | 'secondary' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'info' 
  | 'neutral';

// Visual variants
export type VisualVariant = 
  | 'solid' 
  | 'outline' 
  | 'ghost' 
  | 'link' 
  | 'soft';

// Loading states
export interface LoadingState {
  isLoading?: boolean;
  loadingText?: string;
}

// Disabled state
export interface DisabledState {
  disabled?: boolean;
  disabledReason?: string;
}

// Form component props
export interface FormFieldProps extends BaseComponentProps {
  label?: string;
  description?: string;
  error?: string;
  required?: boolean;
  name?: string;
}

// Input variants
export interface InputProps extends 
  BaseComponentProps,
  FormFieldProps,
  LoadingState,
  DisabledState {
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  size?: SizeVariant;
  variant?: 'default' | 'filled' | 'flushed';
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  autoComplete?: string;
  autoFocus?: boolean;
  readOnly?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

// Button variants
export interface ButtonProps extends 
  BaseComponentProps,
  LoadingState,
  DisabledState {
  variant?: VisualVariant;
  color?: ColorVariant;
  size?: SizeVariant;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  form?: string;
}

// Card variants
export interface CardProps extends BaseComponentProps {
  variant?: 'elevated' | 'outlined' | 'filled';
  padding?: SizeVariant | 'none';
  hover?: boolean;
  clickable?: boolean;
  onClick?: () => void;
}

// Badge variants
export interface BadgeProps extends BaseComponentProps {
  variant?: VisualVariant;
  color?: ColorVariant;
  size?: Exclude<SizeVariant, 'xl'>;
  dot?: boolean;
  ping?: boolean;
}

// Avatar variants
export interface AvatarProps extends BaseComponentProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: SizeVariant;
  shape?: 'circle' | 'square';
  fallback?: React.ReactNode;
  onError?: () => void;
}

// Modal variants
export interface ModalProps extends BaseComponentProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  size?: SizeVariant | 'full';
  centered?: boolean;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  title?: string;
  description?: string;
}

// Tooltip variants
export interface TooltipProps extends BaseComponentProps {
  content: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'top-start' | 'top-end' | 'bottom-start' | 'bottom-end' | 'left-start' | 'left-end' | 'right-start' | 'right-end';
  delay?: number;
  offset?: number;
  arrow?: boolean;
}

// Navigation variants
export interface NavigationProps extends BaseComponentProps {
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'pills' | 'underline' | 'enclosed';
  size?: SizeVariant;
}

// Table variants
export interface TableProps extends BaseComponentProps {
  variant?: 'simple' | 'striped' | 'bordered';
  size?: SizeVariant;
  stickyHeader?: boolean;
  highlightOnHover?: boolean;
}

// Data table specific types
export interface Column<T = any> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  width?: string | number;
  sortable?: boolean;
  filterable?: boolean;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
}

export interface DataTableProps<T = any> extends BaseComponentProps {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
  selection?: {
    selectedKeys: string[];
    onChange: (selectedKeys: string[]) => void;
    getRowKey: (record: T) => string;
  };
  sorting?: {
    field: string;
    direction: 'asc' | 'desc';
    onChange: (field: string, direction: 'asc' | 'desc') => void;
  };
  filtering?: {
    filters: Record<string, any>;
    onChange: (filters: Record<string, any>) => void;
  };
  emptyState?: React.ReactNode;
  errorState?: React.ReactNode;
}

// Form builder types
export interface FormField {
  name: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'checkbox' | 'radio' | 'textarea' | 'date' | 'file';
  label: string;
  placeholder?: string;
  description?: string;
  required?: boolean;
  disabled?: boolean;
  options?: Array<{ label: string; value: string | number }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | undefined;
  };
  defaultValue?: any;
  dependencies?: {
    field: string;
    condition: (value: any) => boolean;
  }[];
}

export interface FormBuilderProps extends BaseComponentProps {
  fields: FormField[];
  onSubmit: (values: Record<string, any>) => void | Promise<void>;
  onValuesChange?: (values: Record<string, any>) => void;
  initialValues?: Record<string, any>;
  loading?: boolean;
  disabled?: boolean;
  layout?: 'vertical' | 'horizontal' | 'inline';
  submitButton?: {
    text: string;
    loading?: boolean;
    disabled?: boolean;
  };
  resetButton?: {
    text: string;
    show?: boolean;
  };
}

// Theme types
export interface ThemeConfig {
  colors: Record<string, Record<string, string>>;
  spacing: Record<string, string>;
  typography: {
    fontFamily: Record<string, string[]>;
    fontSize: Record<string, [string, { lineHeight: string }]>;
    fontWeight: Record<string, string>;
  };
  borderRadius: Record<string, string>;
  shadows: Record<string, string>;
  motion: {
    easing: Record<string, string>;
    duration: Record<string, string>;
  };
}

// Component variant types using class-variance-authority
export type ComponentVariants<T> = VariantProps<T>;

// Event handler types
export type EventHandler<T = any> = (event: T) => void;
export type ChangeHandler<T = string> = (value: T) => void;
export type ClickHandler = () => void;
export type FocusHandler = () => void;
export type BlurHandler = () => void;

// Ref types
export type ComponentRef<T extends keyof JSX.IntrinsicElements> = React.ComponentRef<T>;

// Responsive types
export type ResponsiveValue<T> = T | {
  base?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
};

// Animation types
export interface AnimationConfig {
  duration?: number;
  easing?: string;
  delay?: number;
  repeat?: number | 'infinite';
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

// Accessibility types
export interface AccessibilityProps {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-hidden'?: boolean;
  'aria-disabled'?: boolean;
  'aria-checked'?: boolean | 'mixed';
  'aria-selected'?: boolean;
  'aria-pressed'?: boolean;
  'aria-current'?: boolean | 'page' | 'step' | 'location' | 'date' | 'time';
  role?: string;
  tabIndex?: number;
}

// Layout types
export interface LayoutProps {
  display?: 'block' | 'inline' | 'inline-block' | 'flex' | 'inline-flex' | 'grid' | 'inline-grid' | 'none';
  position?: 'static' | 'relative' | 'absolute' | 'fixed' | 'sticky';
  top?: string | number;
  right?: string | number;
  bottom?: string | number;
  left?: string | number;
  zIndex?: number;
  overflow?: 'visible' | 'hidden' | 'scroll' | 'auto';
  width?: string | number;
  height?: string | number;
  minWidth?: string | number;
  minHeight?: string | number;
  maxWidth?: string | number;
  maxHeight?: string | number;
}

// Spacing types
export interface SpacingProps {
  margin?: ResponsiveValue<string | number>;
  marginTop?: ResponsiveValue<string | number>;
  marginRight?: ResponsiveValue<string | number>;
  marginBottom?: ResponsiveValue<string | number>;
  marginLeft?: ResponsiveValue<string | number>;
  marginX?: ResponsiveValue<string | number>;
  marginY?: ResponsiveValue<string | number>;
  padding?: ResponsiveValue<string | number>;
  paddingTop?: ResponsiveValue<string | number>;
  paddingRight?: ResponsiveValue<string | number>;
  paddingBottom?: ResponsiveValue<string | number>;
  paddingLeft?: ResponsiveValue<string | number>;
  paddingX?: ResponsiveValue<string | number>;
  paddingY?: ResponsiveValue<string | number>;
}

// Border types
export interface BorderProps {
  border?: string;
  borderTop?: string;
  borderRight?: string;
  borderBottom?: string;
  borderLeft?: string;
  borderWidth?: string | number;
  borderStyle?: 'solid' | 'dashed' | 'dotted' | 'double' | 'none';
  borderColor?: string;
  borderRadius?: ResponsiveValue<string | number>;
  borderTopLeftRadius?: ResponsiveValue<string | number>;
  borderTopRightRadius?: ResponsiveValue<string | number>;
  borderBottomLeftRadius?: ResponsiveValue<string | number>;
  borderBottomRightRadius?: ResponsiveValue<string | number>;
}

// Typography types
export interface TypographyProps {
  fontFamily?: string;
  fontSize?: ResponsiveValue<string | number>;
  fontWeight?: ResponsiveValue<string | number>;
  lineHeight?: ResponsiveValue<string | number>;
  letterSpacing?: ResponsiveValue<string | number>;
  textAlign?: ResponsiveValue<'left' | 'center' | 'right' | 'justify'>;
  textTransform?: 'none' | 'uppercase' | 'lowercase' | 'capitalize';
  textDecoration?: 'none' | 'underline' | 'overline' | 'line-through';
  color?: string;
}

// Combined style props
export interface StyleProps extends 
  LayoutProps, 
  SpacingProps, 
  BorderProps, 
  TypographyProps {
  background?: string;
  backgroundColor?: string;
  backgroundImage?: string;
  backgroundSize?: string;
  backgroundPosition?: string;
  backgroundRepeat?: string;
  boxShadow?: string;
  opacity?: number;
  transform?: string;
  transition?: string;
  cursor?: string;
  userSelect?: 'none' | 'auto' | 'text' | 'contain' | 'all';
  pointerEvents?: 'none' | 'auto';
}