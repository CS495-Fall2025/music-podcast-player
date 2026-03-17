import { reactive, ref } from "vue";

// This list will be populated with a single playlist's information 
// (type, title, description, link, image)
export const playlist = reactive([]);

// This list will be populated with track objects, each containing their own information 
// (type, title, artist, description, audio, image, value)
export const playlistTracks = reactive([]);

// Holds the current track's object (element of feed). If none is selected it will be
// null. Make sure to update the whole object rather than a field.
export const currentTrack = ref("");