import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { getToken } from "../../utils";
import { FaChevronUp, FaChevronDown } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export default function Information() {
  const token = useSelector((state) => state.user.token) || getToken();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchId, setSearchId] = useState("");
  const navigate = useNavigate();

  const fetchData = () => {
    setLoading(true);
    setError(null);

    if (!token) {
      setError("No token found, please log in.");
      setLoading(false);
      return;
    }

    const url = `http://35.213.150.144:8000/api/imports/`;

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
          window.location.href = "/login";
          throw new Error("Unauthorized: Token expired or invalid.");
        }
        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }
        return res.json();
      })
      .then((json) => {
        console.log("API Response:", json);
        setData(json || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredData = searchId
    ? data.filter((item) => item.id.toString() === searchId)
    : data;

  const incrementSearchId = () => {
    setSearchId((prev) => (prev ? (parseInt(prev) + 1).toString() : "1"));
  };

  const decrementSearchId = () => {
    setSearchId((prev) => (prev && parseInt(prev) > 1 ? (parseInt(prev) - 1).toString() : ""));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-bold mb-4">Information Page</h1>
      <div className="mb-4 flex items-center space-x-2">
        <input
          type="text"
          placeholder="Search by ID"
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          className="p-2 border rounded w-full md:w-1/3 text-black"
        />
        <div className="flex flex-col">
          <button onClick={incrementSearchId} className="p-1 bg-gray-300 dark:bg-gray-700 rounded">
            <FaChevronUp />
          </button>
          <button onClick={decrementSearchId} className="p-1 bg-gray-300 dark:bg-gray-700 rounded mt-1">
            <FaChevronDown />
          </button>
        </div>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 text-black dark:text-gray-200">
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
    </div>
  );
}