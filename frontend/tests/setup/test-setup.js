import { vi, beforeAll, afterAll, beforeEach, afterEach } from "vitest";

// Setup fake timers
beforeAll(() => {
  vi.useFakeTimers();
});

afterAll(() => {
  vi.useRealTimers();
});

// Reset mocks and timers before each test
beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
  vi.clearAllTimers();

  // Mock window
  vi.stubGlobal("window", {
    alert: vi.fn(),
    Event: vi.fn(),
  });

  // Mock document
  vi.stubGlobal("document", {
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    createElement: () => ({
      contains: vi.fn(),
      reset: vi.fn(),
    }),
  });

  // Mock FormData
  vi.stubGlobal(
    "FormData",
    vi.fn(() => ({
      get: vi.fn(),
      append: vi.fn(),
    })),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});
