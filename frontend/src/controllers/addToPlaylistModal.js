import loadConfig from "../config";

export default {
  name: "AddToPlaylistModal",

  emits: ["close"],

  props: {
    // Tracks object from the feedTracks list
    track: {
      type: Object,
      required: true,
    },
    // Logged in users id (required for GET /playlists/user/{user_id})
    userId: {
      type: [Number, String],
      required: true,
    },
  },

  data() {
    return {
      playlists: [],
      loading: true,
      submitting: false,
      error: "",
    };
  },

  async mounted() {
    await this.fetchPlaylists();
  },

  methods: {
    close() {
      this.$emit("close");
    },

    async fetchPlaylists() {
      this.loading = true;
      this.error = "";
      try {
        const config = await loadConfig();

        const res = await fetch(
          `${config.backendUrl}/playlists/user/${this.userId}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (!res.ok) {
          // Doesn’t crash just shows the message
          this.error = `Could not load playlists (status ${res.status}).`;
          this.playlists = [];
          return;
        }

        const data = await res.json();

        // Backend format: { playlists: [...], total?: number }
        this.playlists = Array.isArray(data.playlists) ? data.playlists : [];
      } catch (err) {
        console.warn("Fetch playlists failed:", err);
        this.error = "Could not load playlists (network/config error).";
        this.playlists = [];
      } finally {
        this.loading = false;
      }
    },

    async selectPlaylist(playlist) {
      // Requirement: close modal after sending the request (even if it fails)
      this.submitting = true;

      try {
        const config = await loadConfig();

        const res = await fetch(
          `${config.backendUrl}/playlists/${playlist.id}/tracks/add`,
          {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },

            body: JSON.stringify({
              title: this.track?.title ?? "",
              artist: this.track?.artist ?? "",
              audio_url: this.track?.audio ?? "",
            }),
          },
        );

        if (!res.ok) {
          console.warn(
            "Add track to playlist failed:",
            res.status,
            await res.text().catch(() => ""),
          );
        }
      } catch (err) {
        console.warn(
          "Add track request error (expected if endpoint missing):",
          err,
        );
      } finally {
        this.submitting = false;
        this.close();
      }
    },
  },
};
