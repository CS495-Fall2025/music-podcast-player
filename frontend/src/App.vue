<script setup>
// Import components here.
import NavBar from "./components/NavBar.vue";
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
}
</style>
