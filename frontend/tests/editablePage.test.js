import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ref, computed } from "vue";

import EditablePage from "../src/components/EditablePage.vue";

vi.mock("../src/controllers/pageContentApi", () => ({
  getPageContent: vi.fn(() => Promise.resolve("<h1>Page Content</h1>")),
  putPageContent: vi.fn((page, html) => Promise.resolve(html)),
}));

const mockIsAdmin = ref(false);
vi.mock("../src/auth/authStore", () => ({
  useAuth: () => ({
    currentUserIsAdmin: computed(() => mockIsAdmin.value),
  }),
}));

describe("EditablePage", () => {
  let wrapper;

  beforeEach(async () => {
    mockIsAdmin.value = false;
    wrapper = mount(EditablePage, { props: { page: "about" } });
    await flushPromises();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("onMounted", () => {
    it("loads content from the API on mount using the page prop", async () => {
      const { getPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      expect(getPageContent).toHaveBeenCalledWith("about");
      expect(wrapper.vm.savedContent).toBe("<h1>Page Content</h1>");
    });

    it("uses the page prop when fetching content", async () => {
      const { getPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      mount(EditablePage, { props: { page: "contact" } });
      await flushPromises();
      expect(getPageContent).toHaveBeenCalledWith("contact");
    });

    it("shows load error when API call fails", async () => {
      const { getPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      getPageContent.mockRejectedValueOnce(new Error("Network error"));
      const w = mount(EditablePage, { props: { page: "about" } });
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
    beforeEach(() => {
      mockIsAdmin.value = true;
    });

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

    it("shows textarea when editing mode is active", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(true);
    });

    it("hides page content when in editing mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".page-content").exists()).toBe(false);
    });
  });

  describe("saveContent", () => {
    beforeEach(() => {
      mockIsAdmin.value = true;
    });

    it("calls putPageContent with the page prop and edited html", async () => {
      const { putPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      wrapper.vm.editContent = "<p>New</p>";
      await wrapper.vm.saveContent();
      expect(putPageContent).toHaveBeenCalledWith("about", "<p>New</p>");
    });

    it("uses the page prop when saving", async () => {
      const { putPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      const w = mount(EditablePage, { props: { page: "contact" } });
      await flushPromises();
      w.vm.editContent = "<p>Contact</p>";
      await w.vm.saveContent();
      expect(putPageContent).toHaveBeenCalledWith("contact", "<p>Contact</p>");
    });

    it("updates savedContent with the confirmed value after saving", async () => {
      const { putPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      const newContent = "<h1>Updated</h1>";
      putPageContent.mockResolvedValueOnce(newContent);
      wrapper.vm.editContent = newContent;
      await wrapper.vm.saveContent();
      expect(wrapper.vm.savedContent).toBe(newContent);
    });

    it("sets isEditing to false after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "content";
      await wrapper.vm.saveContent();
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("sends raw content to API for server-side sanitization", async () => {
      const { putPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      wrapper.vm.editContent = "<script>alert('xss')</script>";
      await wrapper.vm.saveContent();
      expect(putPageContent).toHaveBeenCalledWith(
        "about",
        "<script>alert('xss')</script>",
      );
    });

    it("hides textarea and shows content after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "New content";
      await wrapper.vm.saveContent();
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(false);
      expect(wrapper.find(".page-content").exists()).toBe(true);
    });

    it("shows saveError and keeps editing when putPageContent rejects", async () => {
      const { putPageContent } = await import(
        "../src/controllers/pageContentApi"
      );
      putPageContent.mockRejectedValueOnce(new Error("Save failed"));
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "content";
      await wrapper.vm.saveContent();
      expect(wrapper.vm.saveError).toBeTruthy();
      expect(wrapper.vm.isEditing).toBe(true);
    });
  });

  describe("cancelEdit", () => {
    beforeEach(() => {
      mockIsAdmin.value = true;
    });

    it("sets isEditing to false", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      const cancelBtn = wrapper.findAll(".edit-actions button")[1];
      await cancelBtn.trigger("click");
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("clears editContent", () => {
      wrapper.vm.editContent = "Something";
      wrapper.vm.cancelEdit();
      expect(wrapper.vm.editContent).toBe("");
    });

    it("does not save changes when canceling", async () => {
      const original = wrapper.vm.savedContent;
      wrapper.vm.editContent = "This should not be saved";
      wrapper.vm.cancelEdit();
      expect(wrapper.vm.savedContent).toBe(original);
    });

    it("hides textarea and shows content after canceling", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();
      wrapper.vm.cancelEdit();
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".editor").exists()).toBe(false);
      expect(wrapper.find(".page-content").exists()).toBe(true);
    });
  });

  describe("UI interactions", () => {
    beforeEach(() => {
      mockIsAdmin.value = true;
    });

    it("shows edit button text when admin", async () => {
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
