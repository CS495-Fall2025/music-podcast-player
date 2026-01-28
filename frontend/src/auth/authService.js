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

export function startLogin() {
  auth.startLogin();
}

export function completeLogin(token) {
  auth.completeLogin(token);
}

export function logout() {
  auth.logout();
}

// Also export the store itself for components that need reactivity
export { useAuth };
