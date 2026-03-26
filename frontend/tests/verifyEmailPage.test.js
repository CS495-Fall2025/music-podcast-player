import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import VerifyEmailPage from "../src/pages/VerifyEmailPage.vue";

const pushMock = vi.fn();
const useRouteMock = vi.fn(() => ({ query: {} }));

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: pushMock }),
  useRoute: () => useRouteMock(),
}));

vi.mock("../src/config", () => ({
  default: vi.fn(async () => ({ backendUrl: "http://backend.test" })),
}));

describe("VerifyEmailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("verifies email and redirects to login", async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(VerifyEmailPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#verify-email").setValue("user@example.com");
    await wrapper.find("#verify-code").setValue("123456");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/verify-email",
      expect.objectContaining({ method: "POST" }),
    );

    await vi.runAllTimersAsync();

    expect(pushMock).toHaveBeenCalledWith("/login");
  });

  it("blocks submit for invalid verification code", async () => {
    const wrapper = mount(VerifyEmailPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#verify-email").setValue("user@example.com");
    await wrapper.find("#verify-code").setValue("12345");
    await wrapper.find("form").trigger("submit");

    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain(
      "Verification code must be exactly 6 digits.",
    );
  });

  it("resends verification code", async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const wrapper = mount(VerifyEmailPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    await wrapper.find("#verify-email").setValue("user@example.com");
    await wrapper.find("button.secondary-button").trigger("click");
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://backend.test/auth/resend-verification",
      expect.objectContaining({ method: "POST" }),
    );
    expect(wrapper.text()).toContain(
      "If your account exists, a new verification code has been sent.",
    );
  });

  it("prefills email from query string", async () => {
    useRouteMock.mockReturnValueOnce({
      query: { email: "prefilled@example.com" },
    });

    const wrapper = mount(VerifyEmailPage, {
      global: {
        stubs: {
          "router-link": true,
        },
      },
    });

    const emailValue = wrapper.find("#verify-email").element.value;
    expect(emailValue).toBe("prefilled@example.com");
  });
});
