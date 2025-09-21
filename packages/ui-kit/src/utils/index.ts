/**
 * Utility functions for the design system
 * Provides helper functions for styling, class names, and component props
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines class names and merges Tailwind classes intelligently
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Creates a style variant function using class-variance-authority pattern
 */
export function createVariants<T extends Record<string, Record<string, string>>>(
  variants: T
) {
  return function variant<K extends keyof T>(
    type: K,
    value: keyof T[K]
  ): string {
    return variants[type][value] || '';
  };
}

/**
 * Focuses an element with proper accessibility considerations
 */
export function focusElement(element: HTMLElement | null) {
  if (!element) return;
  
  element.focus();
  
  // Ensure the element is visible
  element.scrollIntoView({
    behavior: 'smooth',
    block: 'nearest',
    inline: 'nearest',
  });
}

/**
 * Generates a unique ID for components
 */
export function generateId(prefix = 'id'): string {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Creates a compound component pattern helper
 */
export function createCompoundComponent<T extends Record<string, any>>(
  components: T
) {
  return components;
}

/**
 * Polymorphic component ref forwarding helper
 */
export function forwardRef<T, P = {}>(
  render: (props: P, ref: React.Ref<T>) => React.ReactElement | null
) {
  return React.forwardRef<T, P>(render);
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Checks if a value is a valid React element
 */
export function isReactElement(value: any): value is React.ReactElement {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.type !== 'undefined'
  );
}

/**
 * Safely gets the display name of a React component
 */
export function getDisplayName(Component: React.ComponentType<any>): string {
  return Component.displayName || Component.name || 'Component';
}

/**
 * Creates a context with a default value and provider
 */
export function createContext<T>(
  defaultValue: T,
  errorMessage = 'useContext must be used within a Provider'
) {
  const Context = React.createContext<T | undefined>(undefined);
  
  function useContext() {
    const context = React.useContext(Context);
    if (context === undefined) {
      throw new Error(errorMessage);
    }
    return context;
  }
  
  return [useContext, Context.Provider] as const;
}

/**
 * Merges refs together
 */
export function mergeRefs<T = any>(
  ...refs: Array<React.MutableRefObject<T> | React.LegacyRef<T>>
): React.RefCallback<T> {
  return (value) => {
    refs.forEach((ref) => {
      if (typeof ref === 'function') {
        ref(value);
      } else if (ref != null) {
        (ref as React.MutableRefObject<T | null>).current = value;
      }
    });
  };
}

/**
 * Hook for using previous value
 */
export function usePrevious<T>(value: T): T | undefined {
  const ref = React.useRef<T>();
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

/**
 * Hook for controlling state externally or internally
 */
export function useControllableState<T>({
  prop,
  defaultProp,
  onChange,
}: {
  prop?: T;
  defaultProp?: T;
  onChange?: (value: T) => void;
}) {
  const [uncontrolledProp, setUncontrolledProp] = React.useState(defaultProp);
  const isControlled = prop !== undefined;
  const value = isControlled ? prop : uncontrolledProp;
  
  const setValue = React.useCallback(
    (nextValue: T) => {
      if (isControlled) {
        onChange?.(nextValue);
      } else {
        setUncontrolledProp(nextValue);
        onChange?.(nextValue);
      }
    },
    [isControlled, onChange]
  );
  
  return [value, setValue] as const;
}

/**
 * Hook for handling click outside
 */
export function useClickOutside(
  ref: React.RefObject<HTMLElement>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  React.useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event);
    };
    
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);
    
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

/**
 * Hook for keyboard navigation
 */
export function useKeyboardNavigation(
  items: HTMLElement[],
  options: {
    orientation?: 'horizontal' | 'vertical';
    loop?: boolean;
    onSelect?: (index: number) => void;
  } = {}
) {
  const { orientation = 'vertical', loop = true, onSelect } = options;
  const [focusedIndex, setFocusedIndex] = React.useState(-1);
  
  const handleKeyDown = React.useCallback(
    (event: KeyboardEvent) => {
      const { key } = event;
      const isHorizontal = orientation === 'horizontal';
      const nextKey = isHorizontal ? 'ArrowRight' : 'ArrowDown';
      const prevKey = isHorizontal ? 'ArrowLeft' : 'ArrowUp';
      
      let nextIndex = focusedIndex;
      
      switch (key) {
        case nextKey:
          event.preventDefault();
          nextIndex = focusedIndex + 1;
          if (nextIndex >= items.length) {
            nextIndex = loop ? 0 : items.length - 1;
          }
          break;
          
        case prevKey:
          event.preventDefault();
          nextIndex = focusedIndex - 1;
          if (nextIndex < 0) {
            nextIndex = loop ? items.length - 1 : 0;
          }
          break;
          
        case 'Home':
          event.preventDefault();
          nextIndex = 0;
          break;
          
        case 'End':
          event.preventDefault();
          nextIndex = items.length - 1;
          break;
          
        case 'Enter':
        case ' ':
          event.preventDefault();
          onSelect?.(focusedIndex);
          return;
      }
      
      if (nextIndex !== focusedIndex && items[nextIndex]) {
        setFocusedIndex(nextIndex);
        focusElement(items[nextIndex]);
      }
    },
    [focusedIndex, items, orientation, loop, onSelect]
  );
  
  return {
    focusedIndex,
    setFocusedIndex,
    handleKeyDown,
  };
}

/**
 * Size utilities
 */
export const sizeUtils = {
  px: (value: number) => `${value}px`,
  rem: (value: number) => `${value}rem`,
  em: (value: number) => `${value}em`,
  percent: (value: number) => `${value}%`,
  vh: (value: number) => `${value}vh`,
  vw: (value: number) => `${value}vw`,
};

/**
 * Animation utilities
 */
export const animationUtils = {
  fadeIn: 'animate-in fade-in duration-200',
  fadeOut: 'animate-out fade-out duration-200',
  slideIn: 'animate-in slide-in-from-bottom-2 duration-200',
  slideOut: 'animate-out slide-out-to-bottom-2 duration-200',
  scaleIn: 'animate-in zoom-in-95 duration-200',
  scaleOut: 'animate-out zoom-out-95 duration-200',
};

/**
 * Responsive utilities
 */
export const responsive = {
  mobile: (classes: string) => `${classes} sm:hidden`,
  tablet: (classes: string) => `hidden sm:${classes} lg:hidden`,
  desktop: (classes: string) => `hidden lg:${classes}`,
  mobileTablet: (classes: string) => `${classes} lg:hidden`,
  tabletDesktop: (classes: string) => `hidden sm:${classes}`,
};

// Re-export React for convenience
import React from 'react';
export { React };