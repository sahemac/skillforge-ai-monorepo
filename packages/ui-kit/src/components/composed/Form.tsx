/**
 * Form component - A comprehensive form builder using primitives
 * Provides validation, submission handling, and various field types
 */

import React from 'react';
import { Button } from '../primitives/Button';
import { Input, PasswordInput, EmailInput, NumberInput } from '../primitives/Input';
import { Card, CardContent, CardHeader, CardTitle } from '../primitives/Card';
import { cn } from '../../utils';
import type { FormBuilderProps, FormField } from '../../types';

// Form context for sharing state between components
interface FormContextValue {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  setValue: (name: string, value: any) => void;
  setError: (name: string, error: string) => void;
  setFieldTouched: (name: string, touched: boolean) => void;
  validateField: (name: string, value: any) => string | undefined;
}

const FormContext = React.createContext<FormContextValue | null>(null);

const useFormContext = () => {
  const context = React.useContext(FormContext);
  if (!context) {
    throw new Error('Form components must be used within a Form');
  }
  return context;
};

/**
 * Individual form field component
 */
interface FormFieldComponentProps {
  field: FormField;
  className?: string;
}

const FormFieldComponent: React.FC<FormFieldComponentProps> = ({ field, className }) => {
  const {
    values,
    errors,
    touched,
    setValue,
    setError,
    setFieldTouched,
    validateField,
  } = useFormContext();

  const value = values[field.name] || field.defaultValue || '';
  const error = touched[field.name] ? errors[field.name] : undefined;

  const handleChange = (newValue: any) => {
    setValue(field.name, newValue);
    
    // Clear error if field was previously invalid
    if (errors[field.name]) {
      setError(field.name, '');
    }
    
    // Validate on change for real-time feedback
    const validationError = validateField(field.name, newValue);
    if (validationError) {
      setError(field.name, validationError);
    }
  };

  const handleBlur = () => {
    setFieldTouched(field.name, true);
    
    // Validate on blur
    const validationError = validateField(field.name, value);
    if (validationError) {
      setError(field.name, validationError);
    }
  };

  // Check if field should be shown based on dependencies
  const shouldShow = React.useMemo(() => {
    if (!field.dependencies) return true;
    
    return field.dependencies.every(dep => {
      const depValue = values[dep.field];
      return dep.condition(depValue);
    });
  }, [field.dependencies, values]);

  if (!shouldShow) return null;

  const commonProps = {
    name: field.name,
    label: field.label,
    description: field.description,
    error,
    required: field.required,
    disabled: field.disabled,
    placeholder: field.placeholder,
    value,
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => 
      handleChange(e.target.value),
    onBlur: handleBlur,
  };

  const wrapperClassName = cn(
    'space-y-2',
    field.type === 'checkbox' && 'flex items-center space-x-2 space-y-0',
    className
  );

  switch (field.type) {
    case 'email':
      return (
        <div className={wrapperClassName}>
          <EmailInput {...commonProps} />
        </div>
      );

    case 'password':
      return (
        <div className={wrapperClassName}>
          <PasswordInput {...commonProps} />
        </div>
      );

    case 'number':
      return (
        <div className={wrapperClassName}>
          <NumberInput 
            {...commonProps}
            min={field.validation?.min}
            max={field.validation?.max}
          />
        </div>
      );

    case 'textarea':
      return (
        <div className={wrapperClassName}>
          <label htmlFor={field.name} className="block text-sm font-medium text-neutral-700">
            {field.label}
            {field.required && <span className="ml-1 text-error-500">*</span>}
          </label>
          <textarea
            id={field.name}
            name={field.name}
            placeholder={field.placeholder}
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={field.disabled}
            required={field.required}
            rows={4}
            className={cn(
              'flex w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm transition-all duration-200',
              'placeholder:text-neutral-500',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:border-primary-500',
              'disabled:cursor-not-allowed disabled:opacity-50',
              error && 'border-error-500 focus:border-error-500 focus:ring-error-500'
            )}
          />
          {field.description && !error && (
            <p className="text-xs text-neutral-600">{field.description}</p>
          )}
          {error && (
            <p className="text-xs text-error-600">{error}</p>
          )}
        </div>
      );

    case 'select':
      return (
        <div className={wrapperClassName}>
          <label htmlFor={field.name} className="block text-sm font-medium text-neutral-700">
            {field.label}
            {field.required && <span className="ml-1 text-error-500">*</span>}
          </label>
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={field.disabled}
            required={field.required}
            className={cn(
              'flex w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:border-primary-500',
              'disabled:cursor-not-allowed disabled:opacity-50',
              error && 'border-error-500 focus:border-error-500 focus:ring-error-500'
            )}
          >
            <option value="">{field.placeholder || 'Select an option'}</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {field.description && !error && (
            <p className="text-xs text-neutral-600">{field.description}</p>
          )}
          {error && (
            <p className="text-xs text-error-600">{error}</p>
          )}
        </div>
      );

    case 'checkbox':
      return (
        <div className={wrapperClassName}>
          <input
            id={field.name}
            name={field.name}
            type="checkbox"
            checked={!!value}
            onChange={(e) => handleChange(e.target.checked)}
            onBlur={handleBlur}
            disabled={field.disabled}
            required={field.required}
            className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor={field.name} className="text-sm text-neutral-700">
            {field.label}
            {field.required && <span className="ml-1 text-error-500">*</span>}
          </label>
          {field.description && (
            <p className="text-xs text-neutral-600">{field.description}</p>
          )}
          {error && (
            <p className="text-xs text-error-600">{error}</p>
          )}
        </div>
      );

    case 'radio':
      return (
        <div className={wrapperClassName}>
          <fieldset>
            <legend className="block text-sm font-medium text-neutral-700">
              {field.label}
              {field.required && <span className="ml-1 text-error-500">*</span>}
            </legend>
            <div className="mt-2 space-y-2">
              {field.options?.map((option) => (
                <div key={option.value} className="flex items-center">
                  <input
                    id={`${field.name}-${option.value}`}
                    name={field.name}
                    type="radio"
                    value={option.value}
                    checked={value === option.value}
                    onChange={(e) => handleChange(e.target.value)}
                    onBlur={handleBlur}
                    disabled={field.disabled}
                    className="h-4 w-4 border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label
                    htmlFor={`${field.name}-${option.value}`}
                    className="ml-2 text-sm text-neutral-700"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </fieldset>
          {field.description && !error && (
            <p className="text-xs text-neutral-600">{field.description}</p>
          )}
          {error && (
            <p className="text-xs text-error-600">{error}</p>
          )}
        </div>
      );

    case 'date':
      return (
        <div className={wrapperClassName}>
          <Input 
            {...commonProps}
            type="date"
          />
        </div>
      );

    case 'file':
      return (
        <div className={wrapperClassName}>
          <label htmlFor={field.name} className="block text-sm font-medium text-neutral-700">
            {field.label}
            {field.required && <span className="ml-1 text-error-500">*</span>}
          </label>
          <input
            id={field.name}
            name={field.name}
            type="file"
            onChange={(e) => handleChange(e.target.files?.[0] || null)}
            onBlur={handleBlur}
            disabled={field.disabled}
            required={field.required}
            className={cn(
              'flex w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm transition-all duration-200',
              'file:border-0 file:bg-transparent file:text-sm file:font-medium',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:border-primary-500',
              'disabled:cursor-not-allowed disabled:opacity-50',
              error && 'border-error-500 focus:border-error-500 focus:ring-error-500'
            )}
          />
          {field.description && !error && (
            <p className="text-xs text-neutral-600">{field.description}</p>
          )}
          {error && (
            <p className="text-xs text-error-600">{error}</p>
          )}
        </div>
      );

    default:
      return (
        <div className={wrapperClassName}>
          <Input {...commonProps} />
        </div>
      );
  }
};

/**
 * Main Form Builder component
 */
export const Form: React.FC<FormBuilderProps> = ({
  fields,
  onSubmit,
  onValuesChange,
  initialValues = {},
  loading = false,
  disabled = false,
  layout = 'vertical',
  submitButton = { text: 'Submit' },
  resetButton = { text: 'Reset', show: true },
  className,
  children,
  ...props
}) => {
  const [values, setValues] = React.useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [touched, setTouched] = React.useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // Update values when initialValues change
  React.useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  // Notify parent of value changes
  React.useEffect(() => {
    onValuesChange?.(values);
  }, [values, onValuesChange]);

  const setValue = React.useCallback((name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);

  const setError = React.useCallback((name: string, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  const setFieldTouched = React.useCallback((name: string, touched: boolean) => {
    setTouched(prev => ({ ...prev, [name]: touched }));
  }, []);

  const validateField = React.useCallback((name: string, value: any): string | undefined => {
    const field = fields.find(f => f.name === name);
    if (!field || !field.validation) return undefined;

    const { min, max, pattern, custom } = field.validation;

    // Required validation
    if (field.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return `${field.label} is required`;
    }

    // Skip other validations if field is empty and not required
    if (!value && !field.required) return undefined;

    // Min/Max validation for numbers
    if (field.type === 'number' || typeof value === 'number') {
      const numValue = typeof value === 'number' ? value : parseFloat(value);
      if (!isNaN(numValue)) {
        if (min !== undefined && numValue < min) {
          return `${field.label} must be at least ${min}`;
        }
        if (max !== undefined && numValue > max) {
          return `${field.label} must be no more than ${max}`;
        }
      }
    }

    // Min/Max validation for strings (length)
    if (typeof value === 'string') {
      if (min !== undefined && value.length < min) {
        return `${field.label} must be at least ${min} characters`;
      }
      if (max !== undefined && value.length > max) {
        return `${field.label} must be no more than ${max} characters`;
      }
    }

    // Pattern validation
    if (pattern && typeof value === 'string' && !pattern.test(value)) {
      return `${field.label} format is invalid`;
    }

    // Custom validation
    if (custom) {
      return custom(value);
    }

    return undefined;
  }, [fields]);

  const validateAllFields = (): boolean => {
    const newErrors: Record<string, string> = {};
    let hasErrors = false;

    fields.forEach(field => {
      const error = validateField(field.name, values[field.name]);
      if (error) {
        newErrors[field.name] = error;
        hasErrors = true;
      }
    });

    setErrors(newErrors);
    return !hasErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Mark all fields as touched
    const newTouched: Record<string, boolean> = {};
    fields.forEach(field => {
      newTouched[field.name] = true;
    });
    setTouched(newTouched);

    // Validate all fields
    if (!validateAllFields()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  const contextValue: FormContextValue = {
    values,
    errors,
    touched,
    isSubmitting: isSubmitting || loading,
    setValue,
    setError,
    setFieldTouched,
    validateField,
  };

  const layoutClasses = {
    vertical: 'space-y-6',
    horizontal: 'grid grid-cols-2 gap-6',
    inline: 'flex flex-wrap gap-4',
  };

  return (
    <FormContext.Provider value={contextValue}>
      <form
        onSubmit={handleSubmit}
        className={cn('w-full', className)}
        {...props}
      >
        <div className={layoutClasses[layout]}>
          {fields.map((field) => (
            <FormFieldComponent
              key={field.name}
              field={field}
              className={layout === 'inline' ? 'min-w-0 flex-1' : undefined}
            />
          ))}
          {children}
        </div>

        <div className="mt-6 flex gap-3">
          <Button
            type="submit"
            isLoading={isSubmitting || loading || submitButton.loading}
            disabled={disabled || submitButton.disabled}
          >
            {submitButton.text}
          </Button>

          {resetButton.show && (
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={disabled || isSubmitting || loading}
            >
              {resetButton.text}
            </Button>
          )}
        </div>
      </form>
    </FormContext.Provider>
  );
};

/**
 * Form with Card wrapper for better presentation
 */
export const FormCard: React.FC<FormBuilderProps & {
  title?: string;
  description?: string;
}> = ({ title, description, ...props }) => {
  return (
    <Card>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <p className="text-sm text-neutral-600">{description}</p>}
        </CardHeader>
      )}
      <CardContent>
        <Form {...props} />
      </CardContent>
    </Card>
  );
};

// Export the form context for advanced usage
export { FormContext, useFormContext };