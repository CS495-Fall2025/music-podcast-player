import { vi } from "vitest";

// Mock window and document for DOM tests
const windowMock = {
  alert: vi.fn(),
};

const documentMock = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  createElement: () => ({
    contains: vi.fn(),
  }),
};

global.window = windowMock;
global.document = documentMock;
