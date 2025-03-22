import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getToken } from "../../utils";

import Header from "../Homepage/Header";

export default function Information() {
  const token = useSelector((state) => state.user.token) || getToken();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchByName, setSearchByName] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(3);
  const [inputPage, setInputPage] = useState("1");
  const navigate = useNavigate();
  const [totalCount, setTotalCount] = useState(0);
  const totalPages = Math.ceil(totalCount / pageSize);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    if (page > totalPages && totalPages > 0) {
      setPage(totalPages, page);
    }
  }, [totalPages]);

  const fetchData = () => {
    setLoading(true);
    setError(null);

    if (!token) {
      setError("No token found, please log in.");
      setLoading(false);
      return;
    }

    let url = searchByName
      ? `http://35.213.150.144:8000/api/imports/?query=${searchByName}`
      : `http://35.213.150.144:8000/api/imports/?page=${page}&page_size=${pageSize}`;

    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (res.status === 404) {
          console.warn(`No data found for name: ${searchByName}`);
          setData([]);
          setLoading(false);
          return null;
        }
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (!json) return;
        setData(json.results || []);
        setTotalCount(json.count || 0);
        setLastUpdate(new Date());
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, [page, pageSize, searchByName]);

  const getPageNumbers = () => {
    if (totalPages <= 5) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    if (page <= 3) {
      return [1, 2, 3, 4, "...", totalPages];
    }
    if (page >= totalPages - 2) {
      return [1, "...", totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
    }
    return [1, "...", page - 1, page, page + 1, "...", totalPages];
  };

  const handlePageSizeChange = (e) => {
    const newSize = parseInt(e.target.value, 10);
    if (!isNaN(newSize) && newSize > 0 && newSize <= totalCount) {
      setPageSize(newSize);
      setPage(1);
      setInputPage("1");
    }
  };

  const handleRefresh = () => {
    fetchData();
  };

  return (
    <div className="min-h-screen min-w-max dark:bg-slate-700 dark:text-cyan-400">
      <Header />
      <div className="max-w-7xl mx-auto px-4 py-6">
         {/* Banner: gray-100 for light color, #253445 for dark color */}
         <div className="mb-4 p-6 rounded-lg bg-gray-100 dark:bg-[#253445] shadow-lg flex items-center space-x-4">
           <svg
             className="h-10 w-10 text-blue-500 animate-bounce"
             fill="none"
             stroke="currentColor"
             viewBox="0 0 24 24"
           >
             <path
               strokeLinecap="round"
               strokeLinejoin="round"
               strokeWidth="2"
               d="M9 17v-6h13M9 17l-4-4m4 4l-4 4"
             />
           </svg>
           <h1 className="text-4xl font-extrabold drop-shadow">
             Information Page
           </h1>
         </div>
 
         {/* Breadcrumb navigation */}
         <nav className="mb-6" aria-label="Breadcrumb">
           <ol className="list-reset flex text-sm text-gray-600 dark:text-gray-300">
             <li>
               <a href="/" className="hover:underline">
                 Home
               </a>
             </li>
             <li>
               <span className="mx-2">/</span>
             </li>
             <li className="font-semibold">Information</li>
           </ol>
         </nav>
 
         {/* Filter area: gray-100 for light colors, #253445 for dark colors */}
         <div className="mb-6 p-6 bg-gray-100 dark:bg-[#253445] rounded-xl shadow-lg border border-transparent hover:border-blue-300 transition-all flex flex-col md:flex-row items-center gap-6">
           <div className="flex-1 w-full md:w-auto">
             <label className="block text-sm font-medium mb-2">
               Search by Name
             </label>
             <div className="relative">
               <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                 <svg
                   className="h-5 w-5 text-gray-400 dark:text-gray-300"
                   fill="currentColor"
                   viewBox="0 0 20 20"
                 >
                   <path
                     fillRule="evenodd"
                     d="M12.9 14.32a8 8 0 111.414-1.414l4.292 4.292a1 1 0 01-1.414 1.414l-4.292-4.292zm-4.9.68a6 6 0 100-12 6 6 0 000 12z"
                     clipRule="evenodd"
                   />
                 </svg>
               </span>
               {/* The text is black in dark mode, you can change it to white if needed */}
               <input
                 type="text"
                 placeholder="Search file name..."
                 value={searchByName}
                 onChange={(e) => setSearchByName(e.target.value)}
                 className="pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded w-full
                            bg-white dark:bg-gray-600 text-gray-900 dark:text-black 
                            focus:outline-none focus:border-blue-500 transition-colors"
               />
             </div>
          </div>

          {/* Page Size */}
          <div>
             <label className="block text-sm font-medium mb-2">Page Size</label>
            <input
              type="number"
              value={pageSize}
              onChange={handlePageSizeChange}
               className="p-2 border border-gray-300 dark:border-gray-600 rounded w-24
                          bg-white dark:bg-gray-600 text-gray-900 dark:text-black
                          focus:outline-none focus:border-blue-500 transition-colors"
              min="1"
              max={totalCount}
            />
          </div>
          </div>

          {/* Stats card: gray-100 for light colors, #253445 for dark colors */}
         <div className="mb-6 p-4 bg-gray-100 dark:bg-[#253445] rounded-xl shadow-lg flex items-center justify-between">
           <div>
             <p className="text-lg font-semibold">
               Total Records: {totalCount}
             </p>
             <p className="text-sm">
               Last updated: {lastUpdate.toLocaleTimeString()}
             </p>
           </div>
           <button
             onClick={handleRefresh}
             className="flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-all transform hover:scale-105"
           >
             <svg
               className="h-5 w-5"
               fill="none"
               stroke="currentColor"
               viewBox="0 0 24 24"
             >
               <path
                 strokeLinecap="round"
                 strokeLinejoin="round"
                 strokeWidth="2"
                 d="M4 4v6h6M20 20v-6h-6M5 19a9 9 0 0114-8.5"
               />
             </svg>
             <span>Refresh</span>
           </button>
         </div>

             {/* Data table area: gray-100 for light color, #253445 for dark color */}
         <div className="bg-gray-100 dark:bg-[#253445] rounded-xl shadow-lg">
           {/* Header: gray-200 for light color, #2F3C4B for dark color */}
           <div className="grid grid-cols-6 items-center px-4 py-3 text-center font-semibold 
                           bg-gray-200 dark:bg-[#2F3C4B] rounded-t-xl">
             <span className="flex items-center justify-center space-x-1">
               <span>File Name</span>
               <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M7 7l3-3 3 3H7zM7 13l3 3 3-3H7z" />
               </svg>
             </span>
             <span className="flex items-center justify-center space-x-1">
               <span>ID</span>
               <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M7 7l3-3 3 3H7zM7 13l3 3 3-3H7z" />
               </svg>
             </span>
             <span className="flex items-center justify-center space-x-1">
               <span>User</span>
               <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M7 7l3-3 3 3H7zM7 13l3 3 3-3H7z" />
               </svg>
             </span>
             <span className="flex items-center justify-center space-x-1">
               <span>Total Rows</span>
               <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M7 7l3-3 3 3H7zM7 13l3 3 3-3H7z" />
               </svg>
             </span>
             <span className="flex items-center justify-center space-x-1">
               <span>Time Uploaded</span>
               <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M7 7l3-3 3 3H7zM7 13l3 3 3-3H7z" />
               </svg>
             </span>
             <span>Action</span>
          </div>

          {/* Loading & Error */}
          {loading && (
             <div className="p-4 text-center">
               <div className="inline-block w-8 h-8 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
            </div>
            )}
           {error && <p className="p-4 text-center text-red-500">Error: {error}</p>}

            {/* Data list */}
           {!loading && !error && data.length > 0 ? (
             data
               .filter((item) =>
                 searchByName
                   ? item.data?.filename?.toLowerCase().includes(searchByName.toLowerCase())
                   : true
               )
               .map((item) => (
                 <div
                   key={item.id}
                   className="grid grid-cols-6 items-center px-4 py-3 text-center 
                              border-b last:border-0 border-gray-300 dark:border-gray-600 
                              hover:bg-gray-50 dark:hover:bg-[#2F3C4B] transition-all transform hover:scale-[1.01]"
                 >
                   <span className="truncate">
                     {item.data?.filename || "N/A"}
                   </span>
                   <span>{item.id}</span>
                   <span>{item.uploaded_by || "Unknown"}</span>
                   <span>{item.data?.total_rows || 0}</span>
                   <span>{new Date(item.uploaded_at).toLocaleString()}</span>
                   <span>
                     <button
                       onClick={() => navigate(`/info/${item.id}`)}
                       className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-all transform hover:scale-105"
                       title="View details"
                     >
                       View
                     </button>
                   </span>
                 </div>
               ))
           ) : (
             !loading && <p className="p-4 text-center">No data available.</p>
           )}
         </div>
 
         {/* Pagination component */}
         <div className="mt-6 flex flex-col md:flex-row items-center justify-between gap-6">
           <div className="flex items-center space-x-2">
             <button
               onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
               disabled={page === 1}
               className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 
                          rounded disabled:opacity-50 hover:bg-gray-400 dark:hover:bg-gray-500 
                          transition-all transform hover:scale-105"
             >
               {"<"}
             </button>
             {getPageNumbers().map((num, index) => (
              <button
              key={index}
              onClick={() => typeof num === "number" && setPage(num)}
              disabled={num === "..."}
              className={`px-3 py-1 rounded transition-all transform hover:scale-105 ${
                num === page
                  ? "bg-blue-500 text-white"
                  : "bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 hover:bg-gray-400 dark:hover:bg-gray-500"
              }`}
              >
                {num}
              </button>
              ))}
              <button
                onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages || totalPages === 0}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 
                           rounded disabled:opacity-50 hover:bg-gray-400 dark:hover:bg-gray-500 
                           transition-all transform hover:scale-105"
              >
                {">"}
              </button>
            </div>
  
            <div className="flex items-center space-x-2">
              <span>Jump to Page:</span>
              <input
                type="number"
                value={inputPage}
                onChange={(e) => setInputPage(e.target.value)}
                className="p-2 border border-gray-300 dark:border-gray-600 rounded w-24 
                           bg-white dark:bg-gray-600 text-gray-900 dark:text-black
                           focus:outline-none focus:border-blue-500 transition-colors"
                min="1"
                max={totalPages}
                placeholder="Page #"
              />
              <button
                onClick={() => {
                  const newPage = parseInt(inputPage, 10);
                  if (!isNaN(newPage) && newPage > 0 && newPage <= totalPages) {
                    setPage(newPage);
                  }
                }}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-all transform hover:scale-105"
              >
                Go
              </button>
          </div>
        </div>
      </div>
    </div>
  );
}