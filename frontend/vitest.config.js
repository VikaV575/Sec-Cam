import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      react: path.resolve(__dirname, "node_modules/react"),
      "react-dom": path.resolve(__dirname, "node_modules/react-dom"),
      "react/jsx-runtime": path.resolve(
        __dirname,
        "node_modules/react/jsx-runtime.js",
      ),
      "react/jsx-dev-runtime": path.resolve(
        __dirname,
        "node_modules/react/jsx-dev-runtime.js",
      ),
      "@testing-library/react": path.resolve(
        __dirname,
        "node_modules/@testing-library/react/dist/index.js",
      ),
      "@testing-library/jest-dom/vitest": path.resolve(
        __dirname,
        "node_modules/@testing-library/jest-dom/dist/vitest.mjs",
      ),
    },
  },
  server: {
    fs: {
      allow: [".."],
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    include: ["../tests/unit/frontend/**/*.test.{js,jsx}"],
    setupFiles: "../tests/unit/frontend/setup.js",
  },
});
