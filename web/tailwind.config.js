/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          900: '#0F1115',
          800: '#14171D',
          700: '#1A1D24',
          600: '#22262E',
          500: '#262A33',
          400: '#363B45',
        },
        fg: {
          DEFAULT: '#E6E8EC',
          muted: '#9AA0AB',
          faint: '#646A75',
          ghost: '#3F454F',
        },
        accent: {
          DEFAULT: '#C9892D',
          soft: '#3A2A14',
          hi: '#E0A14A',
        },
        danger: '#E5484D',
        warn: '#FFB224',
        ok: '#46A758',
        info: '#5B8DEF',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'Menlo'],
      },
      fontSize: {
        '2xs': ['10px', '14px'],
        xs: ['11px', '16px'],
        sm: ['12px', '16px'],
        base: ['13px', '18px'],
        md: ['14px', '20px'],
      },
    },
  },
  plugins: [],
};
