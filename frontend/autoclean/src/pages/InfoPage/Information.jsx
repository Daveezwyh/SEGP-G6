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
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState("All");
  const navigate = useNavigate();
  const [totalCount, setTotalCount] = useState(0);
  const totalPages = pageSize === "All" ? 1 : Math.ceil(totalCount / pageSize);

  const fetchData = () => {
    setLoading(true);
    setError(null);
  
    if (!token) {
      setError("No token found, please log in.");
      setLoading(false);
      return;
    }
  
    let url;
    if (searchId) {
      url = `http://35.213.150.144:8000/api/imports/${searchId}/`;
    } else {
      url = `http://35.213.150.144:8000/api/imports/?page=${page}`;
      if (pageSize !== "All") {
        url += `&page_size=${pageSize}`;
      }
    }
  
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

  const incrementSearchId = () => {
    setSearchId((prev) => (prev ? (parseInt(prev) + 1).toString() : "1"));
  };

  const decrementSearchId = () => {
    setSearchId((prev) => (prev && parseInt(prev) > 1 ? (parseInt(prev) - 1).toString() : ""));
  };

  const incrementPageSize = () => {
    setPage(1);
    setPageSize((prev) => (prev === "All" ? 1 : prev + 1));
  };

  const decrementPageSize = () => {
    setPage(1);
    setPageSize((prev) => (prev > 1 ? prev - 1 : "All"));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 dark:bg-gray-900 dark:text-white">
      <h1 className="text-xl font-bold mb-4">Information Page</h1>

      {/* Search */}
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

      {/* Page Number*/}
      <div className="mb-4 flex items-center space-x-2">
        <button
          onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
          className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded"
          disabled={page === 1}
        >
          Prev
        </button>

        <input
          type="number"
          value={page}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            if (!isNaN(value) && value > 0 && value <= totalPages) {
              setPage(value);
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && page > 0 && page <= totalPages) {
              fetchData();
            }
          }}
          className="w-16 p-2 border rounded text-center text-black"
        />

        <button
          onClick={() => setPage((prev) => (prev < totalPages ? prev + 1 : prev))}
          className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded"
          disabled={page >= totalPages}
        >
          Next
        </button>
      </div>

      {/* Page Size*/}
      <div className="mb-4 flex items-center space-x-2">
        <label className="mr-2">Page Size:</label>
        <input
          type="text"
          value={pageSize}
          onChange={(e) => {
            let value = e.target.value.trim();
            if (value.toLowerCase() === "all") {
              setPageSize("All");
            } else {
              const num = parseInt(value);
              setPageSize(!isNaN(num) && num > 0 ? num : "All");
            }
            setPage(1);
          }}
          className="p-2 border rounded bg-white text-black w-20 text-center"
          placeholder="All"
        />
        <div className="flex flex-col">
          <button onClick={incrementPageSize} className="p-1 bg-gray-300 dark:bg-gray-700 rounded">
            <FaChevronUp />
          </button>
          <button onClick={decrementPageSize} className="p-1 bg-gray-300 dark:bg-gray-700 rounded mt-1">
            <FaChevronDown />
          </button>
        </div>
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
    </div>
  );
}
