import { mount } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";

import ContactPage from "../src/pages/ContactPage.vue";
import EditablePage from "../src/components/EditablePage.vue";

vi.mock("../src/components/EditablePage.vue", () => ({
  default: {
    name: "EditablePage",
    props: ["page"],
    template: "<div class='editable-page-stub'></div>",
  },
}));

describe("ContactPage", () => {
  it("renders EditablePage with page='contact'", () => {
    const wrapper = mount(ContactPage);
    const child = wrapper.findComponent(EditablePage);
    expect(child.exists()).toBe(true);
    expect(child.props("page")).toBe("contact");
  });
});
