import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ref, computed } from "vue";

import AboutPage from "../src/pages/AboutPage.vue";

vi.mock("../src/controllers/textSanitizer", () => ({
  sanitizeText: vi.fn((text) => text),
}));

vi.mock("../src/controllers/pageContentApi", () => ({
  getPageContent: vi.fn(() => Promise.resolve("<h1>About</h1>")),
  putPageContent: vi.fn((page, html) => Promise.resolve(html)),
}));

const mockIsAdmin = ref(false);
vi.mock("../src/auth/authStore", () => ({
  useAuth: () => ({
    currentUserIsAdmin: computed(() => mockIsAdmin.value),
  }),
}));

describe("AboutPage", () => {
  let wrapper;

  beforeEach(async () => {
    mockIsAdmin.value = false;
    wrapper = mount(AboutPage);
    await flushPromises();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("onMounted", () => {
    it("loads content from the API on mount", async () => {
      const { getPageContent } = await import("../src/controllers/pageContentApi");
      expect(getPageContent).toHaveBeenCalledWith("about");
      expect(wrapper.vm.savedContent).toBe("<h1>About</h1>");
    });

    it("shows load error when API call fails", async () => {
      const { getPageContent } = await import("../src/controllers/pageContentApi");
      getPageContent.mockRejectedValueOnce(new Error("Network error"));
      const w = mount(AboutPage);
      await flushPromises();
      expect(w.vm.loadError).toBeTruthy();
    });
  });

  describe("admin visibility", () => {
    it("hides edit button when user is not admin", async () => {
      mockIsAdmin.value = false;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".edit-button button").exists()).toBe(false);
    });

    it("shows edit button when user is admin", async () => {
      mockIsAdmin.value = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".edit-button button").exists()).toBe(true);
    });
  });

  describe("startEditing", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("sets isEditing to true when edit button is clicked", async () => {
      await wrapper.vm.$nextTick();
      await wrapper.find(".edit-button button").trigger("click");
      expect(wrapper.vm.isEditing).toBe(true);
    });

    it("copies savedContent to editContent", async () => {
      wrapper.vm.savedContent = "Existing content";
      await wrapper.vm.startEditing();
      expect(wrapper.vm.editContent).toBe("Existing content");
    });

    it("preserves savedContent when starting edit", async () => {
      const original = wrapper.vm.savedContent;
      await wrapper.vm.startEditing();
      expect(wrapper.vm.savedContent).toBe(original);
    });
  });

  describe("saveContent", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("calls putPageContent with sanitized html", async () => {
      const { putPageContent } = await import("../src/controllers/pageContentApi");
      const { sanitizeText } = await import("../src/controllers/textSanitizer");
      wrapper.vm.editContent = "<p>New</p>";
      await wrapper.vm.saveContent();
      expect(sanitizeText).toHaveBeenCalled();
      expect(putPageContent).toHaveBeenCalledWith("about", "<p>New</p>");
    });

    it("sets isEditing to false after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "content";
      await wrapper.vm.saveContent();
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("sanitizes xss content before saving", async () => {
      const { sanitizeText } = await import("../src/controllers/textSanitizer");
      wrapper.vm.editContent = "xss-payload";
      await wrapper.vm.saveContent();
      expect(sanitizeText).toHaveBeenCalled();
    });

    it("shows saveError when putPageContent rejects", async () => {
      const { putPageContent } = await import("../src/controllers/pageContentApi");
      putPageContent.mockRejectedValueOnce(new Error("Save failed"));
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "content";
      await wrapper.vm.saveContent();
      expect(wrapper.vm.saveError).toBeTruthy();
      expect(wrapper.vm.isEditing).toBe(true);
    });
  });

  describe("cancelEdit", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("sets isEditing to false", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      const cancelBtn = wrapper.findAll(".content-control-buttons button")[1];
      await cancelBtn.trigger("click");
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("clears editContent", () => {
      wrapper.vm.editContent = "Something";
      wrapper.vm.cancelEdit();
      expect(wrapper.vm.editContent).toBe("");
    });
  });

  describe("UI interactions", () => {
    it("shows textarea when editing", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(true);
    });

    it("shows about-content when not editing", async () => {
      wrapper.vm.isEditing = false;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".about-content").exists()).toBe(true);
    });

    it("hides about-content when editing", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".about-content").exists()).toBe(false);
    });
  });
});