import { ref, computed } from "vue";

import loadConfig from "../config";

// Track authentication state without storing the token
// The token is in an httpOnly cookie, inaccessible to JavaScript
const isLoggedIn = ref(false);
const currentUserData = ref(null);

// Refresh token check interval (every 30 minutes)
let refreshInterval = null;

export function useAuth() {
  const isAuthenticated = computed(() => isLoggedIn.value);

  const currentUser = computed(() => currentUserData.value);

  const completeLogin = async () => {
    // Verify the authentication succeeded by checking the cookie
    const verified = await verifyToken();
    if (verified) {
      isLoggedIn.value = true;
      startAutoRefresh();
    }
  };

  const logout = async () => {
    try {
			const config = await loadConfig();

      // Call backend to clear cookies
      await fetch(`${config.backendUrl}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      console.error("Logout request failed:", e);
    }

    isLoggedIn.value = false;
    currentUserData.value = null;
    stopAutoRefresh();
  };

  const verifyToken = async () => {
    try {
			const config = await loadConfig();
      const response = await fetch(
        `${config.backendUrl}/auth/verify`,
        {
          method: "POST",
          credentials: "include", // Send cookies
        },
      );

      if (!response.ok) {
        isLoggedIn.value = false;
        currentUserData.value = null;
        return false;
      }

      const data = await response.json();
      if (data.valid === true) {
        isLoggedIn.value = true;
        currentUserData.value = {
          username: data.user.username,
          email: data.user.email,
        };
        return true;
      }

      return false;
    } catch (e) {
      console.error("Failed to verify token:", e);
      // On network error, keep the current state
      return isLoggedIn.value;
    }
  };

  const refreshToken = async () => {
    try {
			const config = await loadConfig();
      const response = await fetch(
        `${config.backendUrl}/auth/refresh`,
        {
          method: "POST",
          credentials: "include", // Send refresh token cookie
        },
      );

      if (!response.ok) {
        // Refresh failed - user needs to log in again
        await logout();
        return false;
      }

      // Access token cookie has been updated
      return true;
    } catch (e) {
      console.error("Failed to refresh token:", e);
      return false;
    }
  };

  const startAutoRefresh = () => {
    stopAutoRefresh();
    // Refresh every 30 minutes (access token expires in 1 hour)
    refreshInterval = setInterval(
      async () => {
        const success = await refreshToken();
        if (!success) {
          console.log("Auto-refresh failed, stopping interval");
          stopAutoRefresh();
        }
      },
      30 * 60 * 1000,
    );
  };

  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  };

  const startLogin = () => {
    window.location.href = "/login";
  };

  return {
    isAuthenticated,
    currentUser,
    completeLogin,
    logout,
    verifyToken,
    refreshToken,
    startLogin,
  };
}
