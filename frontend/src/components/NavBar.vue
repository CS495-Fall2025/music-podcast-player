<template>
  <nav class="navbar">
    <div class="nav-left">
      <div class="brand">Music Podcast Player</div>

      <button
        class="navbar-toggle"
        @click="isOpen = !isOpen"
        aria-label="Toggle navigation"
      >
        <span class="hamburger-icon"></span>
      </button>

      <div :class="['nav-links', { 'is-open': isOpen }]">
        <router-link to="/" class="nav-link" @click="closeMenu"
          >About</router-link
        >
        <router-link to="/" class="nav-link" @click="closeMenu"
          >Contact</router-link
        >
        <router-link to="/search" class="nav-link" @click="closeMenu"
          >Search</router-link
        >
        <router-link to="/input" class="nav-link" @click="closeMenu"
          >Input Feed</router-link
        >
        <template v-if="includeDevPages">
          <!-- No dev pages currently. -->
        </template>
      </div>
    </div>

    <div class="nav-right">
      <DripIndicator />
      <div v-if="isAuthenticated" class="user-greeting">
        Hello, {{ currentUser?.username }}!
      </div>

      <button class="sat-drip-button" @click="satDripModalOpen = true">
        Sat Drip
      </button>

      <div class="nav-dropdown" ref="dropdownRef">
        <button
          class="dropdown-toggle"
          @click.stop="dropdownOpen = !dropdownOpen"
        >
          Account ▾
        </button>

        <div v-if="dropdownOpen" class="dropdown-menu">
          <template v-if="isAuthenticated">
            <button class="dropdown-item" @click="$router.push('/user')">
              Profile
            </button>
            <button class="dropdown-item" @click="handleLogout">Logout</button>
          </template>
          <template v-else>
            <button class="dropdown-item" @click="handleLogin">Login</button>
            <button class="dropdown-item" @click="handleSignup">Sign Up</button>
          </template>
        </div>
      </div>
    </div>
  </nav>

  <div v-if="satDripModalOpen" class="sat-drip-modal-overlay">
    <div class="sat-drip-modal">
      <h2 class="sat-drip-title">Sat Drip Settings</h2>

      <div class="sat-drip-field">
        <label for="sat-rate">Sats per minute</label>
        <input
          id="sat-rate"
          v-model.number="satDripRate"
          class="sat-drip-input"
          type="number"
          min="0"
        />
      </div>

      <div class="sat-drip-toggle-row">
        <label for="sat-drip-enabled">Enable Sat Dripping</label>
        <label class="sat-toggle">
          <input
            id="sat-drip-enabled"
            v-model="satDripEnabled"
            type="checkbox"
          />
          <span class="sat-toggle-slider"></span>
        </label>
      </div>

      <div class="sat-drip-actions">
        <button class="sat-drip-save" @click="saveSatDripSettings">Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import useNavbar from "../controllers/navBar.js";
import { ref } from "vue";
import { satDripRate, satDripEnabled } from "../controllers/localFeedStore.js";
import DripIndicator from "./DripIndicator.vue";

const {
  isOpen,
  dropdownOpen,
  dropdownRef,
  handleLogin,
  handleSignup,
  handleLogout,
  isAuthenticated,
  currentUser,
} = useNavbar();
const includeDevPages = import.meta.env.VITE_INCLUDE_DEV_FEATURES === "yes";
const satDripModalOpen = ref(false);

function saveSatDripSettings() {
  satDripModalOpen.value = false;
}

function closeMenu() {
  isOpen.value = false;
}
</script>

<style src="../style.css" />
<style scoped>
.navbar {
  background-color: var(--nav-bg);
  padding: 1.25rem 1.5rem;
  font-family: var(--font-helvetica);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-navbar);
  border-bottom: var(--border-thick) var(--orange);
  position: relative;
  z-index: var(--navbar-z);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.nav-right {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.brand {
  font-weight: 700;
  font-size: 1.4rem;
  color: var(--light-orange);
  letter-spacing: 0.5px;
  transition: color var(--transition-slow);
  text-decoration: none;
}

.brand:hover {
  color: var(--lighter-orange);
}

.navbar-toggle {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: var(--light-blue);
  cursor: pointer;
  display: none;
  padding: 0.2rem 0.5rem;
  box-shadow: none;
}

.hamburger-icon::before {
  content: "☰";
  font-size: 1.8rem;
}

/* Alternative: CSS hamburger icon */
.hamburger-icon {
  display: block;
  width: 25px;
  height: 3px;
  background-color: var(--light-blue);
  position: relative;
}

.hamburger-icon::before,
.hamburger-icon::after {
  content: "";
  position: absolute;
  width: 25px;
  height: 3px;
  background-color: var(--light-blue);
  left: 0;
}

.hamburger-icon::before {
  top: -8px;
}

.hamburger-icon::after {
  top: 8px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-link {
  color: var(--light-blue);
  font-weight: 500;
  transition:
    color var(--transition-standard),
    transform var(--transition-fast);
  text-decoration: none;
  letter-spacing: 0.3px;
  margin: 0 0.75rem;
}

.nav-link:hover,
.nav-link:focus {
  color: var(--light-orange);
  transform: scale(1.05);
}

.nav-link.active {
  color: var(--white);
  font-weight: 600;
  border-bottom: var(--border-thick) var(--light-orange);
  padding-bottom: 0.25rem;
}

/* ========================================
   USER GREETING
   ======================================== */

.user-greeting {
  color: var(--light-orange);
  font-weight: 500;
  margin-right: 1.5rem;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
}
/* ========================================
   SAT DRIP
   ======================================== */

.sat-drip-button {
  background: none;
  border: 1px solid var(--light-orange);
  color: var(--light-orange);
  font-weight: 500;
  cursor: pointer;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  border-radius: var(--border-radius);
  margin-right: 0.75rem;
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
}

.sat-drip-button:hover,
.sat-drip-button:focus {
  color: var(--dark-text);
  background-color: var(--light-orange);
}

.sat-drip-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.sat-drip-modal {
  background-color: var(--nav-bg);
  color: var(--light-blue);
  border: 1px solid var(--orange);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  width: 320px;
  padding: 1.5rem;
}

.sat-drip-title {
  margin: 0 0 1rem 0;
  color: var(--light-orange);
}

.sat-drip-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.sat-drip-field label,
.sat-drip-toggle-row label {
  color: var(--light-blue);
}

.sat-drip-input {
  padding: 0.65rem 0.8rem;
  background-color: var(--dark-navy);
  color: var(--white);
  border: 1px solid var(--light-blue);
  border-radius: var(--border-radius);
}

.sat-drip-input:focus {
  outline: none;
  border-color: var(--light-orange);
}

.sat-drip-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: var(--light-blue);
}

.sat-toggle {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 28px;
}

.sat-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.sat-toggle-slider {
  position: absolute;
  inset: 0;
  cursor: pointer;
  background-color: var(--dark-navy);
  border: 1px solid var(--light-blue);
  border-radius: 999px;
  transition: 0.25s ease;
}

.sat-toggle-slider::before {
  content: "";
  position: absolute;
  height: 20px;
  width: 20px;
  left: 3px;
  top: 3px;
  background-color: var(--white);
  border-radius: 50%;
  transition: 0.25s ease;
}

.sat-toggle input:checked + .sat-toggle-slider {
  background-color: var(--light-orange);
  border-color: var(--light-orange);
}

.sat-toggle input:checked + .sat-toggle-slider::before {
  transform: translateX(24px);
}

.sat-drip-actions {
  display: flex;
  justify-content: flex-end;
}

.sat-drip-save {
  background-color: var(--light-orange);
  color: var(--dark-text);
  border: none;
  border-radius: var(--border-radius);
  padding: 0.6rem 1rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.sat-drip-save:hover,
.sat-drip-save:focus {
  opacity: 0.92;
  transform: scale(1.02);
}

/* ========================================
   ACCOUNT DROPDOWN
   ======================================== */

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  background: none !important;
  border: none !important;
  color: var(--light-blue);
  font-weight: 500;
  cursor: pointer;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  text-align: center;
  transition: color var(--transition-standard);
}

.dropdown-toggle:hover,
.dropdown-toggle:focus {
  color: var(--light-orange);
  background: none;
}

.dropdown-menu {
  position: absolute;
  top: 110%;
  right: 0;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  min-width: 140px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: var(--dropdown-z);
}

.dropdown-item {
  background: none;
  border: none;
  color: var(--dark-text);
  font-weight: 500;
  padding: 10px 16px;
  text-align: left;
  width: 100%;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
  font-size: 0.95rem;
}

.dropdown-item:hover {
  background-color: var(--lighter-orange);
  color: var(--dark-text);
}

.dropdown-toggle,
.dropdown-item {
  box-shadow: none !important;
  outline: none !important;
}

@media (max-width: 768px) {
  .navbar-toggle {
    display: block;
  }

  .nav-links {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--dark-navy);
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    display: none;
  }

  .nav-links.is-open {
    display: flex;
  }

  .nav-link {
    margin: 0;
    padding: var(--spacing-sm) 0;
    width: 100%;
    text-align: center;
  }

  .nav-right {
    margin-left: 0;
  }

  .dropdown-menu {
    position: static;
    box-shadow: none;
    border: none;
    background-color: transparent;
  }

  .dropdown-item {
    background-color: var(--dark-navy);
    color: var(--light-blue);
    padding: var(--spacing-sm) 0;
    text-align: center;
  }

  .dropdown-item:hover {
    background-color: var(--light-orange);
    color: var(--dark-text);
  }
}
</style>
