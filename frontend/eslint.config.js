import js from "@eslint/js";
import globals from "globals";
import pluginVue from "eslint-plugin-vue";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,vue}"],
    plugins: { js },
    extends: ["js/recommended"],
    ignores: ["dist/**"],

    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        __NAME__: "readonly",
        __VERSION__: "readonly",
        global: "readonly",
      },
    },

    rules: {
      "no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
    },
  },

  pluginVue.configs["flat/essential"],
]);
