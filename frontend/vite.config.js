import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { name, version } from "./package.json";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
	define: {
		__NAME__: JSON.stringify(name),
		__VERSION__: JSON.stringify(version),
	},
});
