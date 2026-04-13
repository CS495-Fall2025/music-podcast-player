import { mount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ref } from "vue";

import UserPage from "../src/pages/UserPage.vue";

vi.mock("../src/auth/authService", () => ({
  useAuth: () => ({
    currentUser: ref({ username: "testuser" }),
    verifyToken: vi.fn(),
  }),
}));

vi.mock("../src/utils/playlistApi", () => ({
  fetchUserPlaylists: vi.fn(async () => ({ playlists: [] })),
  fetchPlaylistDetail: vi.fn(async () => ({ tracks: [] })),
  deletePlaylist: vi.fn(async () => {}),
  removeTrackFromPlaylist: vi.fn(async () => {}),
  reorderTrackInPlaylist: vi.fn(async () => {}),
  createPlaylist: vi.fn(async () => ({ id: 1 })),
  addTrackToPlaylist: vi.fn(async () => {}),
  updatePlaylist: vi.fn(async () => {}),
}));

vi.mock("../src/config", () => ({
  default: vi.fn(async () => ({ backendUrl: "http://backend.test" })),
}));

vi.mock("../src/controllers/localFeedStore.js", () => ({
  currentTrack: { value: "" },
  feedTracks: [],
}));

describe("UserPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn(async (url) => ({
      ok: true,
      json: async () => {
        if (url.includes("/privacy")) {
          return { profile_public: true };
        }
        return {};
      },
    }));
    global.alert = vi.fn();
    global.confirm = vi.fn();
    // mock window.location
    Object.defineProperty(window, "location", {
      value: {
        origin: "http://localhost",
        assign: vi.fn(),
      },
      writable: true,
    });
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn(async () => {}),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("shareProfile", () => {
    it("copies profile URL to clipboard and shows success alert", async () => {
      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      await vm.shareProfile();

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringMatching(/.*\/user\/testuser$/),
      );
      expect(global.alert).toHaveBeenCalledWith(
        "Share link copied to clipboard.",
      );
    });

    it("shows error alert when clipboard copy fails", async () => {
      navigator.clipboard.writeText.mockRejectedValueOnce(
        new Error("Clipboard error"),
      );

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      await vm.shareProfile();

      expect(global.alert).toHaveBeenCalledWith("Could not copy share link.");
    });

    it("closes profile menu after sharing", async () => {
      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.profileMenuOpen = true;
      await vm.shareProfile();

      expect(vm.profileMenuOpen).toBe(false);
    });
  });

  describe("deleteProfile", () => {
    it("deletes profile on confirmation and redirects home", async () => {
      global.confirm.mockReturnValueOnce(true);
      global.fetch.mockImplementation(async (url) => {
        if (url.includes("/auth/me")) return { ok: true };
        return {
          ok: true,
          json: async () => ({ profile_public: true }),
        };
      });

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      await vm.deleteProfile();

      expect(global.fetch).toHaveBeenCalledWith("http://backend.test/auth/me", {
        method: "DELETE",
        credentials: "include",
      });
      expect(global.location.assign).toHaveBeenCalledWith("/");
    });

    it("does not delete on user cancellation", async () => {
      global.confirm.mockReturnValueOnce(false);

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      await vm.deleteProfile();

      expect(global.fetch).not.toHaveBeenCalledWith(
        "http://backend.test/auth/me",
        expect.objectContaining({ method: "DELETE" }),
      );
    });

    it("shows error alert on delete failure", async () => {
      global.confirm.mockReturnValueOnce(true);
      global.fetch.mockImplementation(async (url) => {
        if (url.includes("/auth/me")) return { ok: false };
        return {
          ok: true,
          json: async () => ({ profile_public: true }),
        };
      });

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      await vm.deleteProfile();

      expect(global.alert).toHaveBeenCalledWith("Could not delete profile.");
      expect(global.location.assign).not.toHaveBeenCalled();
    });

    it("closes profile menu before deletion attempt", async () => {
      global.confirm.mockReturnValueOnce(true);
      global.fetch.mockImplementation(async (url) => {
        if (url.includes("/auth/me")) return { ok: true };
        return {
          ok: true,
          json: async () => ({ profile_public: true }),
        };
      });

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.profileMenuOpen = true;
      await vm.deleteProfile();

      expect(vm.profileMenuOpen).toBe(false);
    });
  });

  describe("Playlist inline editing", () => {
    it("initializes edit state with playlist data", async () => {
      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      const playlist = {
        id: 1,
        title: "My Playlist",
        description: "A test playlist",
      };

      vm.startEditPlaylist(playlist);

      expect(vm.editingPlaylistId).toBe(1);
      expect(vm.editTitle).toBe("My Playlist");
      expect(vm.editDescription).toBe("A test playlist");
    });

    it("converts default description to empty string for editing", async () => {
      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      const playlist = {
        id: 1,
        title: "My Playlist",
        description: "No description added yet.",
      };

      vm.startEditPlaylist(playlist);

      expect(vm.editDescription).toBe("");
    });

    it("cancels editing and clears state", async () => {
      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.editingPlaylistId = 1;
      vm.editTitle = "Test";
      vm.editDescription = "Test desc";

      vm.cancelEditPlaylist();

      expect(vm.editingPlaylistId).toBe(null);
      expect(vm.editTitle).toBe("");
      expect(vm.editDescription).toBe("");
    });

    it("saves playlist edits and updates local state", async () => {
      const playlistApi = await import("../src/utils/playlistApi.js");

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.playlists = [
        {
          id: 1,
          title: "Old Title",
          description: "Old Description",
          trackCount: 5,
          createdLabel: "Apr 13, 2026",
        },
      ];
      vm.editingPlaylistId = 1;
      vm.editTitle = "New Title";
      vm.editDescription = "New Description";

      await vm.saveEditPlaylist({ id: 1 });

      expect(playlistApi.updatePlaylist).toHaveBeenCalledWith(
        1,
        "New Title",
        "New Description",
      );
      expect(vm.playlists[0].title).toBe("New Title");
      expect(vm.playlists[0].description).toBe("New Description");
      expect(vm.editingPlaylistId).toBe(null);
    });

    it("converts empty description back to default text after save", async () => {
      const playlistApi = await import("../src/utils/playlistApi.js");

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.playlists = [
        {
          id: 1,
          title: "My Playlist",
          description: "Old Description",
          trackCount: 5,
          createdLabel: "Apr 13, 2026",
        },
      ];
      vm.editingPlaylistId = 1;
      vm.editTitle = "My Playlist";
      vm.editDescription = "";

      await vm.saveEditPlaylist({ id: 1 });

      expect(vm.playlists[0].description).toBe("No description added yet.");
    });

    it("does not save if title is empty or only whitespace", async () => {
      const playlistApi = await import("../src/utils/playlistApi.js");

      const wrapper = mount(UserPage, {
        global: {
          stubs: {
            UserTrack: true,
            MiniPlayer: true,
            AddToPlaylistModal: true,
          },
        },
      });

      await flushPromises();

      const vm = wrapper.vm;
      vm.editingPlaylistId = 1;
      vm.editTitle = "   ";
      vm.editDescription = "Description";

      await vm.saveEditPlaylist({ id: 1 });

      expect(playlistApi.updatePlaylist).not.toHaveBeenCalled();
    });
  });
});
