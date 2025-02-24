import { useState } from "react";
import { MdOutlineFileUpload } from "react-icons/md";
import { IoTimeOutline } from "react-icons/io5";
import { IoIosLogOut } from "react-icons/io";
import { GoSidebarExpand, GoSidebarCollapse } from "react-icons/go";
import { HiUserCircle } from "react-icons/hi";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const[showLogout, setShowLogout] = useState(false);
    const navigate = useNavigate();

    const toggleSidebar = () => {
        setIsOpen(prevState => !prevState);
    };

    const openLogout = () => {
        setShowLogout(true);
    }

    const closeLogout = () => {
        setShowLogout(false);
    }

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/");
    };

    return (
        <>
            <div className={`fixed top-0 left-0 h-screen ${isOpen ? 'w-20' : 'w-0'} sm:${isOpen ? 'w-20' : 'w-0'} md:${isOpen ? 'w-24' : 'w-0'} lg:${isOpen ? 'w-28' : 'w-0'} transition-width duration-150 m-0 flex flex-col shadow-lg bg-side dark:bg-slate-700`}>
                {!isOpen && (
                    <HeaderIcon icon={<GoSidebarCollapse size="40" onClick={toggleSidebar} />} />
                )}

                {isOpen && (
                    <>
                        <SidebarIcon icon={<GoSidebarExpand size="40" onClick={toggleSidebar} />} />
                        <SidebarIcon icon={<MdOutlineFileUpload size="40" />} />
                        <SidebarIcon icon={<IoTimeOutline size="40" />} />
                        <div className="mt-auto">
                            <SidebarIcon icon={<IoIosLogOut size="40" onClick={openLogout} />} />
                        </div>
                    </>
                )}
            </div>
            {showLogout && (
            <div className="position-fixed top-0 start-0 w-100 h-100 z-index:999 d-flex justify-content-center align-items-center bg-dark bg-opacity-75">
                <div className="card text-center shadow-lg p-4  dark:bg-slate-700 dark:text-cyan-400">
                    <div className="card-body d-flex flex-column align-items-center">
                        <div className="mb-3">
                            <HiUserCircle size="100" className="text-gray-400 dark:text-white" />
                        </div>
                        <p className="card-text mb-4">Are you sure you want to log out?</p>
                        
                        <div className="d-flex justify-content-center gap-3">
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

const SidebarIcon = ({ icon }) => (
    <div className="sidebar-icon">
        {icon}
    </div>
);

const HeaderIcon = ({ icon }) => (
    <div className="header-icon">
        {icon}
    </div>
);

