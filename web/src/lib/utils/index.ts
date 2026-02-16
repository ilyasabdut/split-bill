import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export * from './image';

/**
 * Utility function for conditional Tailwind class merging
 * @param inputs - Class names or conditional class objects
 * @returns Merged class string
 */
export function cn(...inputs: Parameters<typeof clsx>) {
  return twMerge(clsx(inputs));
}
