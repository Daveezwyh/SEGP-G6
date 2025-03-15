import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { getToken } from "../../utils";
import { useNavigate } from "react-router-dom";

import Header from "../Homepage/Header";
import Footer from "../Homepage/footer";

export default function Information() {
  const token = useSelector((state) => state.user.token) || getToken();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchId, setSearchId] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(3);
  const [inputPage, setInputPage] = useState("1");
  const navigate = useNavigate();
  const [totalCount, setTotalCount] = useState(0);
  const totalPages = Math.ceil(totalCount / pageSize);

  useEffect(() => {
    if (page > totalPages && totalPages > 0) {
      setPage(totalPages);
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

    let url = searchId
      ? `http://35.213.150.144:8000/api/imports/${searchId}/`
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
                // When search ID is not found, show no data instead of an error
                console.warn(`No data found for ID: ${searchId}`);
                setData([]);
                setLoading(false);
                return null;
            }
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            return res.json();
        })
      .then((json) => {
        if (!json) return; // If no data is returned, exit early

            console.log("API Response:", json);
        if (searchId) {
          setData(json ? [json] : []);
        } else {
          setData(json.results || []);
          setTotalCount(json.count || 0);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, [page, pageSize, searchId]);

  const filteredData = searchId
    ? data.filter((item) => item.id.toString() === searchId)
    : data;

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

  return (
    <div className="min-h-screen  dark:bg-gray-700  dark:text-cyan-400">
      <Header />
      <div className="flex">
        <div className="flex-1 p-9">
          <h1 className="text-xl font-bold mb-4">Information Page</h1>

          {/* Search */}
          <div className="mb-4 flex items-center space-x-2">
            <input
              type="number"
              placeholder="Search by ID"
              value={searchId}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, "");
                if (value === "" || (parseInt(value, 10) > 0 && parseInt(value, 10) <= totalCount)) {
                  setSearchId(value);
                }
              }}
              className="p-2 border rounded w-full md:w-1/3 dark:bg-gray-800"
              min="1"
              max={totalCount}
            />
          </div>

          {/* Page Size */}
          <div className="mb-4 flex items-center space-x-2 dark:bg">
            <span>Page Size:</span>
            <input
              type="number"
              value={pageSize}
              onChange={(e) => {
                const newSize = parseInt(e.target.value, 10);
                if (!isNaN(newSize) && newSize > 0 && newSize <= totalCount) {
                  setPageSize(newSize);
                  setPage(1);
                  setInputPage("1");
                }
              }}
              className="p-2 border rounded w-20 dark:bg-gray-800"
              min="1"
              max={totalCount}
            />
          </div>

          {/* Data */}
          <div className=" dark:bg-gray-800 rounded-lg shadow p-4 dark:text-cyan-400">
              {/* Header */}
              <div className="grid grid-cols-5 items-center px-4 py-2 text-center">
                <span className="w-40">File Name</span>
                <span className="w-10 ">ID</span>
                <span className="w-20 ">User</span>
                <span className="w-40">Time Uploaded</span>
                <span></span>
              </div>

              <hr className="my-2" />
              
              {loading && <p>Loading...</p>}
              {error && <p className="text-red-500">Error: {error}</p>}
              {!loading && !error && filteredData.length > 0 ? (
                filteredData.map((item) => (
                  <div key={item.id} className=" grid grid-cols-5 items-center px-4 py-2  text-center rounded-lg shadow dark:bg-gray-800 m-3">
                    <span className="w-40 truncate">{item.data?.filename || "N/A"}</span>
                    <span className="w-10 ">{item.id}</span>
                    <span className="w-20 ">{item.uploaded_by || "Unknown"}</span>
                    <span className="w-60">{new Date(item.uploaded_at).toLocaleString()}</span>
                    <span><button
                      onClick={() => navigate(`/info/${item.id}`)}
                      className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
                    >
                      View
                    </button></span>
                  </div>
                ))
              ) : (
                <p>No data available.</p>
              )}
          </div>

          {/* Page Navigation */}
          <div className="mt-12 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-800 rounded disabled:opacity-50"
              >
                {'<'}
              </button>
              {getPageNumbers().map((num, index) => (
                <button
                  key={index}
                  onClick={() => typeof num === "number" && setPage(num)}
                  className={`px-3 py-1 rounded ${num === page ? "bg-blue-500 text-white" : "bg-gray-300 dark:bg-gray-800"}`}
                  disabled={num === "..."}
                >
                  {num}
                </button>
              ))}
              <button
                onClick={() => setPage((prev) => prev + 1)}
                disabled={page === totalPages}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-800 rounded"
              >
                {'>'}
              </button>
            </div>

            {/* Jump to Page */}
            <div className="flex items-center space-x-2">
              <span>Jump to Page:</span>
              <input
                type="number"
                value={inputPage}
                onChange={(e) => setInputPage(e.target.value)}
                className="p-2 border rounded w-24 dark:bg-gray-800"
                min="1"
                max={totalPages}
                placeholder="Page Number"
              />
              <button
                onClick={() => {
                  const newPage = parseInt(inputPage);
                  if (!isNaN(newPage) && newPage > 0 && newPage <= totalPages) setPage(newPage);
                }}
                className="px-4 py-2 bg-blue-500 text-white rounded"
              >
                Go
              </button>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}