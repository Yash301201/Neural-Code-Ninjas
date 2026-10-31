import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({base:'/app/',plugins:[react(),tailwindcss()],server:{host:'127.0.0.1',port:3000,proxy:{'/auth':'http://127.0.0.1:8001','/ui':'http://127.0.0.1:8001','/portal':'http://127.0.0.1:8001','/api':'http://127.0.0.1:8001','/health':'http://127.0.0.1:8001'}},build:{outDir:'dist',emptyOutDir:true,rollupOptions:{output:{manualChunks:{charts:['recharts'],react:['react','react-dom','react-router-dom']}}}}});
