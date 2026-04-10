export default {
  name: "AddToPlaylistModal",

  props: {
    playlists: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: String,
      default: "",
    },
    track: {
      type: Object,
      default: null,
    },
    submitting: {
      type: Boolean,
      default: false,
    },
  },

  emits: ["close", "select-playlist", "create-playlist"],

  data() {
    return {
      newPlaylistTitle: "",
      newPlaylistDescription: "",
    };
  },

  methods: {
    close() {
      this.$emit("close");
    },

    selectPlaylist(playlist) {
      this.$emit("select-playlist", playlist);
    },

    createAndAdd() {
      this.$emit("create-playlist", {
        title: this.newPlaylistTitle.trim(),
        description: this.newPlaylistDescription.trim(),
      });
    },
  },
};
