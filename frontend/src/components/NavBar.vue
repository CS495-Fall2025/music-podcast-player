<template>
  <nav class="navbar">
    <div class="nav-left">
      <div class="brand">RSS Music Player</div>

      <button class="navbar-toggle" @click="isOpen = !isOpen" aria-label="Toggle navigation" />

      <div :class="['nav-links', { 'is-open': isOpen }]">
        <a href="#" class="nav-link">Home</a>
        <a href="#" class="nav-link">About</a>
        <a href="#" class="nav-link">Contact</a>
      </div>
    </div>

    <div class="nav-right">
      <div class="nav-dropdown" ref="dropdownRef">
        <button class="dropdown-toggle" @click.stop="dropdownOpen = !dropdownOpen">
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
