<script>
import { playlist, playlistTracks } from '../controllers/playlistStore';
import { requestPlaylist } from '../controllers/playlistParser';

export default {
    name: "PlaylistDetails",
    setup() {
        requestPlaylist(playlist.id);
        return {
            playlist,
            playlistTracks,
        };
    },
};
</script>

<template>
    <div class="playlist-card">
        <div class="playlist-header">
            <h2>{{ playlist.name }}</h2>
        </div>
        <div class="playlist-info">
            <p>{{ playlist.created_at }}</p>
        </div>
        <div class="playlist-tracks">
<<<<<<< Updated upstream
            <a v-for="track in playlistTracks" :key="track.id" class="track-link">
                <p>{{ track.name }}</p>
                <p>{{ track.artist }}</p>
            </a>
=======
            <div v-for="tracks in playlistTracks.values" :key="tracks">
                <p>{{ tracks.title }}</p>
                <p>{{ tracks.artist }}</p>
            </div>
        </div>
        <div class="playlist-footer">
>>>>>>> Stashed changes
        </div>
    </div>
</template>