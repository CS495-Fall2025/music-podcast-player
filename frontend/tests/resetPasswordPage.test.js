import { mount } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import ResetPasswordPage from "../src/pages/ResetPasswordPage.vue";

const pushMock = vi.fn();
const useRouteMock = vi.fn(() => ({ query: {} }));

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: pushMock }),
  useRoute: () => useRouteMock(),
}));

vi.mock("../src/config", () => ({
  default: vi.fn(async () => ({ backendUrl: "http://backend.test" })),
}));

describe("ResetPasswordPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows error when passwords do not match", async () => {
    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#reset-email").setValue("user@example.com");
    await wrapper.find("#reset-code").setValue("123456");
    await wrapper.find("#new-password").setValue("ValidPassword!234");
    await wrapper
      .find("#confirm-new-password")
      .setValue("DifferentPassword!234");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("Passwords do not match.");
  });

  it("resets password and redirects to login", async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#reset-email").setValue("user@example.com");
    await wrapper.find("#reset-code").setValue("123456");
    await wrapper.find("#new-password").setValue("ValidPassword!234");
    await wrapper.find("#confirm-new-password").setValue("ValidPassword!234");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/reset-password",
      expect.objectContaining({ method: "POST" }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith("/login");
  });

  it("prefills email from query string", async () => {
    useRouteMock.mockReturnValueOnce({
      query: { email: "prefilled@example.com" },
    });

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    const emailValue = wrapper.find("#reset-email").element.value;
    expect(emailValue).toBe("prefilled@example.com");
  });
});
