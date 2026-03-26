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
    sessionStorage.clear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows validation error when reset code is not 6 digits", async () => {
    sessionStorage.setItem("pending_reset_email", "user@example.com");

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#reset-code").setValue("12345");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("Reset code must be exactly 6 digits.");
  });

  it("stores reset code and routes to new password step", async () => {
    sessionStorage.setItem("pending_reset_email", "user@example.com");

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#reset-code").setValue("123456");
    await wrapper.find("form").trigger("submit");

    expect(sessionStorage.getItem("pending_reset_code")).toBe("123456");
    expect(pushMock).toHaveBeenCalledWith({
      path: "/reset-password",
      query: { step: "new-password" },
    });
  });

  it("shows error when passwords do not match on new-password step", async () => {
    sessionStorage.setItem("pending_reset_email", "user@example.com");
    sessionStorage.setItem("pending_reset_code", "123456");
    useRouteMock.mockReturnValueOnce({ query: { step: "new-password" } });

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#new-password").setValue("ValidPassword!234");
    await wrapper
      .find("#confirm-new-password")
      .setValue("DifferentPassword!234");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("Passwords do not match.");
  });

  it("resets password and redirects to login from new-password step", async () => {
    sessionStorage.setItem("pending_reset_email", "user@example.com");
    sessionStorage.setItem("pending_reset_code", "123456");
    useRouteMock.mockReturnValueOnce({ query: { step: "new-password" } });
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(ResetPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#new-password").setValue("ValidPassword!234");
    await wrapper.find("#confirm-new-password").setValue("ValidPassword!234");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/reset-password",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          email: "user@example.com",
          code: "123456",
          new_password: "ValidPassword!234",
        }),
      }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith("/login");
    expect(sessionStorage.getItem("pending_reset_email")).toBe(null);
    expect(sessionStorage.getItem("pending_reset_code")).toBe(null);
  });
});
