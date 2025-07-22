module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  setupFilesAfterEnv: [
    '<rootDir>/src/test/setup/setupTests.ts',
    '<rootDir>/src/test/setup/performanceSetup.ts'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg|webp)$': '<rootDir>/src/test/__mocks__/fileMock.js',
    '^axios$': '<rootDir>/src/test/__mocks__/axios.ts',
    '^date-fns$': '<rootDir>/src/test/__mocks__/date-fns.js',
    '^react-router-dom$': '<rootDir>/src/test/__mocks__/react-router-dom.js'
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        isolatedModules: false,
        types: ['node', 'jest', '@testing-library/jest-dom']
      }
    }],
    '^.+\\.(js|jsx)$': 'babel-jest'
  },
  transformIgnorePatterns: [
    'node_modules/(?!(axios|date-fns|@testing-library)/)'
  ],
  testMatch: [
    '**/__tests__/**/*.(ts|tsx|js)',
    '**/*.test.(ts|tsx|js)',
    '**/*.spec.(ts|tsx|js)',
    '**/test/**/*.test.(ts|tsx|js)',
    '**/test_*.tsx',
    '**/test_*.ts'
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/serviceWorker.ts',
    '!src/**/__tests__/**',
    '!src/**/__mocks__/**',
    '!src/test/**'
  ],
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  moduleDirectories: ['node_modules', 'src'],
  testTimeout: 10000,
  verbose: true
};