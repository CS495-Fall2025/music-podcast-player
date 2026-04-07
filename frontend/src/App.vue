<script setup>
import { onMounted } from "vue";
import { verifyToken } from "./auth/authService";
import NavBar from "./components/NavBar.vue";

// Verify stored token on app startup
onMounted(async () => {
  await verifyToken();
});
</script>

<template>
  <div class="app-wrapper">
    <NavBar />
    <router-view />
  </div>
</template>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  overflow: hidden;
  width: 100%;
}
</style>
