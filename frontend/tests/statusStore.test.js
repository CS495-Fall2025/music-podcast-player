import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  statusState,
  setLoading,
  setError,
  clearError,
  clearStatus,
  navigateToError,
} from "../src/controllers/statusStore.js";
import router from "../src/router";

describe("statusStore module", () => {
  vi.mock("../src/router", () => ({
    default: { push: vi.fn() },
  }));

  beforeEach(() => {
    // Reset state before each test
    statusState.isLoading = false;
    statusState.error = null;
    vi.clearAllMocks();
  });

  it("setLoading updates isLoading state", () => {
    setLoading(true);
    expect(statusState.isLoading).toBe(true);

    setLoading(false);
    expect(statusState.isLoading).toBe(false);
  });

  it("setError populates the error object correctly", () => {
    const mockAction = vi.fn();
    setError("404", "Not Found", "Page missing", "Go Back", mockAction);

    expect(statusState.error).toEqual({
      type: "404",
      title: "Not Found",
      message: "Page missing",
      actionText: "Go Back",
      onAction: mockAction,
    });
  });

  it("clearError nullifies the error object but keeps loading state", () => {
    statusState.isLoading = true;
    setError("500", "Server Error", "Whoops");

    clearError();

    expect(statusState.error).toBeNull();
    expect(statusState.isLoading).toBe(true); // Should not affect isLoading
  });

  it("clearStatus resets both loading and error states", () => {
    setLoading(true);
    setError("error", "Title", "Message");

    clearStatus();

    expect(statusState.isLoading).toBe(false);
    expect(statusState.error).toBeNull();
  });

  it("navigateToError sets error, stops loading, and pushes to router", () => {
    statusState.isLoading = true;
    const mockAction = vi.fn();

    navigateToError("fatal", "Crash", "System failure", "Reboot", mockAction);

    expect(statusState.error).toEqual({
      type: "fatal",
      title: "Crash",
      message: "System failure",
      actionText: "Reboot",
      onAction: mockAction,
    });

    expect(statusState.isLoading).toBe(false);

    expect(router.push).toHaveBeenCalledWith("/error");
  });
});
