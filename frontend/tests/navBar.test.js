import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("useNavbar", () => {
  let navbar;
  let mountedCallbacks = [];
  let unmountCallbacks = [];
  let clickHandler = null;

  beforeEach(async () => {
    mountedCallbacks = [];
    unmountCallbacks = [];
    clickHandler = null;

    // Mock window.location for href and reload
    Object.defineProperty(global.window, "location", {
      value: { href: "", reload: vi.fn() },
      writable: true,
    });

    // Mock addEventListener
    const addEventListenerSpy = vi.spyOn(document, "addEventListener");
    addEventListenerSpy.mockImplementation((event, handler) => {
      if (event === "click") clickHandler = handler;
    });

    // Mock Vue lifecycle hooks
    vi.doMock("vue", async () => {
      const actual = await vi.importActual("vue");
      return {
        ...actual,
        onMounted: (callback) => {
          mountedCallbacks.push(callback);
          callback();
        },
        onBeforeUnmount: (callback) => {
          unmountCallbacks.push(callback);
        },
      };
    });

    // Mock auth functions
    vi.doMock("../src/auth/authService.js", () => ({
      startLogin: vi.fn(),
      logout: vi.fn(),
    }));

    const { default: useNavbar } = await import("../src/controllers/navBar.js");
    navbar = useNavbar();
  });

  afterEach(() => {
    unmountCallbacks.forEach((cb) => cb());
    vi.doUnmock("vue");
    vi.doUnmock("../src/auth/authService.js");
    vi.restoreAllMocks();
  });

  it("initializes with default values", () => {
    expect(navbar.isOpen.value).toBe(false);
    expect(navbar.dropdownOpen.value).toBe(false);
    expect(navbar.dropdownRef.value).toBe(null);
  });

  it("closes dropdown when clicking outside", () => {
    navbar.dropdownOpen.value = true;
    const mockDiv = document.createElement("div");
    navbar.dropdownRef.value = mockDiv;
    const mockTarget = document.createElement("div");

    clickHandler({ target: mockTarget });

    expect(navbar.dropdownOpen.value).toBe(false);
  });

  it("keeps dropdown open when clicking inside", () => {
    navbar.dropdownOpen.value = true;
    const mockDiv = document.createElement("div");
    const originalContains = mockDiv.contains.bind(mockDiv);
    mockDiv.contains = vi.fn(
      (node) => node === mockDiv || originalContains(node),
    );
    navbar.dropdownRef.value = mockDiv;

    clickHandler({ target: mockDiv });

    expect(navbar.dropdownOpen.value).toBe(true);
  });

  it("handleLogin calls startLogin and closes dropdown", async () => {
    const { startLogin } = await import("../src/auth/authService.js");

    navbar.dropdownOpen.value = true;
    navbar.handleLogin();

    expect(startLogin).toHaveBeenCalled();
    expect(navbar.dropdownOpen.value).toBe(false);
  });

  it("handleLogout calls logout, reloads window, and closes dropdown", async () => {
    const { logout } = await import("../src/auth/authService.js");

    navbar.dropdownOpen.value = true;
    navbar.handleLogout();

    expect(logout).toHaveBeenCalled();
    expect(window.location.reload).toHaveBeenCalled();
    expect(navbar.dropdownOpen.value).toBe(false);
  });
});
