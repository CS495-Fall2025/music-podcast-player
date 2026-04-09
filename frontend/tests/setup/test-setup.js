import { vi, beforeAll, afterAll, beforeEach, afterEach } from "vitest";

/**
 * Global test setup config for vitest
 *
 * This configures the testing environment with:
 * - fake timers for controlling async operations
 * - automatic cleanup between tests
 *
 * all tests will run with these mocks applied automatically.
 */

// Enable fake timers for all tests
beforeAll(() => {
  vi.useFakeTimers();
	globalThis.__NAME__ = "MusicPodcastPlayerTest";
	globalThis.__VERSION__ = "1.0.0";
});

// Restore real timers after all tests complete
afterAll(() => {
  vi.useRealTimers();
});

// Reset test environment before each individual test
beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
  vi.clearAllTimers();

  if (globalThis.localStorage) {
    globalThis.localStorage.clear();
  }

  if (globalThis.sessionStorage) {
    globalThis.sessionStorage.clear();
  }
});

// Clean up all global mocks after each test
afterEach(() => {
  vi.restoreAllMocks();
});
