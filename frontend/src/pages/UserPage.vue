<script setup>
import { onMounted, ref } from "vue";
import { useAuth } from "../auth/authService";
import {
  fetchUserPlaylists,
  fetchPlaylistDetail,
  deletePlaylist,
  removeTrackFromPlaylist,
  reorderTrackInPlaylist,
  createPlaylist,
  addTrackToPlaylist,
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
const deletingPlaylistId = ref(null);
const playlistPopupOpen = ref(false);
const popupStyle = ref({
  top: "0px",
  left: "0px",
  transform: "translate(-50%, -50%)",
});
const selectedTrack = ref(null);
const popupPlaylists = ref([]);
const newPlaylistTitle = ref("");
const newPlaylistDescription = ref("");
const popupError = ref("");
const popupLoading = ref(false);

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

async function deletePlaylistFromProfile(playlist) {
  if (deletingPlaylistId.value !== null) {
    return;
  }

  deletingPlaylistId.value = playlist.id;

  try {
    await deletePlaylist(playlist.id);

    const idx = playlists.value.findIndex((p) => p.id === playlist.id);
    if (idx === -1) {
      return;
    }

    const [removedPlaylist] = playlists.value.splice(idx, 1);
    playlistTotal.value = playlists.value.length;
    totalTracks.value = Math.max(
      0,
      totalTracks.value - (removedPlaylist?.trackCount ?? 0),
    );

    if (selectedPlaylistId.value === playlist.id) {
      closePlaylist();
    }
  } catch {
    // silent fail — playlist stays in list
  } finally {
    deletingPlaylistId.value = null;
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
async function handleAddToPlaylist({ track }) {
  selectedTrack.value = track;
  popupError.value = "";
  newPlaylistTitle.value = "";
  newPlaylistDescription.value = "";

  popupStyle.value = {
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
  };

  playlistPopupOpen.value = true;
  popupLoading.value = true;

  try {
    const response = await fetchUserPlaylists();
    popupPlaylists.value = response.playlists || [];
  } catch (error) {
    popupError.value =
      error instanceof Error ? error.message : "Unable to load playlists.";
    popupPlaylists.value = [];
  } finally {
    popupLoading.value = false;
  }
}

function closePlaylistPopup() {
  playlistPopupOpen.value = false;
  selectedTrack.value = null;
  popupError.value = "";
  newPlaylistTitle.value = "";
  newPlaylistDescription.value = "";
}

async function handleAddTrackToPlaylist(playlistId) {
  if (!selectedTrack.value?.track_url) {
    popupError.value = "This track does not have a track URL.";
    return;
  }

  try {
    await addTrackToPlaylist(playlistId, selectedTrack.value.track_url);
    closePlaylistPopup();
  } catch (error) {
    const message = error instanceof Error ? error.message.toLowerCase() : "";

    if (
      message.includes("already exists") ||
      message.includes("already in") ||
      message.includes("duplicate") ||
      message.includes("409") ||
      message.includes("conflict")
    ) {
      popupError.value = "Track already exists in this playlist.";
    } else {
      popupError.value = "Could not add track to playlist.";
    }
  }
}

async function handleCreatePlaylist() {
  const title = newPlaylistTitle.value.trim();
  const description = newPlaylistDescription.value.trim();

  if (!title) {
    popupError.value = "Enter a playlist title.";
    return;
  }

  if (!selectedTrack.value?.track_url) {
    popupError.value = "This track does not have a track URL.";
    return;
  }

  try {
    const created = await createPlaylist(title, description);
    await addTrackToPlaylist(created.id, selectedTrack.value.track_url);
    closePlaylistPopup();
  } catch (error) {
    popupError.value =
      error instanceof Error ? error.message : "Unable to create playlist.";
  }
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
                <span>Public profile</span>
                <button
                  class="toggle-switch"
                  :class="{ 'toggle-switch--on': profilePublic }"
                  @click="togglePrivacy"
                  :aria-label="'Make profile public'"
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
              <div class="playlist-item-header">
                <h3>{{ playlist.title }}</h3>
                <button
                  class="playlist-delete-btn"
                  :disabled="deletingPlaylistId === playlist.id"
                  @click.stop="deletePlaylistFromProfile(playlist)"
                  :aria-label="`Delete playlist ${playlist.title}`"
                  title="Delete playlist"
                >
                  ✕
                </button>
              </div>
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
                <UserTrack :track="track" @add-to-playlist="handleAddToPlaylist" />
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

    <div
      v-if="playlistPopupOpen"
      :style="{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 1000,
        width: '320px',
        maxWidth: '90vw',
        background: '#111',
        border: '1px solid #444',
        borderRadius: '16px',
        boxShadow: '0 12px 32px rgba(0, 0, 0, 0.35)',
        padding: '20px',
      }"
    >
      <div
        :style="{
          position: 'relative',
          marginBottom: '16px',
          minHeight: '32px',
        }"
      >
        <strong
          :style="{
            color: 'white',
            fontWeight: '700',
            fontSize: '1.1rem',
            display: 'block',
            paddingRight: '44px',
          }"
        >
          Add to playlist
        </strong>

        <button
  @click="closePlaylistPopup"
  :style="{
    position: 'absolute',
    top: '0',
    right: '0',
    width: '32px',
    height: '32px',
    border: 'none',
    outline: 'none',
    boxShadow: 'none',
    background: 'transparent',
    color: 'white',
    fontSize: '1.4rem',
    lineHeight: '1',
    cursor: 'pointer',
    padding: '0',
    margin: '0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    appearance: 'none',
    WebkitAppearance: 'none',
  }"
>
  ✕
</button>
      </div>

      <div
        v-if="popupLoading"
        :style="{ color: '#ccc', fontSize: '0.95rem', marginBottom: '12px' }"
      >
        Loading playlists...
      </div>

      <div v-else>
        <div
          v-if="popupError"
          :style="{
            color: '#ff4d6d',
            fontSize: '0.9rem',
            marginBottom: '12px',
          }"
        >
          {{ popupError }}
        </div>

        <div
          v-if="popupPlaylists.length"
          :style="{
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            marginBottom: '14px',
          }"
        >
          <button
            v-for="playlist in popupPlaylists"
            :key="playlist.id"
            @click="handleAddTrackToPlaylist(playlist.id)"
            :style="{
              border: 'none',
              borderRadius: '12px',
              background: '#1b1f27',
              color: 'white',
              padding: '14px 16px',
              textAlign: 'left',
              cursor: 'pointer',
              fontSize: '1rem',
            }"
          >
            {{ playlist.title }}
          </button>
        </div>

        <div
          :style="{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }"
        >
          <input
            v-model="newPlaylistTitle"
            type="text"
            placeholder="New playlist name"
            :style="{
              width: '100%',
              boxSizing: 'border-box',
              border: '1px solid #666',
              borderRadius: '12px',
              padding: '14px 16px',
              background: '#3a3a3a',
              color: 'white',
              fontSize: '1rem',
            }"
          />

          <textarea
            v-model="newPlaylistDescription"
            placeholder="Description (optional)"
            rows="4"
            :style="{
              width: '100%',
              boxSizing: 'border-box',
              border: '1px solid #666',
              borderRadius: '12px',
              padding: '14px 16px',
              background: '#3a3a3a',
              color: 'white',
              fontSize: '1rem',
              resize: 'none',
              minHeight: '120px',
              overflow: 'auto',
            }"
          ></textarea>

          <button
            @click="handleCreatePlaylist"
            :style="{
              border: 'none',
              borderRadius: '12px',
              background: '#2563eb',
              color: 'white',
              padding: '14px 16px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600',
            }"
          >
            Create + Add
          </button>
        </div>
      </div>
    </div>

    <MiniPlayer :showReverse="true" />
  </div>
</template>

<style src="./userPage.css"></style>