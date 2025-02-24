import React, { useState, useEffect } from "react";
import { CiSettings } from "react-icons/ci";

export default function Header() {
  const [darkMode, setDarkMode] = useState(false);
  const [showSetting, setSetting] = useState(false);

  useEffect(() => {
    const handleSystemThemeChange = (e) => {
      const prefersDarkMode = e.matches;
      setDarkMode(prefersDarkMode);
      document.body.classList.toggle("dark", prefersDarkMode);
    };

    const prefersDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDarkMode(prefersDarkMode);
    document.body.classList.toggle("dark", prefersDarkMode);

    const darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    darkModeMediaQuery.addEventListener("change", handleSystemThemeChange);

    return () => {
      darkModeMediaQuery.removeEventListener("change", handleSystemThemeChange);
    };
  }, []);

  const toggleDarkMode = () => {
    setDarkMode((prevState) => {
      const newMode = !prevState;
      document.body.classList.toggle("dark", newMode);
      return newMode;
    });
  };

  const toggleSettings = () => {
    setSetting((prevState) => !prevState);
  };

  return (
    <>
      <header className={`bg-main shadow-lg relative ${darkMode ? "text-cyan-400" : "text-white"}`}>
        <div className="container flex justify-between items-center">
          <div> </div>
          <div className="text-2xl font-bold">AutoClean</div>
          <HeaderIcon icon={<CiSettings size="40" />} onClick={toggleSettings} />
        </div>
      </header>

      {showSetting && (
        <div className="relative">
          <div className="absolute top-0 right-0 mr-4 w-64 card text-center z-999  shadow-lg p-4 dark:bg-slate-700 dark:text-cyan-400">
            <div className="card-body d-flex flex-column align-items-center">
              <h4>Toggle Light and Dark Mode</h4>
              <label className="inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={toggleDarkMode}
                  className="sr-only peer"
                />
                <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

const HeaderIcon = ({ icon, onClick }) => (
  <div className="header-icon" onClick={onClick}>
    {icon}
  </div>
);
