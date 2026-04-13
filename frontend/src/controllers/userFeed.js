import Track from "../components/UserTrack.vue";
import AddToPlaylistModal from "../components/AddToPlaylistModal.vue";
import { feed, feedTracks } from "./localFeedStore.js";
import { fetchUserPlaylists, createPlaylist, addTrackToPlaylist } from "../utils/playlistApi.js";

export default {
  name: "UserFeed",
  components: { Track, AddToPlaylistModal },

  data() {
    return {
      modalOpen: false,
      selectedTrack: null,
      playlists: [],
      loading: false,
      error: "",
    };
  },

  methods: {
    async handleAddToPlaylist(track) {
      this.selectedTrack = track;
      this.error = "";
      this.modalOpen = true;
      this.loading = true;

      try {
        const res = await fetchUserPlaylists();
        this.playlists = res.playlists || [];
      } catch {
        this.error = "Unable to load playlists.";
        this.playlists = [];
      } finally {
        this.loading = false;
      }
    },

    async handleSelectPlaylist(playlist) {
      if (!this.selectedTrack?.audio) return;
      try {
        await addTrackToPlaylist(playlist.id, this.selectedTrack.audio, this.selectedTrack.feed_url);
        this.closeModal();
      } catch (e) {
        const msg = e.message?.toLowerCase() ?? "";
        this.error = msg.includes("unique") || msg.includes("already") || msg.includes("409")
          ? "Track is already in this playlist."
          : "Could not add track.";
      }
    },

    async handleCreatePlaylist({ title, description }) {
      if (!title) {
        this.error = "Enter a playlist name.";
        return;
      }
      if (!this.selectedTrack?.audio) return;
      try {
        const playlist = await createPlaylist(title, description);
        await addTrackToPlaylist(playlist.id, this.selectedTrack.audio, this.selectedTrack.feed_url);
        this.closeModal();
      } catch {
        this.error = "Could not create playlist.";
      }
    },

    closeModal() {
      this.modalOpen = false;
      this.selectedTrack = null;
      this.error = "";
    },
  },

  computed: {
    feed() {
      return feed.length
        ? feed[0]
        : {
            image: "",
            title: "",
            artist: "",
          };
    },
    feedTracks() {
      return feedTracks;
    },
    feedImage() {
      return this.feed.image || "/src/assets/images/default-image.jpg";
    },
    feedTitle() {
      if (this.feed.title === "Unknown") return "";
      return this.feed.title;
    },
    feedArtist() {
      if (this.feed.artist === "Unknown") return "";
      return this.feed.artist;
    },
  },
};
