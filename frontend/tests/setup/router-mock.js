// Mock router for all tests
import { vi } from "vitest";

export const router = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
};

vi.mock("vue-router", () => ({
  createRouter: vi.fn(() => router),
  createWebHistory: vi.fn(),
}));

export default router;
