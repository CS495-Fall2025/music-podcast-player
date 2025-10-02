<template>
  <BNavbar class="spotify-navbar" toggleable="lg">
    <BNavbarBrand href="#" class="brand">RSS Music Player</BNavbarBrand>

    <BNavbarToggle target="nav-collapse" />

    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem href="#" class="nav-link">Home</BNavItem>
        <BNavItem href="#" class="nav-link">About</BNavItem>
        <BNavItem href="#" class="nav-link">Contact</BNavItem>
      </BNavbarNav>

      <BNavbarNav class="ms-auto">
        <BNavItemDropdown text="Account" class="nav-link">
          <BDropdownItem @click="onLogin">Login</BDropdownItem>
          <BDropdownItem @click="onLogout">Logout</BDropdownItem>
        </BNavItemDropdown>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>
</template>

<script setup>
import {
  BNavbar,
  BNavbarBrand,
  BNavbarToggle,
  BCollapse,
  BNavbarNav,
  BNavItem,
  BNavItemDropdown,
  BDropdownItem,
} from "bootstrap-vue-next";

import navbarLogic from "./navBar.js";
const { onLogin, onLogout } = navbarLogic;
</script>

<style src="../style.css" />

