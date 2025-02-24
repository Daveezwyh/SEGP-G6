import React, { useEffect, useState } from "react";
import { IoChevronBackSharp, IoChevronForwardSharp } from "react-icons/io5";
import { useSelector } from "react-redux";
import { getToken } from "../../utils";

export default function Information() {
  const token = useSelector((state) => state.user.token) || getToken();

  // API parameters
  const [importId, setImportId] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(2);
  const [totalPages, setTotalPages] = useState(1);

  // Data & fetch status
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch function with Authorization token
  const fetchData = () => {
    setLoading(true);
    setError(null);

    if (!token) {
      setError("No token found, please log in.");
      setLoading(false);
      return;
    }

    const url = `http://35.213.150.144:8000/api/imports/${importId}/data/?page=${page}&page_size=${pageSize}`;

    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (res.status === 401) {
          localStorage.removeItem("token");
          sessionStorage.removeItem("token");
          window.location.href = "/login";
          throw new Error("Unauthorized: Token expired or invalid.");
        }
        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }
        return res.json();
      })
      .then((json) => {
        setData(json.results || []);
        setTotalPages(Math.ceil(json.count / pageSize));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  // Fetch data when parameters change
  useEffect(() => {
    fetchData();
  }, [importId, page, pageSize]);

  // Handlers for next/prev pages
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-bold mb-4">Information Page</h1>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 text-black dark:text-gray-200">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <div className="flex flex-col">
            <label className="text-sm font-semibold mb-1">Import ID</label>
            <input
              type="number"
              className="border p-1 rounded"
              value={importId}
              onChange={(e) => setImportId(e.target.value)}
            />
          </div>
          <div className="flex flex-col">
            <label className="text-sm font-semibold mb-1">Page Size</label>
            <input
              type="number"
              className="border p-1 rounded"
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
            />
          </div>
        </div>

        {/* Data Display */}
        <div className="bg-gray-200 dark:bg-gray-700 w-full min-h-[10rem] rounded p-4 mb-4">
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">Error: {error}</p>}

          {!loading && !error && data.length > 0 ? (
            <ul>
              {data.map((item) => (
                <li key={item.id} className="mb-2">
                  <strong>ID:</strong> {item.id} <br />
                  <strong>Name:</strong> {item.data.Name} <br />
                  <strong>Age:</strong> {item.data.Age} <br />
                  <strong>Salary:</strong> {item.data.Salary}
                </li>
              ))}
            </ul>
          ) : (
            <p>No data available.</p>
          )}
        </div>

        {/* Pagination Controls */}
        <div className="flex justify-end items-center">
          <div className="flex items-center bg-gray-600 text-white rounded-full px-3 py-2 space-x-3">
            <button
              onClick={handlePrevPage}
              disabled={page <= 1}
              className={`w-8 h-8 flex items-center justify-center rounded-full
                ${page <= 1 ? "bg-gray-500 cursor-not-allowed" : "bg-gray-700 hover:bg-gray-600"}`}
            >
              <IoChevronBackSharp size={18} />
            </button>

            <span className="font-semibold text-sm">
              {page} of {totalPages}
            </span>

            <button
              onClick={handleNextPage}
              disabled={page >= totalPages}
              className={`w-8 h-8 flex items-center justify-center rounded-full
                ${page >= totalPages ? "bg-gray-500 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"}`}
            >
              <IoChevronForwardSharp size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
