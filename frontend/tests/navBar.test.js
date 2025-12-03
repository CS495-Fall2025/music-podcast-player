import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("useNavbar", () => {
  let navbar;
  let alertMock;
  let mountedCallbacks = [];
  let unmountCallbacks = [];
  let clickHandler = null;

  // Setup mocks and import navbar controller before each test
  beforeEach(async () => {
    mountedCallbacks = [];
    unmountCallbacks = [];
    clickHandler = null;

    alertMock = vi.fn();
    vi.stubGlobal("alert", alertMock);

    const addEventListenerSpy = vi.spyOn(document, "addEventListener");
    addEventListenerSpy.mockImplementation((event, handler) => {
      if (event === "click") {
        clickHandler = handler;
      }
    });

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

    const { default: useNavbar } = await import("../src/controllers/navBar.js");
    navbar = useNavbar();
  });

  // Clean up mocks after each test
  afterEach(() => {
    unmountCallbacks.forEach((cb) => cb());
    vi.doUnmock("vue");
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  // Test initial state of navbar
  it("initializes with default values", () => {
    expect(navbar.isOpen.value).toBe(false);
    expect(navbar.dropdownOpen.value).toBe(false);
    expect(navbar.dropdownRef.value).toBe(null);
  });

  // Test dropdown closes when clicking outside the element
  it("closes dropdown when clicking outside", () => {
    navbar.dropdownOpen.value = true;
    const mockDiv = document.createElement("div");
    navbar.dropdownRef.value = mockDiv;

    const mockTarget = document.createElement("div");

    clickHandler({ target: mockTarget });

    expect(navbar.dropdownOpen.value).toBe(false);
  });

  // Test dropdown stays open when clicking inside the element
  it("keeps dropdown open when clicking inside", () => {
    navbar.dropdownOpen.value = true;
    const mockDiv = document.createElement("div");
    const originalContains = mockDiv.contains.bind(mockDiv);
    mockDiv.contains = vi.fn((node) => {
      return node === mockDiv || originalContains(node);
    });

    navbar.dropdownRef.value = mockDiv;

    clickHandler({ target: mockDiv });

    expect(navbar.dropdownOpen.value).toBe(true);
  });

  // Test login handler shows alert and closes dropdown
  it("handleLogin shows alert and closes dropdown", () => {
    navbar.dropdownOpen.value = true;
    navbar.handleLogin();

    expect(alertMock).toHaveBeenCalledWith("Login clicked");
    expect(navbar.dropdownOpen.value).toBe(false);
  });

  // Test logout handler shows alert and closes dropdown
  it("handleLogout shows alert and closes dropdown", () => {
    navbar.dropdownOpen.value = true;
    navbar.handleLogout();

    expect(alertMock).toHaveBeenCalledWith("Logout clicked");
    expect(navbar.dropdownOpen.value).toBe(false);
  });
});
