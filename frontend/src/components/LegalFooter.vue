<template>
  <nav class="footer">
    <router-link to="/terms"> Terms of Service </router-link>
    <router-link to="/privacy"> Privacy Policy </router-link>
    <router-link to="/cookies"> Cookie Policy </router-link>
  </nav>
</template>

<style scoped>
a {
  color: var(--light-blue);
  font-weight: 500;
  margin: 0 0.75rem;
  font-size: clamp(0.6rem, 0.75vw, 0.8rem);
}
.footer {
  background-color: var(--nav-bg);
  padding: 0.25rem;
  font-family: var(--font-helvetica);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-navbar);
  border-top: var(--border-thick) var(--orange);
  position: relative;
  z-index: var(--navbar-z);
  margin-top: auto;
}
</style>
