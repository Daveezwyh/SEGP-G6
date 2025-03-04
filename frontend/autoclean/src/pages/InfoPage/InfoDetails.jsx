import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { getToken } from "../../utils";

export default function InfoDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = useSelector((state) => state.user.token) || getToken();
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(3);
  const [inputPage, setInputPage] = useState("1");

  useEffect(() => {
    if (!id) return;

    const fetchDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(
          `http://35.213.150.144:8000/api/imports/${id}/data/?page=${page}&page_size=${pageSize}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (res.status === 401) {
          localStorage.removeItem("token");
          sessionStorage.removeItem("token");
          window.location.href = "/login";
          throw new Error("Unauthorized: Token expired or invalid.");
        }
        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        setDetails(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id, page, pageSize]);

  const totalPages = details ? Math.ceil(details.count / pageSize) : 1;

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
    <div className="min-h-screen bg-gray-100 p-6 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-bold mb-4">File Details (ID: {id})</h1>
      <button
        onClick={() => navigate(-1)}
        className="mb-4 px-4 py-2 bg-gray-500 text-white rounded"
      >
        Back
      </button>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-black dark:text-gray-200">
        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p className="text-red-500">Error: {error}</p>
        ) : details ? (
          <div>
            <h2 className="font-bold text-lg">File Data</h2>
            <p>
              <strong>Total Records:</strong> {details.count}
            </p>
            <h3 className="mt-4 font-bold">Records:</h3>
            <ul className="list-disc list-inside">
              {details.results?.length > 0 ? (
                details.results.map((record) => (
                  <li key={record.id} className="p-2 border rounded my-2">
                    <p>
                      <strong>ID:</strong> {record.id}
                    </p>
                    <p>
                      <strong>Name:</strong> {record.data.Name}
                    </p>
                    <p>
                      <strong>Age:</strong> {record.data.Age}
                    </p>
                    <p>
                      <strong>Gender:</strong> {record.data.Gender}
                    </p>
                    <p>
                      <strong>Salary:</strong> {record.data.Salary}
                    </p>
                  </li>
                ))
              ) : (
                <p>No records available.</p>
              )}
            </ul>

            {/* Pagination Controls */}
            <div className="mt-4 flex items-center space-x-2">
              <span>Page Size:</span>
              <input
                type="number"
                value={pageSize}
                onChange={(e) => {
                  const newSize = parseInt(e.target.value, 10);
                  if (!isNaN(newSize) && newSize > 0) setPageSize(newSize);
                }}
                className="p-2 border rounded w-20 text-black"
                min="1"
              />
              <span>Page Navigation:</span>
              <button
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                Previous Page
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
                Next Page
              </button>
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
        ) : (
          <p>No details available.</p>
        )}
      </div>
    </div>
  );
}