import { createRouter, createWebHistory } from "vue-router";
import InputFeedPage from "../pages/InputFeedPage.vue";
import SearchFeedPage from "../pages/SearchFeedPage.vue";
import ViewFeedPage from "../pages/ViewFeedPage.vue";
import AuthCallback from "../pages/AuthCallback.vue";
import { isAuthenticated } from "../auth/authService";

const routes = [
  { path: "/", component: InputFeedPage },

  {
    path: "/search",
    component: SearchFeedPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/view",
    component: ViewFeedPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/auth/callback",
    component: AuthCallback,
  },

  ...(import.meta.env.VITE_INCLUDE_DEV_FEATURES !== "yes" ? [] : []),
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    // redirects unauthenticated users to home
    return "/";
  }
});

export default router;
