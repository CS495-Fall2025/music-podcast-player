import { mount } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import ContactPage from "../src/pages/ContactPage.vue";

vi.mock("../src/controllers/textSanitizer", () => ({
  sanitizeText: vi.fn((text) => text),
}));

describe("ContactPage", () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(ContactPage);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("component rendering", () => {
    it("renders the contact page component", () => {
      expect(wrapper.exists()).toBe(true);
    });

    it("has a contact container", () => {
      const container = wrapper.find(".contact-container");
      expect(container.exists()).toBe(true);
    });

    it("displays the default contact content", () => {
      const content = wrapper.find(".contact-content");
      expect(content.exists()).toBe(true);
      expect(content.text()).toContain("contact@example.com");
    });

    it("renders without errors", () => {
      expect(wrapper.vm).toBeDefined();
    });
  });

  describe("startEditing", () => {
    it("changes isEditing to true when edit button is clicked", async () => {
      expect(wrapper.vm.isEditing).toBe(false);

      const editButton = wrapper.find(".edit-button button");
      await editButton.trigger("click");

      expect(wrapper.vm.isEditing).toBe(true);
    });

    it("copies savedContent to editContent when starting to edit", async () => {
      const originalContent = wrapper.vm.savedContent;

      await wrapper.vm.startEditing();

      expect(wrapper.vm.editContent).toBe(originalContent);
    });

    it("shows textarea when editing mode is active", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find(".editor");
      expect(textarea.exists()).toBe(true);
    });

    it("hides contact content when in editing mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const contactContent = wrapper.find(".contact-content");
      expect(contactContent.exists()).toBe(false);
    });
  });

  describe("saveContent", () => {
    it("saves edited content to savedContent", async () => {
      const newContent = "<h1>Updated Contact Info</h1>";
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

    it("hides textarea and shows content after saving", async () => {
      wrapper.vm.isEditing = true;
      wrapper.vm.editContent = "New content";

      await wrapper.vm.saveContent();
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find(".editor");
      const contactContent = wrapper.find(".contact-content");

      expect(textarea.exists()).toBe(false);
      expect(contactContent.exists()).toBe(true);
    });

    it("updates displayed content after saving", async () => {
      const newContent =
        "<h1>Contact Us</h1><p>Email: newemail@example.com</p>";
      wrapper.vm.editContent = newContent;

      await wrapper.vm.saveContent();
      await wrapper.vm.$nextTick();

      const displayedContent = wrapper.find(".contact-content");
      expect(displayedContent.text()).toContain("newemail@example.com");
    });
  });

  describe("checkAdmin", () => {
    it("returns true when user is admin", () => {
      const result = wrapper.vm.checkAdmin();

      expect(result).toBe(true);
      expect(wrapper.vm.isAdmin).toBe(true);
    });

    it("shows edit button only when admin", async () => {
      wrapper.vm.checkAdmin();
      await wrapper.vm.$nextTick();

      const editButton = wrapper.find(".edit-button button");
      expect(editButton.exists()).toBe(true);
    });

    it("enables editing only for admin users", async () => {
      const isAdmin = wrapper.vm.checkAdmin();
      expect(isAdmin).toBe(true);

      await wrapper.vm.startEditing();
      expect(wrapper.vm.isEditing).toBe(true);
    });
  });

  describe("cancelEditing", () => {
    it("sets isEditing to false when cancel is clicked", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const cancelButton = wrapper.findAll(".edit-actions button")[1];
      await cancelButton.trigger("click");

      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("hides textarea and shows content after canceling", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      await wrapper.vm.cancelEditing();
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find(".editor");
      const contactContent = wrapper.find(".contact-content");

      expect(textarea.exists()).toBe(false);
      expect(contactContent.exists()).toBe(true);
    });

    it("does not save changes when canceling", async () => {
      const originalContent = wrapper.vm.savedContent;
      wrapper.vm.editContent = "This should not be saved";

      await wrapper.vm.cancelEditing();

      expect(wrapper.vm.savedContent).toBe(originalContent);
    });
  });

  describe("UI interactions", () => {
    it("shows edit button when admin", async () => {
      wrapper.vm.checkAdmin();
      await wrapper.vm.$nextTick();

      const editButton = wrapper.find(".edit-button button");
      expect(editButton.exists()).toBe(true);
      expect(editButton.text()).toBe("Edit");
    });

    it("shows save and cancel buttons in edit mode", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const buttons = wrapper.findAll(".edit-actions button");
      expect(buttons).toHaveLength(2);
      expect(buttons[0].text()).toBe("Save");
      expect(buttons[1].text()).toBe("Cancel");
    });

    it("textarea has correct attributes", async () => {
      wrapper.vm.isEditing = true;
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find(".editor");
      expect(textarea.attributes("rows")).toBe("15");
      expect(textarea.attributes("placeholder")).toBe("Edit Here...");
    });
  });

  describe("end-to-end editing flow", () => {
    it("allows admin to edit and save contact content", async () => {
      const originalContent = wrapper.vm.savedContent;
      const newContent = "<h1>Contact Us</h1><p>Email: updated@example.com</p>";

      // Check admin
      const isAdmin = wrapper.vm.checkAdmin();
      expect(isAdmin).toBe(true);

      // Start editing
      await wrapper.vm.startEditing();
      expect(wrapper.vm.isEditing).toBe(true);
      expect(wrapper.vm.editContent).toBe(originalContent);

      // Modify content
      wrapper.vm.editContent = newContent;

      // Save content
      await wrapper.vm.saveContent();
      expect(wrapper.vm.savedContent).toBe(newContent);
      expect(wrapper.vm.isEditing).toBe(false);
    });

    it("allows admin to edit and cancel without saving", async () => {
      const originalContent = wrapper.vm.savedContent;
      const newContent = "<h1>This should not be saved</h1>";

      // Start editing
      await wrapper.vm.startEditing();
      expect(wrapper.vm.isEditing).toBe(true);

      // Modify content
      wrapper.vm.editContent = newContent;

      // Cancel edit
      await wrapper.vm.cancelEditing();
      expect(wrapper.vm.isEditing).toBe(false);
      expect(wrapper.vm.savedContent).toBe(originalContent);
    });
  });
});
