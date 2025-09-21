/**
 * Theme provider and utilities
 * Provides theme context and customization capabilities
 */

import React from 'react';
import { tokens } from '../tokens';
import type { ThemeConfig } from '../types';

// Default theme configuration
const defaultTheme: ThemeConfig = {
  colors: tokens.colors,
  spacing: tokens.spacing,
  typography: tokens.typography,
  borderRadius: tokens.borderRadius,
  shadows: tokens.shadows,
  motion: tokens.motion,
};

// Theme context
interface ThemeContextValue {
  theme: ThemeConfig;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (theme: Partial<ThemeConfig>) => void;
}

const ThemeContext = React.createContext<ThemeContextValue | null>(null);

// Theme provider props
interface ThemeProviderProps {
  children: React.ReactNode;
  theme?: Partial<ThemeConfig>;
  defaultDark?: boolean;
}

/**
 * Theme provider component
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  theme: customTheme = {},
  defaultDark = false,
}) => {
  const [isDark, setIsDark] = React.useState(defaultDark);
  const [theme, setThemeState] = React.useState<ThemeConfig>({
    ...defaultTheme,
    ...customTheme,
  });

  // Merge custom theme with default
  React.useEffect(() => {
    setThemeState({
      ...defaultTheme,
      ...customTheme,
    });
  }, [customTheme]);

  // Apply theme to CSS custom properties
  React.useEffect(() => {
    const root = document.documentElement;
    
    // Apply color variables
    Object.entries(theme.colors).forEach(([colorName, colorShades]) => {
      if (typeof colorShades === 'object') {
        Object.entries(colorShades).forEach(([shade, value]) => {
          root.style.setProperty(`--color-${colorName}-${shade}`, value);
        });
      } else {
        root.style.setProperty(`--color-${colorName}`, colorShades);
      }
    });

    // Apply spacing variables
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value);
    });

    // Apply typography variables
    Object.entries(theme.typography.fontSize).forEach(([size, [value, config]]) => {
      root.style.setProperty(`--font-size-${size}`, value);
      root.style.setProperty(`--line-height-${size}`, config.lineHeight);
    });

    Object.entries(theme.typography.fontWeight).forEach(([weight, value]) => {
      root.style.setProperty(`--font-weight-${weight}`, value);
    });

    // Apply border radius variables
    Object.entries(theme.borderRadius).forEach(([key, value]) => {
      root.style.setProperty(`--border-radius-${key}`, value);
    });

    // Apply shadow variables
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value);
    });

    // Apply motion variables
    Object.entries(theme.motion.duration).forEach(([key, value]) => {
      root.style.setProperty(`--duration-${key}`, value);
    });

    Object.entries(theme.motion.easing).forEach(([key, value]) => {
      root.style.setProperty(`--easing-${key}`, value);
    });

    // Apply dark mode class
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme, isDark]);

  const toggleTheme = React.useCallback(() => {
    setIsDark(!isDark);
  }, [isDark]);

  const setTheme = React.useCallback((newTheme: Partial<ThemeConfig>) => {
    setThemeState(prev => ({
      ...prev,
      ...newTheme,
    }));
  }, []);

  const contextValue: ThemeContextValue = {
    theme,
    isDark,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * Hook to use theme context
 */
export const useTheme = (): ThemeContextValue => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

/**
 * Hook to get current theme values
 */
export const useThemeValue = () => {
  const { theme } = useTheme();
  return theme;
};

/**
 * Hook for responsive values based on breakpoints
 */
export const useResponsiveValue = <T,>(
  value: T | { [key: string]: T },
  breakpoints = tokens.breakpoints
): T => {
  const [currentValue, setCurrentValue] = React.useState<T>(
    typeof value === 'object' && value !== null && 'base' in value
      ? (value as any).base
      : value as T
  );

  React.useEffect(() => {
    if (typeof value !== 'object' || value === null || !('base' in value)) {
      setCurrentValue(value as T);
      return;
    }

    const responsiveValue = value as { [key: string]: T };
    
    const updateValue = () => {
      const width = window.innerWidth;
      
      // Convert breakpoints to numbers and sort them
      const sortedBreakpoints = Object.entries(breakpoints)
        .map(([key, val]) => ({ key, value: parseInt(val) }))
        .sort((a, b) => a.value - b.value);

      // Find the appropriate value
      let selectedValue = responsiveValue.base;

      for (const breakpoint of sortedBreakpoints) {
        if (width >= breakpoint.value && responsiveValue[breakpoint.key]) {
          selectedValue = responsiveValue[breakpoint.key];
        }
      }

      setCurrentValue(selectedValue);
    };

    updateValue();
    window.addEventListener('resize', updateValue);
    
    return () => window.removeEventListener('resize', updateValue);
  }, [value, breakpoints]);

  return currentValue;
};

/**
 * Hook for CSS-in-JS style objects with theme values
 */
export const useThemeStyles = () => {
  const { theme } = useTheme();

  const getColor = (colorPath: string) => {
    const [colorName, shade] = colorPath.split('.');
    const color = theme.colors[colorName];
    
    if (typeof color === 'object' && shade) {
      return color[shade];
    }
    
    return color || colorPath;
  };

  const getSpacing = (key: string) => {
    return theme.spacing[key] || key;
  };

  const getBorderRadius = (key: string) => {
    return theme.borderRadius[key] || key;
  };

  const getShadow = (key: string) => {
    return theme.shadows[key] || key;
  };

  return {
    getColor,
    getSpacing,
    getBorderRadius,
    getShadow,
    theme,
  };
};

/**
 * Higher-order component for theme injection
 */
export const withTheme = <P extends object>(
  Component: React.ComponentType<P & { theme: ThemeConfig }>
) => {
  const WrappedComponent = (props: P) => {
    const { theme } = useTheme();
    return <Component {...props} theme={theme} />;
  };

  WrappedComponent.displayName = `withTheme(${Component.displayName || Component.name})`;
  return WrappedComponent;
};

// Export default theme for external use
export { defaultTheme, tokens };