import { useEffect, useState } from "react";
import Home from "./pages/Home.jsx";

const THEME_STORAGE_KEY = "subtitle-theme";
const DEFAULT_THEME = "aurora";

export default function App() {
  const [theme, setTheme] = useState(() => {
    const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
    return saved || DEFAULT_THEME;
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  return (
    <div className="min-h-screen">
      <Home theme={theme} setTheme={setTheme} />
    </div>
  );
}
