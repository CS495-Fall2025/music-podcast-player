import { reactive, ref } from "vue";

// This list will be populated with a single feed's information (type, artist, title, description, link, image)
export const feed = reactive([]);

// This list will be populated with track objects, each containing their own information (type, title, artist, description, audio, image, value)
export const feedTracks = reactive([]);

// Holds the current track's object (element of feed). If none is selected it will be
// null. Make sure to update the whole object rather than a field.
export const currentTrack = ref("");

// Populate with feeds found using the backend.
export const searchedFeeds = reactive([]);

// Sat Drip settings
export const satDripRate = ref(0);
export const satDripEnabled = ref(false);
