/// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath } from "url";
import { dirname } from "path";
import path from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
