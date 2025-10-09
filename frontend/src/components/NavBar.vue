<template>
  <nav class="navbar">
    <div class="nav-left">
      <div class="brand">RSS Music Player</div>

      <button
        class="navbar-toggle"
        @click="isOpen = !isOpen"
        aria-label="Toggle navigation"
      />

      <div :class="['nav-links', { 'is-open': isOpen }]">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/" class="nav-link">About</router-link>
        <router-link to="/" class="nav-link">Contact</router-link>
        <router-link to="/search" class="nav-link">Search Feeds</router-link>
        <router-link to="/" class="nav-link">Input Feed</router-link>
      </div>
    </div>

    <div class="nav-right">
      <div class="nav-dropdown" ref="dropdownRef">
        <button
          class="dropdown-toggle"
          @click.stop="dropdownOpen = !dropdownOpen"
        >
          Account ▾
        </button>
        <div v-if="dropdownOpen" class="dropdown-menu">
          <button class="dropdown-item" @click="handleLogin">Login</button>
          <button class="dropdown-item" @click="handleLogout">Logout</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import useNavbar from "./navBar.js";

const { isOpen, dropdownOpen, dropdownRef, handleLogin, handleLogout } =
  useNavbar();
</script>

<style src="../style.css" />
