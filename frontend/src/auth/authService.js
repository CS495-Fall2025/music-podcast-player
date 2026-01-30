import { useAuth } from "./authStore";

// For backwards compatibility, export functions that use the store
const auth = useAuth();

export function isAuthenticated() {
  return auth.isAuthenticated.value;
}

export function getCurrentUser() {
  return auth.currentUser.value;
}

export async function verifyToken() {
  return auth.verifyToken();
}

export async function refreshToken() {
  return auth.refreshToken();
}

export function startLogin() {
  auth.startLogin();
}

export async function completeLogin() {
  return auth.completeLogin();
}

export async function logout() {
  return auth.logout();
}

// Also export the store itself for components that need reactivity
export { useAuth };
