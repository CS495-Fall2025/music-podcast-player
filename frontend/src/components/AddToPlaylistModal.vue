<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card" role="dialog" aria-modal="true">

      <div class="modal-header">
        <h2 class="modal-title">Add to playlist</h2>
        <button class="modal-close" type="button" @click="$emit('close')">✕</button>
      </div>

      <p v-if="track" class="modal-track-name">{{ track.title || "Unknown track" }}</p>

      <div v-if="loading" class="modal-message">Loading playlists...</div>

      <template v-else>
        <div v-if="error" class="modal-message error">{{ error }}</div>

        <div v-if="playlists.length" class="playlist-list">
          <button
            v-for="p in playlists"
            :key="p.id"
            class="playlist-item"
            type="button"
            @click="$emit('select-playlist', p)"
          >
            <span class="playlist-name">{{ p.title }}</span>
            <span class="playlist-count">{{ p.track_count ?? 0 }} tracks</span>
          </button>
        </div>
        <p v-else class="modal-message">No playlists yet.</p>

        <div class="create-section">
          <h3 class="create-title">New playlist</h3>
          <input
            v-model="newTitle"
            class="create-input"
            type="text"
            placeholder="Playlist name"
          />
          <textarea
            v-model="newDescription"
            class="create-input create-textarea"
            placeholder="Description (optional)"
            rows="3"
          ></textarea>
          <button class="create-btn" type="button" @click="create">Create + Add</button>
        </div>
      </template>

    </div>
  </div>
</template>

<script>
export default {
  name: "AddToPlaylistModal",

  props: {
    playlists: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    error: { type: String, default: "" },
    track: { type: Object, default: null },
  },

  emits: ["close", "select-playlist", "create-playlist"],

  data() {
    return {
      newTitle: "",
      newDescription: "",
    };
  },

  methods: {
    create() {
      this.$emit("create-playlist", {
        title: this.newTitle.trim(),
        description: this.newDescription.trim(),
      });
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: grid;
  place-items: center;
  z-index: 9999;
  padding: 12px;
}

.modal-card {
  width: min(480px, 100%);
  max-height: calc(100vh - 24px);
  overflow-y: auto;
  background: var(--h-background);
  color: var(--text);
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  color: var(--text);
}

.modal-close:hover {
  background: rgba(128, 128, 128, 0.15);
}

.modal-track-name {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-message {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0;
}

.modal-message.error {
  color: #d9534f;
  opacity: 1;
}

.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
  padding: 2px;
}

.playlist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid rgba(128, 128, 128, 0.25);
  border-radius: 10px;
  background: var(--track-background);
  color: var(--text);
  cursor: pointer;
  text-align: left;
  gap: 8px;
}

.playlist-item:hover {
  background: var(--hover-blue);
  color: var(--dark-blue);
}

.playlist-name {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-count {
  font-size: 0.8rem;
  opacity: 0.7;
  flex-shrink: 0;
}

.create-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid rgba(128, 128, 128, 0.2);
  padding-top: 12px;
}

.create-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
}

.create-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 10px;
  border: 1px solid rgba(128, 128, 128, 0.3);
  border-radius: 8px;
  background: var(--h-background);
  color: var(--text);
  font: inherit;
}

.create-textarea {
  resize: none;
}

.create-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 10px;
  background: #1f6feb;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.create-btn:hover {
  opacity: 0.9;
}
</style>
