import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("useAuth", () => {
  let useAuth;
  let fetchMock;

	// mock config.json
  const mockConfig = () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ backendUrl: "http://localhost:5000" }),
    });
  };

  beforeEach(async () => {
    vi.useFakeTimers();

    // Mock fetch
    fetchMock = vi.fn();
    global.fetch = fetchMock;

    // Mock console methods
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(console, "log").mockImplementation(() => {});

    // Import fresh module for each test
    vi.resetModules();
    const authStore = await import("../src/auth/authStore.js");
    useAuth = authStore.useAuth;
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe("initial state", () => {
    it("should start unauthenticated", () => {
      const auth = useAuth();
      expect(auth.isAuthenticated.value).toBe(false);
      expect(auth.currentUser.value).toBe(null);
    });
  });

  describe("verifyToken", () => {
    it("should verify valid token and update state", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: {
            username: "testuser",
            email: "test@example.com",
          },
        }),
      });

      const result = await auth.verifyToken();

      expect(result).toBe(true);
      expect(auth.isAuthenticated.value).toBe(true);
      expect(auth.currentUser.value).toEqual({
        username: "testuser",
        email: "test@example.com",
      });
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/auth/verify"),
        expect.objectContaining({
          method: "POST",
          credentials: "include",
        }),
      );
    });

    it("should handle invalid token", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: false,
      });

      const result = await auth.verifyToken();

      expect(result).toBe(false);
      expect(auth.isAuthenticated.value).toBe(false);
      expect(auth.currentUser.value).toBe(null);
    });

    it("should handle network errors gracefully", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockRejectedValueOnce(new Error("Network error"));

      const result = await auth.verifyToken();

      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith(
        "Failed to verify token:",
        expect.any(Error),
      );
    });

    it("should return false when response is valid but token is invalid", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      const result = await auth.verifyToken();

      expect(result).toBe(false);
      expect(auth.isAuthenticated.value).toBe(false);
    });
  });

  describe("completeLogin", () => {
    it("should complete login when token is valid", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: {
            username: "testuser",
            email: "test@example.com",
          },
        }),
      });

      await auth.completeLogin();

      expect(auth.isAuthenticated.value).toBe(true);
      expect(auth.currentUser.value).toEqual({
        username: "testuser",
        email: "test@example.com",
      });
    });

    it("should start auto-refresh after successful login", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });

      await auth.completeLogin();

      expect(auth.isAuthenticated.value).toBe(true);

      // Verify auto-refresh is scheduled
      expect(vi.getTimerCount()).toBe(1);
    });

    it("should not set authenticated state when token is invalid", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: false,
      });

      await auth.completeLogin();

      expect(auth.isAuthenticated.value).toBe(false);
      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe("logout", () => {
    it("should call logout endpoint and clear state", async () => {
      const auth = useAuth();

			mockConfig();
      // Setup authenticated state
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });
      await auth.completeLogin();

			mockConfig();
      // Mock logout endpoint
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await auth.logout();

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/auth/logout"),
        expect.objectContaining({
          method: "POST",
          credentials: "include",
        }),
      );
      expect(auth.isAuthenticated.value).toBe(false);
      expect(auth.currentUser.value).toBe(null);
    });

    it("should clear state even if logout endpoint fails", async () => {
      const auth = useAuth();

			mockConfig();
      // Setup authenticated state
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });
      await auth.completeLogin();

			mockConfig();
      // Mock logout endpoint failure
      fetchMock.mockRejectedValueOnce(new Error("Network error"));

      await auth.logout();

      expect(auth.isAuthenticated.value).toBe(false);
      expect(auth.currentUser.value).toBe(null);
    });

    it("should stop auto-refresh on logout", async () => {
      const auth = useAuth();

			mockConfig();
      // Setup authenticated state
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });
      await auth.completeLogin();

      expect(vi.getTimerCount()).toBe(1);

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await auth.logout();

      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe("refreshToken", () => {
    it("should refresh token successfully", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const result = await auth.refreshToken();

      expect(result).toBe(true);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/auth/refresh"),
        expect.objectContaining({
          method: "POST",
          credentials: "include",
        }),
      );
    });

    it("should logout when refresh fails", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: false,
      });

			mockConfig();
      // Mock logout endpoint
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const result = await auth.refreshToken();

      expect(result).toBe(false);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/auth/logout"),
        expect.any(Object),
      );
    });

    it("should handle network errors", async () => {
      const auth = useAuth();

			mockConfig();
      fetchMock.mockRejectedValueOnce(new Error("Network error"));

      const result = await auth.refreshToken();

      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith(
        "Failed to refresh token:",
        expect.any(Error),
      );
    });
  });

  describe("auto-refresh", () => {
    it("should refresh token every 30 minutes", async () => {
      const auth = useAuth();

			mockConfig();
      // Complete login to start auto-refresh
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });
      await auth.completeLogin();

			mockConfig();
      // Mock successful refresh
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      // Advance time by 30 minutes
      await vi.advanceTimersByTimeAsync(30 * 60 * 1000);

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/auth/refresh"),
        expect.any(Object),
      );
    });

    it("should stop auto-refresh when refresh fails", async () => {
      const auth = useAuth();

			mockConfig();
      // Complete login to start auto-refresh
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          user: { username: "testuser", email: "test@example.com" },
        }),
      });
      await auth.completeLogin();

			mockConfig();
      // Mock failed refresh (will trigger logout)
      fetchMock.mockResolvedValueOnce({ ok: false });
			mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      }); // logout

      // Advance time by 30 minutes
      await vi.advanceTimersByTimeAsync(30 * 60 * 1000);

      // Timer should be cleared after failed refresh
      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe("startLogin", () => {
    it("should redirect to login page", () => {
      const auth = useAuth();
      const originalLocation = window.location;

      delete window.location;
      window.location = { href: "" };

      auth.startLogin();

      expect(window.location.href).toBe("/login");

      window.location = originalLocation;
    });
  });
});
