import { useState } from "react";
import { GoSidebarCollapse, GoSidebarExpand } from "react-icons/go";
import { HiUserCircle } from "react-icons/hi";
import { IoIosLogOut } from "react-icons/io";
import { IoTimeOutline } from "react-icons/io5";
import { MdOutlineFileUpload } from "react-icons/md";
import { useNavigate } from "react-router-dom";

export default function Sidebar({ isOpen, toggleSidebar }) {
    const [showLogout, setShowLogout] = useState(false);
    const navigate = useNavigate();

    const openLogout = () => setShowLogout(true);
    const closeLogout = () => setShowLogout(false);

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/");
    };

    const handleNavigateToHome = () => {
        navigate("/homepage");
    };

    const handleNavigateRecentFiles = () => {
        navigate("/info");
    };

    return (
        <>
            <div
                className={`fixed top-0 left-0 h-full z-50 bg-side dark:bg-slate-700 shadow-lg transition-transform duration-300 ${
                    isOpen ? "translate-x-0 w-20" : "-translate-x-full w-0"
                }`}
            >
                <div className="flex flex-col h-full p-2 transition-all duration-300">
                    <SidebarIcon
                        icon={<GoSidebarCollapse size="40" onClick={toggleSidebar} />}
                        label="Close"
                        isOpen={isOpen}
                        extraClass="-mt-4"
                    />
                    <SidebarIcon
                        icon={<MdOutlineFileUpload size="40" onClick={handleNavigateToHome} />}
                        label="Upload File"
                        isOpen={isOpen}
                        extraClass="-mt-4"
                    />
                    <SidebarIcon
                        icon={<IoTimeOutline size="40" onClick={handleNavigateRecentFiles} />}
                        label="Recent Files"
                        isOpen={isOpen}
                        extraClass="-mt-4"
                    />
                    <div className="mt-auto">
                        <SidebarIcon
                            icon={<IoIosLogOut size="40" onClick={openLogout} />}
                            label="Log Out"
                            isOpen={isOpen}
                        />
                    </div>
                </div>
            </div>

            {showLogout && (
                <div className="fixed top-0 left-0 w-full h-full flex justify-center items-center bg-black bg-opacity-50 z-50">
                    <div className="card text-center shadow-lg p-4 bg-white text-black dark:bg-slate-700 dark:text-cyan-400">
                        <div className="card-body flex flex-col items-center">
                            <HiUserCircle size="100" className="text-gray-400 dark:text-white mb-3" />
                            <p className="card-text mb-4">Are you sure you want to log out?</p>
                            <div className="flex gap-3">
                                <button onClick={closeLogout} className="btn btn-secondary px-4">
                                    Cancel
                                </button>
                                <button onClick={handleLogout} className="btn btn-danger px-4">
                                    Log Out
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

const SidebarIcon = ({ icon, label, isOpen, extraClass = "" }) => (
    <div
        className={`relative flex flex-col items-center group p-2 transition-all duration-300 ${extraClass} ${
            isOpen ? "translate-x-0 opacity-100" : "-translate-x-20 opacity-0"
        }`}
    >
        <div className="sidebar-icon">{icon}</div>
        <span className="absolute left-14 bg-gray-800 text-white text-xs px-2 py-1 rounded-md shadow-md scale-0 group-hover:scale-100 transition-all">
            {label}
        </span>
    </div>
);
