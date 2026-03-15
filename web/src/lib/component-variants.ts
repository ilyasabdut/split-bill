import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Component variant utilities for consistent styling across the app.
 * All variants use semantic design tokens from app.css.
 */

// Badge variants - for status indicators, labels, tags
export const badgeVariants = {
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  error: 'bg-error/10 text-error',
  info: 'bg-info/10 text-info',
  neutral: 'bg-surface-100 text-text-secondary',
} as const;

// Button variants - extend existing Button component patterns
export const buttonVariants = {
  primary: 'bg-primary-500 text-white hover:bg-primary-600',
  secondary: 'bg-surface-0 text-text-primary border border-surface-200',
  danger: 'bg-error text-white hover:bg-error/90',
  ghost: 'text-text-primary hover:bg-surface-50',
} as const;

// Input sizes - all meet minimum 44px touch target
export const inputSizes = {
  sm: 'px-3 py-2 text-label h-11',      // 44px height
  md: 'px-4 py-3 text-body h-12',       // 48px height
  lg: 'px-5 py-4 text-subheading h-16', // 64px height (for prominent inputs)
} as const;

// Card padding variants - for consistent card spacing
export const cardPadding = {
  compact: 'p-4',      // 16px
  default: 'p-6',      // 24px
  spacious: 'p-8',     // 32px
} as const;

/**
 * Gap size variants - semantic spacing for layouts
 */
export const gapVariants = {
  tight: 'gap-tight',       // 8px
  component: 'gap-component', // 16px
  section: 'gap-section',  // 24px
} as const;

/**
 * Merge class names with proper precedence.
 * Wrapper around clsx + tailwind-merge for consistent utility class handling.
 */
export function cv(...classes: ClassValue[]) {
  return twMerge(clsx(...classes));
}

// Type exports for TypeScript consumers
export type BadgeVariant = keyof typeof badgeVariants;
export type ButtonVariant = keyof typeof buttonVariants;
export type InputSize = keyof typeof inputSizes;
export type CardPadding = keyof typeof cardPadding;
export type GapVariant = keyof typeof gapVariants;
