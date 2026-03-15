import { mount } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import ForgotPasswordPage from "../src/pages/ForgotPasswordPage.vue";

const pushMock = vi.fn();

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("../src/config", () => ({
  default: vi.fn(async () => ({ backendUrl: "http://backend.test" })),
}));

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sends forgot-password request and routes to reset page", async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(ForgotPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#forgot-email").setValue("user@example.com");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/forgot-password",
      expect.objectContaining({ method: "POST" }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith({
      path: "/reset-password",
      query: { email: "user@example.com" },
    });
  });

  it("shows validation error when email is missing", async () => {
    const wrapper = mount(ForgotPasswordPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("Please enter your email.");
  });
});
