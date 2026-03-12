<script>
import { playlist } from "../controllers/playlistStore.js";

export default {
    name: "PlaylistDetails",
    data() {
        return {
            playlist,
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
    </div>
</template>