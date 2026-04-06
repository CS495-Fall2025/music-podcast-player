import { reactive } from "vue";
import router from "../router";

export const statusState = reactive({
  isLoading: false,
  error: null,
  // error object should have: { type, title, message, actionText, onAction }
});

export function setLoading(isLoading) {
  statusState.isLoading = isLoading;
}

export function setError(
  errorType,
  title,
  message,
  actionText = null,
  onAction = null,
) {
  statusState.error = { type: errorType, title, message, actionText, onAction };
}

export function clearError() {
  statusState.error = null;
}

export function clearStatus() {
  statusState.isLoading = false;
  statusState.error = null;
}

export function navigateToError(
  errorType,
  title,
  message,
  actionText = null,
  onAction = null,
) {
  setError(errorType, title, message, actionText, onAction);
  setLoading(false);
  router.push("/error");
}
