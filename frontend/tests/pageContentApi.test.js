import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("pageContentApi", () => {
  let fetchMock;
  let pageContentApi;

  const mockConfig = () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ backendUrl: "http://localhost:5000" }),
    });
  };

  beforeEach(async () => {
    fetchMock = vi.fn();
    global.fetch = fetchMock;
    vi.resetModules();
    pageContentApi = await import("../src/controllers/pageContentApi.js");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getPageContent", () => {
    it("returns html on success", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ page: "about", html: "<h1>About</h1>" }),
      });

      const result = await pageContentApi.getPageContent("about");

      expect(result).toBe("<h1>About</h1>");
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/pages/about"),
        expect.objectContaining({ credentials: "include" }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false, status: 404 });

      await expect(pageContentApi.getPageContent("about")).rejects.toThrow(
        "Failed to load page content: 404",
      );
    });
  });

  describe("putPageContent", () => {
    it("sends PUT with html body and returns saved html", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ page: "about", html: "<p>Updated</p>" }),
      });

      const result = await pageContentApi.putPageContent(
        "about",
        "<p>Updated</p>",
      );

      expect(result).toBe("<p>Updated</p>");
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/pages/about"),
        expect.objectContaining({
          method: "PUT",
          credentials: "include",
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({ html: "<p>Updated</p>" }),
        }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false, status: 403 });

      await expect(
        pageContentApi.putPageContent("about", "<p>x</p>"),
      ).rejects.toThrow("Failed to save page content: 403");
    });
  });
});
