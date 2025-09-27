/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",   // 扫描 React 组件里的 className
  ],
  theme: {
    extend: {
      colors: {
        user: "#3B82F6",     // 蓝色 (用户气泡)
        bot: "#E5E7EB"       // 灰色 (机器人气泡)
      }
    },
  },
  plugins: [],
};
