import { ref } from "vue";

const MAX_HISTORY = 25;
const COOKIE_NAME = "searchHistory";
const SETTINGS_COOKIE = "saveSearchHistory";

export const searchHistory = ref([]);
export const saveSearchHistory = ref(true);

// Cookie helper functions
function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name, value, maxAge = 31536000) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}`;
}

function deleteCookie(name) {
  document.cookie = `${name}=; Max-Age=0; path=/`;
}

// load search history
export function loadSearchHistory() {
  const saved = getCookie(COOKIE_NAME);
  const setting = getCookie(SETTINGS_COOKIE);

  saveSearchHistory.value = setting !== "false";

  if (saved && saveSearchHistory.value) {
    try {
      searchHistory.value = JSON.parse(saved);
    } catch {
      searchHistory.value = [];
    }
  }
}

// add search query
export function addSearch(query) {
  if (!saveSearchHistory.value || !query) return;

  searchHistory.value = searchHistory.value.filter((q) => q !== query);
  searchHistory.value.unshift(query);

  if (searchHistory.value.length > MAX_HISTORY) {
    searchHistory.value.pop();
  }
  while (JSON.stringify(searchHistory.value).length > 25000) {
    searchHistory.value.pop();
  }

  setCookie(COOKIE_NAME, JSON.stringify(searchHistory.value));
}

export function clearSearchHistory() {
  searchHistory.value = [];
  deleteCookie(COOKIE_NAME);
}

export function setSaveHistory(enabled) {
  saveSearchHistory.value = enabled;
  setCookie(SETTINGS_COOKIE, enabled);

  if (!enabled) {
    clearSearchHistory();
  }
}
