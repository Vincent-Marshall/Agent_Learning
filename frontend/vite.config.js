import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 开发期前端跑在 5173,API 请求代理到 FastAPI(:8000)——前后端分离的标准姿势。
// 生产环境则由 FastAPI 直接托管 build 产物(dist),不经过此代理。
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
