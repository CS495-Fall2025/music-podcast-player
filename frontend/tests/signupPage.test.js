import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import SignupPage from "../src/pages/SignupPage.vue";

const pushMock = vi.fn();
const useRouteMock = vi.fn(() => ({ query: {} }));

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: pushMock }),
  useRoute: () => useRouteMock(),
}));

vi.mock("../src/config", () => ({
  default: vi.fn(async () => ({ backendUrl: "http://backend.test" })),
}));

describe("SignupPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("submits registration and routes to signup verification step", async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(SignupPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#username").setValue("validuser");
    await wrapper.find("#email").setValue("user@example.com");
    await wrapper.find("#password").setValue("ValidPassword!234");
    await wrapper.find("#confirmPassword").setValue("ValidPassword!234");
    await wrapper.find("form").trigger("submit");
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/signup",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          username: "validuser",
          email: "user@example.com",
          password: "ValidPassword!234",
        }),
      }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith({
      path: "/signup",
      query: { step: "verify" },
    });
  });

  it("renders code-only verification step and verifies with stored email", async () => {
    useRouteMock.mockReturnValueOnce({ query: { step: "verify" } });

    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(SignupPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    expect(wrapper.find("#email").exists()).toBe(false);
    expect(wrapper.find("#verification-code").exists()).toBe(true);

    await wrapper.find("#verification-code").setValue("123456");
    await wrapper.find("form").trigger("submit");
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/signup/verify",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          code: "123456",
        }),
      }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith("/login");
  });

  it("shows validation message for invalid verification code", async () => {
    useRouteMock.mockReturnValueOnce({ query: { step: "verify" } });

    const wrapper = mount(SignupPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#verification-code").setValue("12345");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain(
      "Verification code must be exactly 6 digits.",
    );
  });
});
