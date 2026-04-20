import { describe, it, expect, beforeEach } from "vitest";
import {
  statusState,
  setLoading,
  setError,
  clearError,
  clearStatus,
} from "../src/controllers/statusStore.js";

describe("statusStore", () => {
  beforeEach(() => {
    clearStatus();
  });

  it("setLoading updates the isLoading state correctly", () => {
    expect(statusState.isLoading).toBe(false);

    setLoading(true);
    expect(statusState.isLoading).toBe(true);

    setLoading(false);
    expect(statusState.isLoading).toBe(false);
  });

  it("setError sets the error object with all provided properties", () => {
    const mockAction = () => {};

    setError(
      "network-error",
      "Timeout",
      "Connection took too long.",
      "Retry",
      mockAction,
    );

    expect(statusState.error).toEqual({
      type: "network-error",
      title: "Timeout",
      message: "Connection took too long.",
      actionText: "Retry",
      onAction: mockAction,
    });
  });

  it("setError handles default parameters correctly", () => {
    setError("generic-error", "Oops", "Something went wrong.");

    expect(statusState.error).toEqual({
      type: "generic-error",
      title: "Oops",
      message: "Something went wrong.",
      actionText: null,
      onAction: null,
    });
  });

  it("clearError nullifies the error object but leaves isLoading intact", () => {
    setLoading(true);
    setError("error", "Title", "Message");

    clearError();

    expect(statusState.error).toBeNull();
    expect(statusState.isLoading).toBe(true);
  });

  it("clearStatus resets both isLoading and error states", () => {
    setLoading(true);
    setError("error", "Title", "Message");

    clearStatus();

    expect(statusState.isLoading).toBe(false);
    expect(statusState.error).toBeNull();
  });
});
