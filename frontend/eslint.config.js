import js from '@eslint/js'
import globals from 'globals'
import reactPlugin from 'eslint-plugin-react'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    plugins: { react: reactPlugin },
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactPlugin.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',  // React 17+ no requiere import React
      'react/prop-types': 'off',           // sin TypeScript no vale la pena
      'no-unused-vars': 'warn',
      'no-console': 'warn',
    },
  },
]
