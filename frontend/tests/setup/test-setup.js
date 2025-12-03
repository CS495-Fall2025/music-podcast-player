import { vi, beforeAll, afterAll, beforeEach, afterEach } from "vitest";

/**
 * Global test setup config for vitest
 *
 * This configures the testing environment with:
 * - fake timers for controlling async operations
 * - mock browser APIs (window, document, FormData)
 * - automatic cleanup between tests
 *
 * all tests will run with these mocks applied automatically.
 */

// Enable fake timers for all tests
beforeAll(() => {
  vi.useFakeTimers();
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

  // Mock browser window object
  vi.stubGlobal("window", {
    alert: vi.fn(),
    Event: vi.fn(),
  });

  // Mock browser document object
  vi.stubGlobal("document", {
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    createElement: () => ({
      contains: vi.fn(),
      reset: vi.fn(),
    }),
  });

  // Mock FormData API
  vi.stubGlobal(
    "FormData",
    vi.fn(() => ({
      get: vi.fn(),
      append: vi.fn(),
    })),
  );
});

// Clean up all global mocks after each test
afterEach(() => {
  vi.unstubAllGlobals();
});
