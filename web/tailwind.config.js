/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        success: 'rgba(var(--color-success), <alpha-value>)',
        warning: 'rgba(var(--color-warning), <alpha-value>)',
        error: 'rgba(var(--color-error), <alpha-value>)',
        info: 'rgba(var(--color-info), <alpha-value>)',
        surface: {
          0: 'rgba(var(--color-surface-0), <alpha-value>)',
          50: 'rgba(var(--color-surface-50), <alpha-value>)',
          100: 'rgba(var(--color-surface-100), <alpha-value>)',
          200: 'rgba(var(--color-surface-200), <alpha-value>)',
        },
        text: {
          primary: 'rgba(var(--color-text-primary), <alpha-value>)',
          secondary: 'rgba(var(--color-text-secondary), <alpha-value>)',
          tertiary: 'rgba(var(--color-text-tertiary), <alpha-value>)',
          inverted: 'rgba(var(--color-text-inverted), <alpha-value>)',
        },
      },
      borderRadius: {
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        xl2: '1.25rem',
      },
      spacing: {
        'section': 'var(--spacing-6)',
        'component': 'var(--spacing-4)',
        'tight': 'var(--spacing-2)',
      },
      fontSize: {
        'caption': 'var(--font-size-xs)',
        'label': 'var(--font-size-sm)',
        'body': 'var(--font-size-base)',
        'subheading': 'var(--font-size-md)',
        'section': 'var(--font-size-lg)',
        'heading': 'var(--font-size-xl)',
        'hero': 'var(--font-size-2xl)',
        'display': 'var(--font-size-3xl)',
      },
      boxShadow: {
        'card': 'var(--shadow-card)',
        'elevated': 'var(--shadow-elevated)',
        'modal': 'var(--shadow-modal)',
      },
    }
  },
  plugins: [
    require('@skeletonlabs/skeleton/tailwind.cjs')({
      themes: ['skeleton', 'wintry', 'modern', 'crimson', 'gold-nouveau', 'vintage']
    })
  ]
};
