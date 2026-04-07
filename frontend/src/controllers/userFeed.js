import Track from "../components/UserTrack.vue";
import AddToPlaylistModal from "../components/AddToPlaylistModal.vue";
import { feed, feedTracks } from "./localFeedStore.js";
import { useAuth } from "../auth/authService";


export default {
  name: "UserFeed",
  components: { Track, AddToPlaylistModal },

  data(){
    return{
      showAddToPlaylist: false,
      selectedTrackForPlaylist: null,
    };
  },

  methods: {
    handleAddToPlaylist(track) {
      console.log("Add to playlist clicked for track", track);
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

  currentUserId(){
    const { currentUser } = useAuth();
    return (
      currentUser.value?.id ??
      currentUser.value?.user_id ??
      currentUser.value?.userId
    );
  },

  methods:{
    handleAddtoPlaylist(track){
      if (this.currentUserId == null){
        console.warn(
          "Cannot open add-to-playlist modal: user id not available yet."
        );
        return;
      }
      this.selectedTrackForPlaylist = track;
      this.showAddToPlaylist = true;
    },
    closeAddToPlaylistModal() {
      this.showAddToPlaylist = false;
      this.selectedTrackForPlaylist = null;
    },
  },
};
