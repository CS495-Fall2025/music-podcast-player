import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ref, computed } from "vue";

import ContactPage from "../src/pages/ContactPage.vue";

vi.mock("../src/controllers/textSanitizer", () => ({
  sanitizeText: vi.fn((text) => text),
}));

vi.mock("../src/controllers/pageContentApi", () => ({
  getPageContent: vi.fn(() => Promise.resolve("<h1>Contact</h1>")),
  putPageContent: vi.fn((page, html) => Promise.resolve(html)),
}));

const mockIsAdmin = ref(false);
vi.mock("../src/auth/authStore", () => ({
  useAuth: () => ({
    currentUserIsAdmin: computed(() => mockIsAdmin.value),
  }),
}));

describe("ContactPage", () => {
  let wrapper;

  beforeEach(async () => {
    mockIsAdmin.value = false;
    wrapper = mount(ContactPage);
    await flushPromises();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("component rendering", () => {
    it("renders the contact page component", () => {
      expect(wrapper.exists()).toBe(true);
    });

    it("has a contact container", () => {
      expect(wrapper.find(".contact-container").exists()).toBe(true);
    });

    it("renders without errors", () => {
      expect(wrapper.vm).toBeDefined();
    });
  });

  describe("onMounted", () => {
    it("loads content from the API on mount", async () => {
      const { getPageContent } = await import("../src/controllers/pageContentApi");
      expect(getPageContent).toHaveBeenCalledWith("contact");
      expect(wrapper.vm.savedContent).toBe("<h1>Contact</h1>");
    });

    it("shows load error when API call fails", async () => {
      const { getPageContent } = await import("../src/controllers/pageContentApi");
      getPageContent.mockRejectedValueOnce(new Error("Network error"));
      const w = mount(ContactPage);
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

    it("changes isEditing to true when edit button is clicked", async () => {
      await wrapper.vm.$nextTick();
      await wrapper.find(".edit-button button").trigger("click");
      expect(wrapper.vm.isEditing).toBe(true);
    });

    it("copies savedContent to editContent", async () => {
      const original = wrapper.vm.savedContent;
      await wrapper.vm.startEditing();
      expect(wrapper.vm.editContent).toBe(original);
    });

    it("shows textarea when editing mode is active", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(true);
    });

    it("hides contact content when in editing mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".contact-content").exists()).toBe(false);
    });
  });

  describe("saveContent", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("saves edited content to savedContent", async () => {
      const { putPageContent } = await import("../src/controllers/pageContentApi");
      const newContent = "<h1>Updated Contact Info</h1>";
      putPageContent.mockResolvedValueOnce(newContent);
      wrapper.vm.editContent = newContent;
      await wrapper.vm.saveContent();
      expect(wrapper.vm.savedContent).toBe(newContent);
    });

    it("sets isEditing to false after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "New content";
      await wrapper.vm.saveContent();
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("sends raw content to API for server-side sanitization", async () => {
      const { putPageContent } = await import("../src/controllers/pageContentApi");
      wrapper.vm.editContent = "<script>alert('xss')</script>";
      await wrapper.vm.saveContent();
      expect(putPageContent).toHaveBeenCalledWith("contact", "<script>alert('xss')</script>");
    });

    it("hides textarea and shows content after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "New content";
      await wrapper.vm.saveContent();
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(false);
      expect(wrapper.find(".contact-content").exists()).toBe(true);
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

  describe("cancelEditing", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("sets isEditing to false when cancel is clicked", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      const cancelBtn = wrapper.findAll(".edit-actions button")[1];
      await cancelBtn.trigger("click");
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("hides textarea and shows content after canceling", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      await wrapper.vm.cancelEditing();
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(false);
      expect(wrapper.find(".contact-content").exists()).toBe(true);
    });

    it("does not save changes when canceling", async () => {
      const original = wrapper.vm.savedContent;
      wrapper.vm.editContent = "This should not be saved";
      await wrapper.vm.cancelEditing();
      expect(wrapper.vm.savedContent).toBe(original);
    });
  });

  describe("UI interactions", () => {
    beforeEach(() => { mockIsAdmin.value = true; });

    it("shows edit button when admin", async () => {
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".edit-button button").text()).toBe("Edit");
    });

    it("shows save and cancel buttons in edit mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      const btns = wrapper.findAll(".edit-actions button");
      expect(btns[0].text()).toContain("Save");
      expect(btns[1].text()).toBe("Cancel");
    });
  });
});