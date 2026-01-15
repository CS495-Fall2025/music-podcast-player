<template>
  <nav class="navbar">
    <div class="nav-left">
      <div class="brand">RSS Music Player</div>

      <button
        class="navbar-toggle"
        @click="isOpen = !isOpen"
        aria-label="Toggle navigation"
      >
        <span class="hamburger-icon"></span>
      </button>

      <div :class="['nav-links', { 'is-open': isOpen }]">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/" class="nav-link">About</router-link>
        <router-link to="/" class="nav-link">Contact</router-link>
        <router-link to="/search" class="nav-link">Search Feeds</router-link>
        <router-link to="/" class="nav-link">Input Feed</router-link>
        <template v-if="includeDevPages">
          <!-- No dev pages currently. -->
        </template>
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
import useNavbar from "../controllers/navBar.js";

const { isOpen, dropdownOpen, dropdownRef, handleLogin, handleLogout } =
  useNavbar();
const includeDevPages = import.meta.env.VITE_INCLUDE_DEV_FEATURES === "yes";
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
