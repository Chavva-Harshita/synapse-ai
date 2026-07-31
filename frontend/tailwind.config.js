/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        synapse: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b'
        },
        cyber: {
          pink: '#ff2d95',
          cyan: '#00f0ff',
          purple: '#8b5cf6',
          indigo: '#6366f1'
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'synapse-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'cyber-gradient': 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)'
      },
      boxShadow: {
        glass: '0 10px 30px rgba(0,0,0,0.35)',
        glow: '0 0 20px rgba(99, 102, 241, 0.3)',
        'glow-cyan': '0 0 20px rgba(0, 240, 255, 0.25)',
        'glow-pink': '0 0 20px rgba(255, 45, 149, 0.25)',
        'inner-glow': 'inset 0 0 20px rgba(99, 102, 241, 0.1)'
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out 3s infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'fade-in-up': 'fade-in-up 0.5s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'slide-out-right': 'slide-out-right 0.3s ease-in',
        'spin-slow': 'spin 8s linear infinite',
        'border-glow': 'border-glow 3s ease-in-out infinite',
        'line-reveal': 'line-reveal 0.3s ease-out',
        'robot-float': 'robot-float 4s ease-in-out infinite',
        'status-pulse': 'status-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 0.4 },
          '50%': { opacity: 1 }
        },
        'gradient-shift': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' }
        },
        'fade-in-up': {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' }
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100%)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 }
        },
        'slide-out-right': {
          '0%': { transform: 'translateX(0)', opacity: 1 },
          '100%': { transform: 'translateX(100%)', opacity: 0 }
        },
        'border-glow': {
          '0%, 100%': { borderColor: 'rgba(34, 211, 238, 0.2)' },
          '50%': { borderColor: 'rgba(139, 92, 246, 0.4)' }
        },
        'line-reveal': {
          '0%': { opacity: 0, transform: 'translateX(-5px)' },
          '100%': { opacity: 1, transform: 'translateX(0)' }
        },
        'robot-float': {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '25%': { transform: 'translateY(-5px) rotate(-2deg)' },
          '75%': { transform: 'translateY(-5px) rotate(2deg)' },
        },
        'status-pulse': {
          '0%, 100%': { boxShadow: '0 0 4px rgba(34, 211, 238, 0.4)' },
          '50%': { boxShadow: '0 0 12px rgba(34, 211, 238, 0.8)' }
        }
      }
    }
  },
  plugins: []
}
