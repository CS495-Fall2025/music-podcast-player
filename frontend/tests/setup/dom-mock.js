/**
 * Global DOM mocks for testing
 *
 * Provides mock implementations of browser window and document objects.
 * These mocks are available globally in all test files.
 */

import { vi } from "vitest";

// Mock window object with common methods
const windowMock = {
  alert: vi.fn(),
};

// Mock document object with DOM manipulation methods
const documentMock = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  createElement: () => ({
    contains: vi.fn(),
  }),
};

globalThis.window = windowMock;
globalThis.document = documentMock;
