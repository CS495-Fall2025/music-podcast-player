import Track from "../components/UserTrack.vue";
import { feed, feedTracks } from "./localFeedStore.js";
import {
  fetchUserPlaylists,
  createPlaylist,
  addTrackToPlaylist,
} from "../utils/playlistApi.js";

export default {
  name: "UserFeed",
  components: { Track },

  data() {
    return {
      playlistPopupOpen: false,
      popupStyle: {
        top: "0px",
        left: "0px",
      },
      selectedTrack: null,
      playlists: [],
      newPlaylistTitle: "",
      newPlaylistDescription: "",
      popupError: "",
      popupLoading: false,
    };
  },

  methods: {
    async handleAddToPlaylist({ track }) {
      this.selectedTrack = track;
      this.popupError = "";
      this.newPlaylistTitle = "";
      this.newPlaylistDescription = "";

      this.popupStyle = {
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      };

      this.playlistPopupOpen = true;
      this.popupLoading = true;

      try {
        const response = await fetchUserPlaylists();
        this.playlists = response.playlists || [];
      } catch (error) {
        this.popupError =
          error instanceof Error ? error.message : "Unable to load playlists.";
        this.playlists = [];
      } finally {
        this.popupLoading = false;
      }
    },

    closePlaylistPopup() {
      this.playlistPopupOpen = false;
      this.selectedTrack = null;
      this.popupError = "";
      this.newPlaylistTitle = "";
      this.newPlaylistDescription = "";
    },

    async handleAddTrackToPlaylist(playlistId) {
      if (!this.selectedTrack?.track_url) {
        this.popupError = "This track does not have a track URL.";
        return;
      }
    
      try {
        await addTrackToPlaylist(playlistId, this.selectedTrack.track_url);
        this.closePlaylistPopup();
      } catch (error) {
        const message = error instanceof Error ? error.message.toLowerCase() : "";
    
        if (
          message.includes("already exists") ||
          message.includes("already in") ||
          message.includes("duplicate") ||
          message.includes("409") ||
          message.includes("conflict")
        ) {
          this.popupError = "Track already exists in this playlist.";
        } else {
          this.popupError = "Could not add track to playlist.";
        }
      }
    },

    async handleCreatePlaylist() {
      const title = this.newPlaylistTitle.trim();
      const description = this.newPlaylistDescription.trim();

      if (!title) {
        this.popupError = "Enter a playlist title.";
        return;
      }

      if (!this.selectedTrack?.track_url) {
        this.popupError = "This track does not have a track URL.";
        return;
      }

      try {
        const created = await createPlaylist(title, description);
        await addTrackToPlaylist(created.id, this.selectedTrack.track_url);
        this.closePlaylistPopup();
      } catch (error) {
        this.popupError =
          error instanceof Error ? error.message : "Unable to create playlist.";
      }
    },
  },

  computed: {
    // Returns feed if a feed is loaded. If a feed is not loaded, returns mock empty feed (until a feed is loaded) to prevent crashing.
    feed() {
      return feed.length
        ? feed[0]
        : {
            image: "",
            title: "",
            artist: "",
          };
    },
    // Returns the list of track objects within the feed. Each object holds its own data.
    feedTracks() {
      return feedTracks;
    },
    // Returns the feed's image, if there's no image, returns placeholder.
    feedImage() {
      return this.feed.image || "/src/assets/images/default-image.jpg";
    },
    // Returns the feed's title, if there's no title, returns placeholder.
    feedTitle() {
      return this.feed.title || "Untitled Feed";
    },
    // Returns the feed's artist, if there's no artist, returns placeholder.
    feedArtist() {
      return this.feed.artist || "Feed artist not found";
    },
  },
};
