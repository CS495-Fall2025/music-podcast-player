<script>
import { playlist, playlistTracks } from '../controllers/playlistStore';

export default {
    name: "PlaylistDetails",
    data() {
        return {
            playlist,
            playlistTracks,
        };
    },
};
</script>

<template>
    <div class="playlist-card">
        <div class = playlist-header>
            <h2>{{ playlist.name }}</h2>
        </div>
        <div class="playlist-info">
            <p>{{ playlist.description }}</p>
        </div>
        <div class="playlist-tracks">
        </div>
        <div class="playlist-footer">
        </div>
    </div>
</template>