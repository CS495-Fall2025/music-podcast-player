import { mount } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";

import AboutPage from "../src/pages/AboutPage.vue";
import EditablePage from "../src/components/EditablePage.vue";

vi.mock("../src/components/EditablePage.vue", () => ({
  default: {
    name: "EditablePage",
    props: ["page"],
    template: "<div class='editable-page-stub'></div>",
  },
}));

describe("AboutPage", () => {
  it("renders EditablePage with page='about'", () => {
    const wrapper = mount(AboutPage);
    const child = wrapper.findComponent(EditablePage);
    expect(child.exists()).toBe(true);
    expect(child.props("page")).toBe("about");
  });
});
