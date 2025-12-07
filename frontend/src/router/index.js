import { createRouter, createWebHistory } from "vue-router";
import InputFeedPage from "../pages/InputFeedPage.vue";
import SearchFeedPage from "../pages/SearchFeedPage.vue";
import ViewFeedPage from "../pages/ViewFeedPage.vue";

const routes = [
  { path: "/", component: InputFeedPage },
  { path: "/search", component: SearchFeedPage },
  { path: "/view", component: ViewFeedPage },
  // Development tool pages, add paths to the else condition.
  ...(import.meta.env.VITE_INCLUDE_DEV_FEATURES !== "yes" ? [] : []),
];

const router = createRouter({
  history: createWebHistory(), // Uses history mode (clean URLs)
  routes,
});

export default router;
