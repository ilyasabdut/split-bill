// vitest.config.js
import { defineConfig } from "file:///home/ubuntu/repository/split-bill/web/node_modules/vitest/dist/config.js";
import { sveltekit } from "file:///home/ubuntu/repository/split-bill/web/node_modules/@sveltejs/kit/src/exports/vite/index.js";
var vitest_config_default = defineConfig({
  plugins: [sveltekit()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/lib/tests/setup.js"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      extensions: ["js", "ts", "svelte"],
      include: ["src/lib/**/*"],
      exclude: [
        "src/lib/tests/**",
        "src/lib/**/*.test.{js,ts}",
        "src/lib/**/*.spec.{js,ts}",
        "**/*.d.ts",
        "**/*.config.{js,ts}"
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 90,
        statements: 90
      }
    }
  },
  resolve: {
    alias: {
      $lib: "/src/lib",
      $app: "/src/app"
    }
  }
});
export {
  vitest_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZXN0LmNvbmZpZy5qcyJdLAogICJzb3VyY2VzQ29udGVudCI6IFsiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIi9ob21lL3VidW50dS9yZXBvc2l0b3J5L3NwbGl0LWJpbGwvd2ViXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvaG9tZS91YnVudHUvcmVwb3NpdG9yeS9zcGxpdC1iaWxsL3dlYi92aXRlc3QuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9ob21lL3VidW50dS9yZXBvc2l0b3J5L3NwbGl0LWJpbGwvd2ViL3ZpdGVzdC5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlc3QvY29uZmlnJztcbmltcG9ydCB7IHN2ZWx0ZWtpdCB9IGZyb20gJ0BzdmVsdGVqcy9raXQvdml0ZSc7XG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG5cdHBsdWdpbnM6IFtzdmVsdGVraXQoKV0sXG5cdHRlc3Q6IHtcblx0XHRlbnZpcm9ubWVudDogJ2pzZG9tJyxcblx0XHRnbG9iYWxzOiB0cnVlLFxuXHRcdHNldHVwRmlsZXM6IFsnLi9zcmMvbGliL3Rlc3RzL3NldHVwLmpzJ10sXG5cdFx0Y292ZXJhZ2U6IHtcblx0XHRcdHByb3ZpZGVyOiAndjgnLFxuXHRcdFx0cmVwb3J0ZXI6IFsndGV4dCcsICdqc29uJywgJ2h0bWwnXSxcblx0XHRcdGV4dGVuc2lvbnM6IFsnanMnLCAndHMnLCAnc3ZlbHRlJ10sXG5cdFx0XHRpbmNsdWRlOiBbJ3NyYy9saWIvKiovKiddLFxuXHRcdFx0ZXhjbHVkZTogW1xuXHRcdFx0XHQnc3JjL2xpYi90ZXN0cy8qKicsXG5cdFx0XHRcdCdzcmMvbGliLyoqLyoudGVzdC57anMsdHN9Jyxcblx0XHRcdFx0J3NyYy9saWIvKiovKi5zcGVjLntqcyx0c30nLFxuXHRcdFx0XHQnKiovKi5kLnRzJyxcblx0XHRcdFx0JyoqLyouY29uZmlnLntqcyx0c30nXG5cdFx0XHRdLFxuXHRcdFx0dGhyZXNob2xkczoge1xuXHRcdFx0XHRsaW5lczogOTAsXG5cdFx0XHRcdGZ1bmN0aW9uczogOTAsXG5cdFx0XHRcdGJyYW5jaGVzOiA5MCxcblx0XHRcdFx0c3RhdGVtZW50czogOTBcblx0XHRcdH1cblx0XHR9XG5cdH0sXG5cdHJlc29sdmU6IHtcblx0XHRhbGlhczoge1xuXHRcdFx0JGxpYjogJy9zcmMvbGliJyxcblx0XHRcdCRhcHA6ICcvc3JjL2FwcCdcblx0XHR9XG5cdH1cbn0pO1xuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUF3UyxTQUFTLG9CQUFvQjtBQUNyVSxTQUFTLGlCQUFpQjtBQUUxQixJQUFPLHdCQUFRLGFBQWE7QUFBQSxFQUMzQixTQUFTLENBQUMsVUFBVSxDQUFDO0FBQUEsRUFDckIsTUFBTTtBQUFBLElBQ0wsYUFBYTtBQUFBLElBQ2IsU0FBUztBQUFBLElBQ1QsWUFBWSxDQUFDLDBCQUEwQjtBQUFBLElBQ3ZDLFVBQVU7QUFBQSxNQUNULFVBQVU7QUFBQSxNQUNWLFVBQVUsQ0FBQyxRQUFRLFFBQVEsTUFBTTtBQUFBLE1BQ2pDLFlBQVksQ0FBQyxNQUFNLE1BQU0sUUFBUTtBQUFBLE1BQ2pDLFNBQVMsQ0FBQyxjQUFjO0FBQUEsTUFDeEIsU0FBUztBQUFBLFFBQ1I7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsTUFDRDtBQUFBLE1BQ0EsWUFBWTtBQUFBLFFBQ1gsT0FBTztBQUFBLFFBQ1AsV0FBVztBQUFBLFFBQ1gsVUFBVTtBQUFBLFFBQ1YsWUFBWTtBQUFBLE1BQ2I7QUFBQSxJQUNEO0FBQUEsRUFDRDtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1IsT0FBTztBQUFBLE1BQ04sTUFBTTtBQUFBLE1BQ04sTUFBTTtBQUFBLElBQ1A7QUFBQSxFQUNEO0FBQ0QsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
