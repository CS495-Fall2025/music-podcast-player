/**
 * Mock router for testing
 *
 * Provides a mock Vue Router instance with spies on all navigation methods.
 * This mock is automatically applied to all tests that import vue-router.
 */

import { vi } from "vitest";

// Mock router instance with common navigation methods
export const router = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
};

// Mock vue-router module
vi.mock("vue-router", () => ({
  createRouter: vi.fn(() => router),
  createWebHistory: vi.fn(),
}));

export default router;
