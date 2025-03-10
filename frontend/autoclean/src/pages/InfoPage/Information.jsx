import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { getToken } from "../../utils";
import { useNavigate } from "react-router-dom";

import Header from "../Homepage/Header";
import Sidebar from "../Homepage/bars/Sidebar";
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
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then((json) => {
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
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 dark:text-white">
      <Header />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 p-9 bg-white dark:bg-gray-800 rounded-lg shadow-md">
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
              className="p-2 border rounded w-full md:w-1/3 text-black"
              min="1"
              max={totalCount}
            />
          </div>

          {/* Page Size */}
          <div className="mb-4 flex items-center space-x-2">
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
              className="p-2 border rounded w-20 text-black"
              min="1"
              max={totalCount}
            />
          </div>

          {/* Data */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-black dark:text-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {loading && <p>Loading...</p>}
              {error && <p className="text-red-500">Error: {error}</p>}
              {!loading && !error && filteredData.length > 0 ? (
                filteredData.map((item) => (
                  <div key={item.id} className="bg-gray-200 dark:bg-gray-700 rounded-lg p-4 shadow-md">
                    <strong>ID:</strong> {item.id} <br />
                    <strong>Description:</strong> {item.description || "N/A"} <br />
                    <strong>Filename:</strong> {item.data?.filename || "N/A"} <br />
                    <strong>Total Rows:</strong> {item.data?.total_rows || 0} <br />
                    <strong>Uploaded By:</strong> {item.uploaded_by || "Unknown"} <br />
                    <strong>Uploaded At:</strong> {new Date(item.uploaded_at).toLocaleString()} <br />
                    <button
                      onClick={() => navigate(`/info/${item.id}`)}
                      className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
                    >
                      View
                    </button>
                  </div>
                ))
              ) : (
                <p>No data available.</p>
              )}
            </div>
          </div>

          {/* Page Navigation */}
          <div className="mt-12 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                {'<'}
              </button>
              {getPageNumbers().map((num, index) => (
                <button
                  key={index}
                  onClick={() => typeof num === "number" && setPage(num)}
                  className={`px-3 py-1 rounded ${num === page ? "bg-blue-500 text-white" : "bg-gray-300 dark:bg-gray-700"}`}
                  disabled={num === "..."}
                >
                  {num}
                </button>
              ))}
              <button
                onClick={() => setPage((prev) => prev + 1)}
                disabled={page === totalPages}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded"
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
                className="p-2 border rounded w-24 text-black"
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