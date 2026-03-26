<script setup>
import { onMounted, ref } from "vue";
import { useAuth } from "../auth/authService";

const { currentUser, verifyToken } = useAuth();
const playlists = ref([]);

onMounted(async () => {
  if (!currentUser.value) {
    await verifyToken();
  }
});
</script>

<template>
  <div v-if="currentUser" class="profile-container">
    <div class="profile-card">
      <div class="profile-info">
        <h1>{{ currentUser.username }}'s Profile</h1>
      </div>
      <div class="break"></div>
      <div class="playlist-info">
        <h2>Playlists</h2>
        <div
          v-if="!playlists || playlists.length === 0"
          class="empty-playlists"
        >
          Add Some Playlists!
        </div>
        <div v-else class="playlist-box">
          <div v-for="track in playlists" :key="track.id" class="playlist-item">
            {{ track.name }}
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading-state">
    <p>Loading profile...</p>
  </div>
</template>

<style src="./userPage.css"></style>
