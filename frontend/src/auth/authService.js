import { jwtDecode } from "jwt-decode";

const TOKEN_KEY = "access_token";

export function isAuthenticated() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;

  try {
    const payload = jwtDecode(token);
    return payload.exp * 1000 > Date.now();
  } catch (e) {
    console.error("Invalid token", e);
    return false;
  }
}

// gets current user info from JWT
export function getCurrentUser() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;

  try {
    const payload = jwtDecode(token);
    return {
      username: payload.name || "Unknown",
      email: payload.email || null,
    };
  } catch (e) {
    console.error("Failed to parse JWT", e);
    return null;
  }
}

export function startLogin() {
  window.location.href = import.meta.env.VITE_AUTH_API + "/auth";
}

// stores JWT in localstorage
export function completeLogin(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}
