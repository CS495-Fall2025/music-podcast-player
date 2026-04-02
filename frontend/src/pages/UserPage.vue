<script setup>
import { onMounted, ref } from "vue";
import { useAuth } from "../auth/authService";
import {
  fetchUserPlaylists,
  fetchPlaylistDetail,
  removeTrackFromPlaylist,
  reorderTrackInPlaylist,
} from "../utils/playlistApi";
import loadConfig from "../config";
import { currentTrack, feedTracks } from "../controllers/localFeedStore.js";
import UserTrack from "../components/UserTrack.vue";
import MiniPlayer from "../components/MiniPlayer.vue";

const { currentUser, verifyToken } = useAuth();
const playlists = ref([]);
const playlistTotal = ref(0);
const totalTracks = ref(0);
const isLoadingPlaylists = ref(true);
const playlistError = ref("");

const profilePublic = ref(true);

async function loadPrivacy() {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/me/privacy`, {
    credentials: "include",
  });
  if (response.ok) {
    const data = await response.json();
    profilePublic.value = data.profile_public;
  }
}

async function togglePrivacy() {
  const newValue = !profilePublic.value;
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/me/privacy`, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_public: newValue }),
  });
  if (response.ok) {
    profilePublic.value = newValue;
  }
}

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
    playlistTotal.value = response.playlists.length;
    totalTracks.value = response.playlists.reduce(
      (sum, p) => sum + p.track_count,
      0,
    );
    playlists.value = mapPlaylistResponse(response);
  } catch (error) {
    playlistError.value =
      error instanceof Error ? error.message : "Unable to load playlists.";
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

  await Promise.all([loadPlaylists(), loadPrivacy()]);
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
    currentTrack.value = "";
    feedTracks.splice(0, feedTracks.length, ...detail.tracks);
  } catch (err) {
    trackError.value =
      err instanceof Error ? err.message : "Could not load tracks.";
  } finally {
    isLoadingTracks.value = false;
  }
}

async function deleteTrack(track) {
  try {
    await removeTrackFromPlaylist(selectedPlaylistId.value, track.track_url);
    const idx = selectedPlaylistTracks.value.findIndex(
      (t) => t.track_url === track.track_url,
    );
    if (idx !== -1) selectedPlaylistTracks.value.splice(idx, 1);
    feedTracks.splice(0, feedTracks.length, ...selectedPlaylistTracks.value);
    const playlist = playlists.value.find(
      (p) => p.id === selectedPlaylistId.value,
    );
    if (playlist) playlist.trackCount--;
  } catch {
    // silent fail — track stays in list
  }
}

async function moveTrack(track, direction) {
  const idx = selectedPlaylistTracks.value.findIndex(
    (t) => t.track_url === track.track_url,
  );
  const newPosition = idx + 1 + direction; // positions are 1-based
  if (newPosition < 1 || newPosition > selectedPlaylistTracks.value.length)
    return;

  try {
    await reorderTrackInPlaylist(
      selectedPlaylistId.value,
      track.track_url,
      newPosition,
    );
    const tracks = selectedPlaylistTracks.value;
    const moved = tracks.splice(idx, 1)[0];
    tracks.splice(idx + direction, 0, moved);
    feedTracks.splice(0, feedTracks.length, ...tracks);
  } catch {
    // silent fail — order stays as-is
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
  <div class="page-layout">
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

            <div class="privacy-toggle">
              <div class="toggle-label">
                <span>{{
                  profilePublic ? "Public profile" : "Private profile"
                }}</span>
                <button
                  class="toggle-switch"
                  :class="{ 'toggle-switch--on': profilePublic }"
                  @click="togglePrivacy"
                  :aria-label="
                    profilePublic
                      ? 'Make profile private'
                      : 'Make profile public'
                  "
                >
                  <span class="toggle-knob" />
                </button>
              </div>
            </div>

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
            <p class="section-caption">
              Playlists made by {{ currentUser.username }}.
            </p>
          </div>

          <div v-if="isLoadingPlaylists" class="playlist-state-card">
            Loading playlists...
          </div>

          <div
            v-else-if="playlistError"
            class="playlist-state-card playlist-error"
          >
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
              :class="{
                'playlist-item--active': selectedPlaylistId === playlist.id,
              }"
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
              <button
                class="track-panel-close"
                @click="closePlaylist"
                aria-label="Close tracks"
              >
                ✕
              </button>
            </div>

            <div v-if="isLoadingTracks" class="playlist-state-card">
              Loading tracks...
            </div>

            <div
              v-else-if="trackError"
              class="playlist-state-card playlist-error"
            >
              {{ trackError }}
            </div>

            <div v-else class="track-list">
              <div
                v-for="(track, index) in selectedPlaylistTracks"
                :key="track.id"
                class="track-row"
              >
                <UserTrack :track="track" />
                <div class="track-actions">
                  <button
                    class="track-action-btn"
                    :disabled="index === 0"
                    @click.stop="moveTrack(track, -1)"
                    title="Move up"
                  >
                    ▲
                  </button>
                  <button
                    class="track-action-btn"
                    :disabled="index === selectedPlaylistTracks.length - 1"
                    @click.stop="moveTrack(track, 1)"
                    title="Move down"
                  >
                    ▼
                  </button>
                  <button
                    class="track-action-btn track-action-btn--delete"
                    @click.stop="deleteTrack(track)"
                    title="Remove track"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div v-else class="loading-state">
      <p>Loading profile...</p>
    </div>

    <MiniPlayer :showReverse="false" />
  </div>
</template>

<style src="./userPage.css"></style>
