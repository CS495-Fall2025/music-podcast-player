import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("useNavbar", () => {
  let navbar;
  let alertMock;
  let mountedCallbacks = [];
  let unmountCallbacks = [];
  let clickHandler = null;

  beforeEach(async () => {
    // Reset
    mountedCallbacks = [];
    unmountCallbacks = [];
    clickHandler = null;

    // Setup alert mock
    alertMock = vi.fn();
    vi.stubGlobal("alert", alertMock);

    // Spy on document.addEventListener to capture the click handler
    const addEventListenerSpy = vi.spyOn(document, "addEventListener");
    addEventListenerSpy.mockImplementation((event, handler) => {
      if (event === "click") {
        clickHandler = handler;
      }
    });

    // Mock Vue lifecycle hooks
    vi.doMock("vue", async () => {
      const actual = await vi.importActual("vue");
      return {
        ...actual,
        onMounted: (callback) => {
          mountedCallbacks.push(callback);
          // Execute immediately in tests
          callback();
        },
        onBeforeUnmount: (callback) => {
          unmountCallbacks.push(callback);
        },
      };
    });

    // Import after mocking
    const { default: useNavbar } = await import("../src/controllers/navBar.js");
    navbar = useNavbar();
  });

  afterEach(() => {
    // Trigger cleanup
    unmountCallbacks.forEach((cb) => cb());
    vi.doUnmock("vue");
    vi.unstubAllGlobals();
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

    // Directly call the click handler
    clickHandler({ target: mockTarget });

    expect(navbar.dropdownOpen.value).toBe(false);
  });

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

  it("handleLogin shows alert and closes dropdown", () => {
    navbar.dropdownOpen.value = true;
    navbar.handleLogin();

    expect(alertMock).toHaveBeenCalledWith("Login clicked");
    expect(navbar.dropdownOpen.value).toBe(false);
  });

  it("handleLogout shows alert and closes dropdown", () => {
    navbar.dropdownOpen.value = true;
    navbar.handleLogout();

    expect(alertMock).toHaveBeenCalledWith("Logout clicked");
    expect(navbar.dropdownOpen.value).toBe(false);
  });
});
