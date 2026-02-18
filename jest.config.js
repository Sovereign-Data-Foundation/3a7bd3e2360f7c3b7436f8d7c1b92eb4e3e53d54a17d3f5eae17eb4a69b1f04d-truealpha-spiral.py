/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',

  // Root of the "Crystalline Lattice"
  roots: ['<rootDir>/src'],

  // Match only explicit test files
  testMatch: [
    "**/__tests__/**/*.+(ts|js)",
    "**/?(*.)+(spec|test).+(ts|js)"
  ],

  // Transform TS with strict config
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
      diagnostics: {
        warnOnly: false // Fail on compilation errors (Day Zero requirement)
      }
    }]
  },

  // Coverage to ensure no logic hides in the dark
  collectCoverage: true,
  coverageReporters: ['text', 'lcov'],
  coverageDirectory: 'coverage'
};
