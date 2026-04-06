import { reactive } from "vue";

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
