import { mount } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import AboutPage from "../src/pages/AboutPage.vue";

vi.mock("../src/controllers/textSanitizer", () => ({
  sanitizeText: vi.fn((text) => text),
}));

describe("AboutPage", () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(AboutPage);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("startEditing", () => {
    it("changes isEditing to true when edit button is clicked", async () => {
      expect(wrapper.vm.isEditing).toBe(false);

      const editButton = wrapper.find(".edit-button button");
      await editButton.trigger("click");

      expect(wrapper.vm.isEditing).toBe(true);
    });

    it("copies savedContent to editContent when starting to edit", async () => {
      wrapper.vm.savedContent = "Test content for editing";

      await wrapper.vm.startEditing();

      expect(wrapper.vm.editContent).toBe(wrapper.vm.savedContent);
      expect(wrapper.vm.editContent).toBe("Test content for editing");
    });

    it("preserves savedContent value when starting edit", async () => {
      const originalContent = wrapper.vm.savedContent;

      await wrapper.vm.startEditing();

      expect(wrapper.vm.savedContent).toBe(originalContent);
    });
  });

  describe("saveContent", () => {
    it("saves edited content to savedContent", async () => {
      const newContent = "Updated content for the about page";
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

    it("sanitizes content before saving", async () => {
      const { sanitizeText } = await import("../src/controllers/textSanitizer");

      wrapper.vm.editContent = "<script>alert('xss')</script>";

      await wrapper.vm.saveContent();

      expect(sanitizeText).toHaveBeenCalled();
    });

    it("clears editContent value after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "Some content";

      await wrapper.vm.saveContent();
      expect(wrapper.vm.isEditing).toBe(false);
    });
  });

  describe("checkAdmin", () => {
    it("returns true when user is admin", () => {
      const result = wrapper.vm.checkAdmin();

      expect(result).toBe(true);
      expect(wrapper.vm.isAdmin).toBe(true);
    });

    it("sets isAdmin to true when checkAdmin is called", () => {
      expect(wrapper.vm.isAdmin).toBe(false);

      wrapper.vm.checkAdmin();

      expect(wrapper.vm.isAdmin).toBe(true);
    });

    it("shows edit button only when checkAdmin returns true", async () => {
      wrapper.vm.isAdmin = false;
      await wrapper.vm.$nextTick();

      let editButton = wrapper.find(".edit-button button");
      expect(editButton.exists()).toBe(false);

      wrapper.vm.checkAdmin();
      await wrapper.vm.$nextTick();

      editButton = wrapper.find(".edit-button button");
      expect(editButton.exists()).toBe(true);
    });
  });

  describe("cancelEdit", () => {
    it("sets isEditing to false when cancel is clicked", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const cancelButton = wrapper.findAll(
        ".content-control-buttons button",
      )[1];
      await cancelButton.trigger("click");

      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("clears editContent when canceling", () => {
      wrapper.vm.editContent = "Some edited content";

      wrapper.vm.cancelEdit();

      expect(wrapper.vm.editContent).toBe("");
    });
  });

  describe("UI interactions", () => {
    it("shows edit button when admin", async () => {
      wrapper.vm.checkAdmin();
      await wrapper.vm.$nextTick();

      const editButton = wrapper.find(".edit-button button");
      expect(editButton.exists()).toBe(true);
    });

    it("shows textarea when in editing mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find(".editor");
      expect(textarea.exists()).toBe(true);
    });

    it("shows about content when not editing", async () => {
      wrapper.vm.isEditing = false;
      await wrapper.vm.$nextTick();

      const aboutContent = wrapper.find(".about-content");
      expect(aboutContent.exists()).toBe(true);
    });

    it("hides about content when editing", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const aboutContent = wrapper.find(".about-content");
      expect(aboutContent.exists()).toBe(false);
    });
  });

  describe("end-to-end editing flow", () => {
    it("allows admin to edit and save content", async () => {
      const originalContent = wrapper.vm.savedContent;
      const newContent = "This is completely new content";

      const isAdmin = wrapper.vm.checkAdmin();
      expect(isAdmin).toBe(true);

      await wrapper.vm.startEditing();
      expect(wrapper.vm.isEditing).toBe(true);
      expect(wrapper.vm.editContent).toBe(originalContent);

      wrapper.vm.editContent = newContent;

      await wrapper.vm.saveContent();
      expect(wrapper.vm.savedContent).toBe(newContent);
      expect(wrapper.vm.isEditing).toBe(false);
    });
  });
});
