import React, { useEffect, useState } from "react";
import { IoChevronBackSharp, IoChevronForwardSharp } from "react-icons/io5";
import { useSelector } from "react-redux";
import { useLocation } from "react-router-dom";
import { getToken } from "../../utils";

export default function Information() {
  const token = useSelector((state) => state.user.token) || getToken();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const importIds = queryParams.get("importIds")?.split(",") || [];

  const [fileData, setFileData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pages, setPages] = useState({});
  const [pageSize, setPageSize] = useState(5); // Default items per page

  const fetchData = (importId, page = 1 , customPageSize = pageSize) => {
    setLoading(true);
    setError(null);

    if (!token) {
      setError("No token found, please log in.");
      setLoading(false);
      return;
    }

    const url = `http://35.213.150.144:8000/api/imports/${importId}/data/?page=${page}&page_size=${customPageSize}`;


    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (res.status === 401) {
          localStorage.removeItem("token");
          sessionStorage.removeItem("token");
          window.location.href = "/";
          throw new Error("Unauthorized: Token expired or invalid.");
        }
        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }
        return res.json();
      })
      .then((json) => {
        setFileData((prevData) => ({
          ...prevData,
          [importId]: {
            results: json.results || [],
            totalPages: Math.ceil(json.count / pageSize),
          },
        }));
        setPages((prevPages) => ({
          ...prevPages,
          [importId]: page,
        }));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    importIds.forEach((importId) => {
      if (!fileData[importId]){
      fetchData(importId);
      }
    });
  }, [importIds]); 

  const handlePrevPage = (importId) => {
    if (pages[importId] > 1) {
      fetchData(importId, pages[importId] - 1);
    }
  };

  const handleNextPage = (importId) => {
    if (pages[importId] < (fileData[importId]?.totalPages || 1)) {
      fetchData(importId, pages[importId] + 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-bold mb-4">Information Page</h1>
      
      <div className="flex flex-col">
              <label className="text-sm font-semibold mb-1">Page Size</label>
            </div>
      <input
                type="number"
                className="border p-1 rounded dark:bg-gray-700 dark:text-white"
                value={pageSize}
                onChange={(e) => {
                  const newSize = Number(e.target.value);
                  if (newSize > 0) {
                    setPageSize(newSize);
                    const updatedPages = { ...pages };
                    importIds.forEach((importId) => {
                      updatedPages[importId] = 1; // Reset page number to 1
                      fetchData(importId, 1, newSize); // Pass the new page size directly
                    });
                    setPages(updatedPages);
                  }
                }}
                min="1"
              />

      {importIds.length === 0 && <p>No files found.</p>}

      {importIds.map((importId) => (
        <div key={importId} className=" dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 mb-6 dark:text-gray-200">        
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-bold">Import ID: {importId}</h2>  
          </div>

          <div className="bg-gray-200 dark:bg-gray-700 w-full min-h-[10rem] rounded p-4 mb-4">
            {loading && <p>Loading...</p>}
            {error && <p className="text-red-500">Error: {error}</p>}
            {!loading && !error && fileData[importId]?.results?.length > 0 ? (
              <ul>
                {fileData[importId].results.map((item) => (
                  <li key={item.id} className="mb-2">
                    <strong>ID:</strong> {item.id} <br />
                    <strong>Name:</strong> {item.data?.Name || "N/A"} <br />
                    <strong>Age:</strong> {item.data?.Age || "N/A"} <br />
                    <strong>Salary:</strong> {item.data?.Salary || "N/A"}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No data available.</p>
            )}
          </div>

          <div className="flex justify-end items-center">
            <div className="flex items-center bg-gray-600 text-white rounded-full px-3 py-2 space-x-3">
              <button
                onClick={() => handlePrevPage(importId)}
                disabled={pages[importId] <= 1}
                className={`w-8 h-8 flex items-center justify-center rounded-full ${
                  pages[importId] <= 1 ? "bg-gray-500 cursor-not-allowed" : "bg-gray-700 hover:bg-gray-600"
                }`}
              >
                <IoChevronBackSharp size={18} />
              </button>
              <span className="font-semibold text-sm">
                {pages[importId]} of {fileData[importId]?.totalPages || 1}
              </span>
              <button
                onClick={() => handleNextPage(importId)}
                disabled={pages[importId] >= (fileData[importId]?.totalPages || 1)}
                className={`w-8 h-8 flex items-center justify-center rounded-full ${
                  pages[importId] >= (fileData[importId]?.totalPages || 1) ? "bg-gray-500 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
                }`}
              >
                <IoChevronForwardSharp size={18} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
