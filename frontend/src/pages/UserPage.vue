<script setup>
import { onMounted, ref } from "vue";
import { useAuth } from "../auth/authService";
import { fetchUserPlaylists, fetchPlaylistDetail } from "../utils/playlistApi";
import { currentTrack, feedTracks } from "../controllers/localFeedStore.js";
import UserTrack from "../components/UserTrack.vue";
import MiniPlayer from "../components/MiniPlayer.vue";

const { currentUser, verifyToken } = useAuth();
const playlists = ref([]);
const playlistTotal = ref(0);
const totalTracks = ref(0);
const isLoadingPlaylists = ref(true);
const playlistError = ref("");

const selectedPlaylistId = ref(null);
const selectedPlaylistTitle = ref("");
const selectedPlaylistTracks = ref([]);
const isLoadingTracks = ref(false);
const trackError = ref("");

function formatCreatedAt(createdAt) {
  const date = new Date(createdAt);

  if (Number.isNaN(date.getTime())) {
    return "Created recently";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function mapPlaylistResponse(response) {
  return response.playlists.map((playlist) => ({
    id: playlist.id,
    title: playlist.title,
    description: playlist.description || "No description added yet.",
    trackCount: playlist.track_count,
    createdLabel: formatCreatedAt(playlist.created_at),
  }));
}

async function loadPlaylists() {
  isLoadingPlaylists.value = true;
  playlistError.value = "";

  try {
    const response = await fetchUserPlaylists();
    playlistTotal.value = response.total;
    totalTracks.value = response.playlists.reduce((sum, p) => sum + p.track_count, 0);
    playlists.value = mapPlaylistResponse(response);
  } catch (error) {
    playlistError.value = error instanceof Error ? error.message : "Unable to load playlists.";
    playlists.value = [];
    playlistTotal.value = 0;
  } finally {
    isLoadingPlaylists.value = false;
  }
}

onMounted(async () => {
  if (!currentUser.value) {
    await verifyToken();
  }

  await loadPlaylists();
});

async function openPlaylist(playlist) {
  if (selectedPlaylistId.value === playlist.id) {
    closePlaylist();
    return;
  }

  selectedPlaylistId.value = playlist.id;
  selectedPlaylistTitle.value = playlist.title;
  selectedPlaylistTracks.value = [];
  isLoadingTracks.value = true;
  trackError.value = "";

  try {
    const detail = await fetchPlaylistDetail(playlist.id);
    selectedPlaylistTracks.value = detail.tracks;
    feedTracks.splice(0, feedTracks.length, ...detail.tracks);
  } catch (err) {
    trackError.value =
      err instanceof Error ? err.message : "Could not load tracks.";
  } finally {
    isLoadingTracks.value = false;
  }
}

function closePlaylist() {
  selectedPlaylistId.value = null;
  selectedPlaylistTitle.value = "";
  selectedPlaylistTracks.value = [];
  currentTrack.value = "";
  feedTracks.splice(0, feedTracks.length);
}
</script>

<template>
  <div v-if="currentUser" class="profile-container">
    <div class="profile-card">
      <section class="profile-hero">
        <div class="profile-avatar" aria-hidden="true">
          {{ currentUser.username.slice(0, 1).toUpperCase() }}
        </div>

        <div class="profile-copy">
          <p class="profile-eyebrow">Listener Profile</p>
          <h1>{{ currentUser.username }}'s Profile</h1>
          <p class="profile-description">
            Profile of {{ currentUser.username }}.
          </p>

          <div class="profile-stats" aria-label="Profile stats">
            <div class="stat-pill">
              <span class="stat-value">{{ playlistTotal }}</span>
              <span class="stat-label">Playlists</span>
            </div>
            <div class="stat-pill">
              <span class="stat-value">{{ totalTracks }}</span>
              <span class="stat-label">Total Tracks</span>
            </div>
          </div>
        </div>
      </section>

      <section class="playlist-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Library</p>
            <h2>Playlists</h2>
          </div>
          <p class="section-caption">Playlists made by {{ currentUser.username }}.</p>
        </div>

        <div v-if="isLoadingPlaylists" class="playlist-state-card">
          Loading playlists...
        </div>

        <div v-else-if="playlistError" class="playlist-state-card playlist-error">
          {{ playlistError }}
        </div>

        <div
          v-else-if="!playlists || playlists.length === 0"
          class="playlist-state-card"
        >
          Add Some Playlists!
        </div>

        <div v-else class="playlist-grid">
          <article
            v-for="playlist in playlists"
            :key="playlist.id"
            class="playlist-item"
            :class="{ 'playlist-item--active': selectedPlaylistId === playlist.id }"
            @click="openPlaylist(playlist)"
          >
            <h3>{{ playlist.title }}</h3>
            <p class="playlist-description">{{ playlist.description }}</p>

            <div class="playlist-meta">
              <span>{{ playlist.trackCount }} tracks</span>
              <span>Created {{ playlist.createdLabel }}</span>
            </div>
          </article>
        </div>

        <div v-if="selectedPlaylistId !== null" class="track-panel">
          <div class="track-panel-header">
            <h3>{{ selectedPlaylistTitle }}</h3>
            <button class="track-panel-close" @click="closePlaylist" aria-label="Close tracks">✕</button>
          </div>

          <div v-if="isLoadingTracks" class="playlist-state-card">
            Loading tracks...
          </div>

          <div v-else-if="trackError" class="playlist-state-card playlist-error">
            {{ trackError }}
          </div>

          <div v-else class="track-list">
            <UserTrack
              v-for="track in selectedPlaylistTracks"
              :key="track.id"
              :track="track"
            />
          </div>
        </div>
      </section>
    </div>

    <MiniPlayer />
  </div>

  <div v-else class="loading-state">
    <p>Loading profile...</p>
  </div>
</template>

<style src="./userPage.css"></style>
