module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  corePlugins: {
    preflight: false
  },
  theme: {
    extend: {
      colors: {
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        accent: 'rgb(var(--color-accent) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        ink: 'rgb(var(--color-ink) / <alpha-value>)'
      },
      borderRadius: {
        app: 'var(--radius-app)',
        control: 'var(--radius-control)',
        pill: '999rem'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        panel: '0 1.5rem 4rem rgb(15 23 42 / 0.12)'
      }
    }
  },
  plugins: []
}
