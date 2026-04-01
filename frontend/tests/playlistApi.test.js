import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("playlistApi", () => {
  let fetchMock;
  let playlistApi;

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
    playlistApi = await import("../src/utils/playlistApi.js");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("fetchUserPlaylists", () => {
    it("returns playlists on success", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ playlists: [{ id: 1, title: "My Playlist" }] }),
      });

      const result = await playlistApi.fetchUserPlaylists();

      expect(result.playlists).toHaveLength(1);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/me"),
        expect.objectContaining({ credentials: "include" }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(playlistApi.fetchUserPlaylists()).rejects.toThrow(
        "Unable to load playlist data.",
      );
    });
  });

  describe("fetchPlaylistDetail", () => {
    it("returns playlist detail on success", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 5, title: "Road Trip", tracks: [] }),
      });

      const result = await playlistApi.fetchPlaylistDetail(5);

      expect(result.id).toBe(5);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/5"),
        expect.objectContaining({ credentials: "include" }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(playlistApi.fetchPlaylistDetail(5)).rejects.toThrow(
        "Unable to load playlist tracks.",
      );
    });
  });

  describe("removeTrackFromPlaylist", () => {
    it("sends DELETE with track_url in body", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "Track removed" }),
      });

      await playlistApi.removeTrackFromPlaylist(
        5,
        "http://example.com/feed.rss",
      );

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/5/tracks/remove"),
        expect.objectContaining({
          method: "DELETE",
          credentials: "include",
          body: JSON.stringify({ track_url: "http://example.com/feed.rss" }),
        }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(
        playlistApi.removeTrackFromPlaylist(5, "http://example.com/feed.rss"),
      ).rejects.toThrow("Unable to remove track.");
    });
  });

  describe("reorderTrackInPlaylist", () => {
    it("sends PATCH with track_url and new_position", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ position: 3 }),
      });

      await playlistApi.reorderTrackInPlaylist(
        5,
        "http://example.com/feed.rss",
        3,
      );

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/5/tracks/reorder"),
        expect.objectContaining({
          method: "PATCH",
          credentials: "include",
          body: JSON.stringify({
            track_url: "http://example.com/feed.rss",
            new_position: 3,
          }),
        }),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(
        playlistApi.reorderTrackInPlaylist(5, "http://example.com/feed.rss", 2),
      ).rejects.toThrow("Unable to reorder track.");
    });
  });

  describe("fetchPublicUserPlaylists", () => {
    it("fetches playlists for a username without credentials", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          playlists: [{ id: 1, title: "Public Playlist" }],
        }),
      });

      const result = await playlistApi.fetchPublicUserPlaylists("musicfan");

      expect(result.playlists).toHaveLength(1);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/user/musicfan"),
      );
      // Should NOT send credentials
      const callArgs = fetchMock.mock.calls[1];
      expect(callArgs[1]).toBeUndefined();
    });

    it("throws when user not found or private", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(
        playlistApi.fetchPublicUserPlaylists("secretuser"),
      ).rejects.toThrow("User not found.");
    });
  });

  describe("fetchPublicPlaylistDetail", () => {
    it("fetches public playlist without credentials", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 3, title: "Shared Playlist", tracks: [] }),
      });

      const result = await playlistApi.fetchPublicPlaylistDetail(3);

      expect(result.id).toBe(3);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/playlists/public/3"),
      );
    });

    it("throws on non-ok response", async () => {
      mockConfig();
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(playlistApi.fetchPublicPlaylistDetail(3)).rejects.toThrow(
        "Unable to load playlist tracks.",
      );
    });
  });
});
