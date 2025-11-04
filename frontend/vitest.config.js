/// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup/test-setup.js"],
    include: ["tests/**/*.test.js"],
    deps: {
      inline: ["vue-router"],
    },
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
