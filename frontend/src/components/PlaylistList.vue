<script>
import { playlist } from "../controllers/playlistStore.js";
import { requestPlaylist } from "../controllers/playlistParser.js";

export default {
    name: "PlaylistDetails",
    setup() {
        requestPlaylist(playlist.id);
        return {
            playlist,
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
            <p>{{ playlist.track_count }}</p>
            <p>{{ playlist.created_at }}</p>
        </div>
    </div>
</template>