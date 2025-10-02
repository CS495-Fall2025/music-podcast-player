<template>
  <BNavbar toggleable="lg" type="dark" variant="primary">
    <BNavbarBrand href="#">MyApp</BNavbarBrand>

    <BNavbarToggle target="nav-collapse" />

    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem href="#">Home</BNavItem>
        <BNavItem href="#">About</BNavItem>
        <BNavItem href="#">Contact</BNavItem>
      </BNavbarNav>

      <BNavbarNav class="ms-auto">
        <BNavItemDropdown text="Account" right>
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
  BButton
} from 'bootstrap-vue-next'

import navbarLogic from './navBar.js'
const { onLogin, onLogout } = navbarLogic
</script>

<style scoped>
button.btn {
margin-right: 0.5rem;
}
</style>
