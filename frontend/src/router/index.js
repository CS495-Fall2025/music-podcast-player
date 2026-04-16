import { createRouter, createWebHistory } from "vue-router";
import InputFeedPage from "../pages/InputFeedPage.vue";
import SearchFeedPage from "../pages/SearchFeedPage.vue";
import ViewFeedPage from "../pages/ViewFeedPage.vue";
import AuthCallback from "../pages/AuthCallback.vue";
import LoginPage from "../pages/LoginPage.vue";
import SignupPage from "../pages/SignupPage.vue";
import ForgotPasswordPage from "../pages/ForgotPasswordPage.vue";
import ResetPasswordPage from "../pages/ResetPasswordPage.vue";
import { isAuthenticated } from "../auth/authService";
import UserProfilePage from "../pages/UserPage.vue";
import PublicUserPage from "../pages/PublicUserPage.vue";
import { clearError } from "../controllers/statusStore.js";
import { resetCurrentFeed } from "../controllers/localFeedStore.js";

const routes = [
  { path: "/", redirect: "/search" },

  {
    path: "/input",
    component: InputFeedPage,
    meta: { requiresAuth: false },
  },

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
    path: "/login",
    component: LoginPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/signup",
    component: SignupPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/verify-email",
    redirect: {
      path: "/signup",
      query: { step: "verify" },
    },
  },

  {
    path: "/forgot-password",
    component: ForgotPasswordPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/reset-password",
    component: ResetPasswordPage,
    meta: { requiresAuth: false },
  },

  {
    path: "/auth/callback",
    component: AuthCallback,
  },

  {
    path: "/user",
    component: UserProfilePage,
    meta: { requiresAuth: true },
  },

  {
    path: "/user/:username",
    component: PublicUserPage,
    meta: { requiresAuth: false },
  },

  ...(import.meta.env.VITE_INCLUDE_DEV_FEATURES !== "yes" ? [] : []),
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  // Clear any persistent errors when navigating to new route
  clearError();
  resetCurrentFeed();

  if (to.meta.requiresAuth && !isAuthenticated()) {
    // redirect unauthenticated users to home(search page)
    return "/search";
  }
});

export default router;
