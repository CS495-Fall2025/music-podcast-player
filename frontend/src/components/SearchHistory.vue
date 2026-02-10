<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import {
  searchHistory,
  saveSearchHistory,
  loadSearchHistory,
  clearSearchHistory,
  setSaveHistory,
} from "../controllers/searchHistory.js";
import { requestFeeds } from "../controllers/backendFeedParser.js";

const emit = defineEmits(["select"]);
const showHistory = ref(false);
const boxRef = ref(null);
const buttonRef = ref(null);

function selectHistory(item) {
  requestFeeds(item);
  showHistory.value = false;
}

function handleClickOutside(e) {
  if (
    boxRef.value &&
    !boxRef.value.contains(e.target) &&
    !buttonRef.value.contains(e.target)
  ) {
    showHistory.value = false;
  }
}

onMounted(() => {
  loadSearchHistory();
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<template>
  <div class="history-container">
    <button ref="buttonRef" @click="showHistory = !showHistory">History</button>

    <div v-if="showHistory" ref="boxRef" class="history-box">
      <div v-if="!saveSearchHistory">
        <em>Search history is disabled.</em>
      </div>

      <ul v-else>
        <li
          v-for="item in searchHistory"
          :key="item"
          @click="selectHistory(item)"
        >
          {{ item }}
        </li>
      </ul>

      <div class="controls">
        <button @click="clearSearchHistory">Clear Search History</button>

        <label>
          <input
            type="checkbox"
            :checked="saveSearchHistory"
            @change="setSaveHistory($event.target.checked)"
          />
          Save search history
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-container {
  position: relative;
}

.history-box {
  position: absolute;
  top: 120%;
  right: 0;
  width: 300px;
  background: white;
  border: 1px solid #ccc;
  padding: 8px;
  z-index: 10;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  padding: 6px;
  cursor: pointer;
  color: #333;
}

div {
  color: #333;
}

label {
  color: #333;
}

li:hover {
  background: #f0f0f0;
}

.controls {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
