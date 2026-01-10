import jwtDecode from "jwt-decode";

// JWT will be stored in localStorage
const TOKEN_KEY = "access_token";

export function isAuthenticated() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;

  try {
    const payload = jwtDecode(token);
    // Check expiry
    return payload.exp * 1000 > Date.now();
  } catch (e) {
    console.error("Invalid token", e);
    return false;
  }
}

/**
 * gets current user info from JWT
 */
export function getCurrentUser() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;

  try {
    const payload = jwtDecode(token);
    return {
      username: payload.name || payload.preferred_username || "Unknown",
      email: payload.email || null,
    };
  } catch (e) {
    console.error("Failed to parse JWT", e);
    return null;
  }
}

export function startLogin() {
  // PKCE, state, etc. handled here if needed
  window.location.href = import.meta.env.VITE_AUTH_API + "/authorize";
}

// stores JWT in localstorage
export function completeLogin(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}
