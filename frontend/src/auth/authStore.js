import { ref, computed } from "vue";
import { jwtDecode } from "jwt-decode";

const TOKEN_KEY = "access_token";

// Reactive auth state
const token = ref(localStorage.getItem(TOKEN_KEY));

function updateAuthState() {
  token.value = localStorage.getItem(TOKEN_KEY);
}

export function useAuth() {
  const isAuthenticated = computed(() => {
    if (!token.value) return false;
    try {
      const payload = jwtDecode(token.value);
      return payload.exp * 1000 > Date.now();
    } catch (e) {
      console.error("Invalid token", e);
      return false;
    }
  });

  const currentUser = computed(() => {
    if (!token.value) return null;
    try {
      const payload = jwtDecode(token.value);
      return {
        username: payload.name || "Unknown",
        email: payload.email || null,
      };
    } catch (e) {
      console.error("Failed to parse JWT", e);
      return null;
    }
  });

  const completeLogin = (newToken) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    token.value = newToken;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    token.value = null;
  };

  const verifyToken = async () => {
    const currentToken = token.value;
    if (!currentToken) return false;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_AUTH_API}/auth/verify`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: currentToken }),
        },
      );

      if (!response.ok) {
        // Token is invalid, remove it
        logout();
        return false;
      }

      const data = await response.json();
      return data.valid === true;
    } catch (e) {
      console.error("Failed to verify token:", e);
      // On network error, keep the token but log the error
      return true;
    }
  };

  const startLogin = () => {
    window.location.href = "/login";
  };

  return {
    isAuthenticated,
    currentUser,
    token: token,
    completeLogin,
    logout,
    verifyToken,
    startLogin,
    updateAuthState,
  };
}
