// main.js
import { createApp } from "vue";
import App from "./App.vue";

// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap/dist/js/bootstrap.bundle.js";

// Import specific BootstrapVueNext components
import {
  BButton,
  BNavbar,
  BNavbarBrand,
  BNavbarToggle,
  BCollapse,
  BNavItem,
} from "bootstrap-vue-next";

const app = createApp(App);

// Register components globally
app.component("BButton", BButton);
app.component("BNavbar", BNavbar);
app.component("BNavbarBrand", BNavbarBrand);
app.component("BNavbarToggle", BNavbarToggle);
app.component("BCollapse", BCollapse);
app.component("BNavItem", BNavItem);

app.mount("#app");
