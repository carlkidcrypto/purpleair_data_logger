import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    preserveSymlinks: true,
  },
  test: {
    environment: "node",
    globals: true,
    include: ["vitest/**/*.test.ts"],
  },
});
