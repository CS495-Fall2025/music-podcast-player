<script setup>
import { onMounted } from "vue";
import {
  searchHistory,
  saveSearchHistory,
  loadSearchHistory,
  setSaveHistory,
} from "../controllers/searchHistory.js";

const emit = defineEmits(["select"]);

function selectHistory(item) {
  emit("select", item);
}

onMounted(() => {
  loadSearchHistory();
});
</script>

<template>
  <div class="history-box">
    <div v-if="!saveSearchHistory">
      <em>Search history is disabled.</em>
    </div>

    <template v-else>
      <ul v-if="searchHistory.length">
        <li
          v-for="item in searchHistory"
          :key="item"
          @click="selectHistory(item)"
        >
          {{ item }}
        </li>
      </ul>

      <div v-else>
        <em>No recent searches.</em>
      </div>
    </template>

    <div class="controls">
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
</template>

<style scoped>
.history-box {
  position: absolute;
  top: 120%;
  right: 0;
  width: 300px;
  background: white;
  border: 1px solid #ccc;
  padding: 8px;
  z-index: 10;
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
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
