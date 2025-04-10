import React, { useState, useEffect } from "react";
import { CiSettings } from "react-icons/ci";
import Sidebar from "./bars/Sidebar";
import { GoSidebarExpand } from "react-icons/go";

export default function Header() {
    const [darkMode, setDarkMode] = useState(() => {
        const savedTheme = localStorage.getItem("darkMode");
        return savedTheme !== null ? savedTheme === "true" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    });
    const [showSetting, setSetting] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    useEffect(() => {
        document.body.classList.toggle("dark", darkMode);
        localStorage.setItem("darkMode", darkMode);
    }, [darkMode]);

    const toggleDarkMode = () => {
        setDarkMode((prevDarkMode) => !prevDarkMode);
    };

    const toggleSettings = () => setSetting((prevState) => !prevState);
    const toggleSidebar = () => setIsSidebarOpen((prevState) => !prevState);

    return (
        <>
            <header className={`bg-main shadow-lg relative ${darkMode ? "text-cyan-400" : "text-white"}`}>
                <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
                <div className="container flex items-center px-6 h-20">
                <div className="absolute left-4 p-2 cursor-pointer" onClick={toggleSidebar}>
                        <GoSidebarExpand size="40" />
                    </div>
                    <div className="text-2xl font-bold flex-1 text-center">AutoClean</div>

                    <div className="absolute right-4 p-2 cursor-pointer" onClick={toggleSettings}>
                        <CiSettings size="40" />
                    </div>
                </div>
            </header>

            {showSetting && (
                <div className="relative">
                    <div className="absolute top-0 right-0 mr-4 w-64 card text-center shadow-lg p-4 dark:bg-slate-700 dark:text-cyan-400">
                        <div className="card-body flex flex-col items-center">
                            <h4>Light and Dark Mode</h4>
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
