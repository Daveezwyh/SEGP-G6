import { useState } from "react";
import { GoSidebarCollapse, GoSidebarExpand } from "react-icons/go";
import { HiUserCircle } from "react-icons/hi";
import { IoIosLogOut } from "react-icons/io";
import { IoTimeOutline } from "react-icons/io5";
import { MdOutlineFileUpload } from "react-icons/md";

export default function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const [showLogout, setShowLogout] = useState(false);

    const toggleSidebar = () => {
        setIsOpen(prevState => !prevState);
    };

    const openLogout = () => {
        setShowLogout(true);
    }

    const closeLogout = () => {
        setShowLogout(false);
    }

    return (
        <>
            {/* sidebar container */}
            <div className={`fixed top-0 left-0 h-screen
                ${isOpen ? 'w-20' : 'w-0'}
                sm:${isOpen ? 'w-20' : 'w-0'}
                md:${isOpen ? 'w-24' : 'w-0'}
                lg:${isOpen ? 'w-28' : 'w-0'}
                transition-width duration-150 m-0 flex flex-col shadow-lg bg-side dark:bg-slate-700`}>
                
                {!isOpen && (
                    <HeaderIcon icon={<GoSidebarCollapse size="40" onClick={toggleSidebar} />}
                    label="Expand" moveRight="ml-10"
                    />
                )}

                {isOpen && (
                    <>
                        <SidebarIcon icon = {<GoSidebarExpand size ="40" onClick={toggleSidebar} />} label="Close"/>
                        <SidebarIcon icon = {<MdOutlineFileUpload size ="40" />} label="Upload File"/>
                        <SidebarIcon icon = {<IoTimeOutline size ="40" />} label="Recent Files"/>
                        <div className="mt-auto">
                            <SidebarIcon icon = {<IoIosLogOut size ="40" onClick = {openLogout} />} label="Log Out"/>
                        </div>
                    </>
                )}
            </div>

            {showLogout && (
            <div className="fixed top-0 left-0 w-full h-full flex justify-center items-center bg-black bg-opacity-50">
                <div className="card text-center shadow-lg p-4 bg-white text-blacks dark:bg-slate-700 dark:text-cyan-400">
                    <div className="card-body d-flex flex-column align-items-center">
                        <div className="mb-3">
                            <HiUserCircle size="100" className="text-gray-400 dark:text-white" />
                        </div>
                        <p className="card-text mb-4">Are you sure you want to log out?</p>
                        
                        <div className="d-flex justify-content-center gap-3">
                            <button onClick={closeLogout} className="btn btn-secondary px-4">
                                Cancel
                            </button>
                            <button className="btn btn-danger px-4">
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

const SidebarIcon = ({ icon, label }) => (
    <div className="relative flex flex-col items-center group">
        <div className="sidebar-icon">{icon}</div>
        {/* Tooltip */}
        <span className="absolute bottom-12 scale-0 group-hover:scale-100 transition-all bg-gray-800 text-white text-xs px-2 py-1 rounded-md">
            {label}
        </span>
    </div>
);


const HeaderIcon = ({ icon, label, moveRight = "" }) => (
    <div className="relative flex flex-col items-center group">
    <div className={`header-icon ${moveRight}`}>{icon}</div>
        <span className="absolute bottom-12 scale-0 group-hover:scale-100 transition-all bg-gray-800 text-white text-xs px-2 py-1 rounded-md">
                {label}
        </span>
    </div>
);

