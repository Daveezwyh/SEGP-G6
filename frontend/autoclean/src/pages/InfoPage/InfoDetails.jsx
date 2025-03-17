import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { getToken } from "../../utils";
import Swal from 'sweetalert2';

import Header from "../Homepage/Header";
import Footer from "../Homepage/footer";

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
    const [headers, setHeaders] = useState([]);
    const [showTabs, setShowTabs] = useState(false);
    const [activeTab, setActiveTab] = useState(0);

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

                if (data.results && data.results.length > 0) {
                    const firstRow = data.results[0].data;
                    setHeaders(Object.keys(firstRow));
                }
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
        <div className="min-h-screen min-w-[1000px] dark:bg-slate-700 dark:text-cyan-400">
            <Header />
            <div className="flex">
                <div className="flex-1 p-9  dark:bg-slate-700  shadow-md">
                    <h1 className="text-xl font-bold mb-4">File Details (ID: {id})</h1>

                    <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <span>Page Size:</span>
                        <input
                            type="number"
                            value={pageSize}
                            onChange={(e) => {
                                const newSize = parseInt(e.target.value, 10);
                                if (!isNaN(newSize) && newSize > 0) {
                                    setPageSize(newSize);
                                    setPage(1);
                                    setInputPage("1");
                                }
                            }}
                            className="p-2 border rounded w-20 dark:bg-gray-800 "
                            min="1"
                        />
                    </div>

                    <button
                        onClick={() => {
                            Swal.fire({
                            title: 'Confirm?',
                            text: 'Do you want clean data?',
                            icon: 'info',
                            showCancelButton: true,
                            confirmButtonColor: '#3085d6',
                            cancelButtonColor: '#d33',
                            confirmButtonText: 'Yes',
                        }).then((result) => {
                            if(result.isConfirmed){
                            setPageSize(3); // Reset to default page size
                            setPage(1); // Reset to the first page
                            setInputPage("1"); // Reset the input field
                            setShowTabs(true);
                        }
                      });
                    }}
                        className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded text-white"
                    >
                        Clean
                    </button>
                </div>

                    <div className="e dark:bg-gray-800 rounded-lg shadow p-4 dark:text-cyan-400">
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
                                {details.results?.length > 0 ? (
                                    <table className="min-w-full border-collapse">
                                    <thead>
                                        <tr>
                                            {headers.map((header) => (
                                                <th key={header} className="border px-4 py-2 bg-gray-400 dark:bg-gray-700">
                                                    {header}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {details.results.map((record) => (
                                            <tr key={record.id} className="hover:bg-gray-100 dark:hover:bg-gray-600">
                                                {headers.map((header) => (
                                                    <td key={header} className="border px-4 py-2">
                                                        {record.data[header] ?? "-"}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                ) : (
                                    <p>No records available.</p>
                                )}

                                <div className="pt-4">
                                <button
                                    onClick={() => navigate(-1)}
                                    className="mb-1 px-4 py-2 bg-gray-700 rounded"
                                >
                                    Back
                                </button>
                                </div>

                                {/* Pagination Controls */}
                                <div className="mt-12 flex items-center justify-between">
                                    <div className="mt-4 flex items-center space-x-2">
                                        <button
                                            onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                                            disabled={page === 1}
                                            className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
                                        >
                                            {"<"}
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
                                            {">"}
                                        </button>
                                    </div>

                                    <div className="flex items-center space-x-2 ml-auto">
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
                        ) : (
                            <p>No details available.</p>
                        )}
                    </div>

                    {showTabs && (
                <div className="mt-6 border-b border-gray-300">
                    <ul className="flex space-x-6 border-b">
                        {["Errors", "Dropdown", "Link", "Disabled"].map((tab, index) => (
                            <li
                                key={index}
                                className={`p-3 px-3 cursor-pointer transition-all duration-300
                                    ${
                                        activeTab === index
                                            ? "border-b-2 border-blue-500 text-black font-semibold bg-gray-100"
                                            : "text-blue-500 hover:text-blue-700"
                                    } 
                                    ${tab === "Disabled" ? "text-gray-400 cursor-not-allowed" : ""}
                                `}
                                onClick={() => tab !== "Disabled" && setActiveTab(index)}
                            >
                                {tab}
                            </li>
                        ))}
                    </ul>

                    {/* Tab Content Section */}
                    <div className="p-6 bg-white rounded-lg shadow-md transition-opacity duration-300">
                        {activeTab === 0 && <div>🔥 <strong>Errors</strong> Data Goes Here</div>}
                        {activeTab === 1 && <div>📂 <strong>Dropdown</strong> Data Content</div>}
                        {activeTab === 2 && <div>🔗 <strong>Link</strong> Data Content</div>}
                        {activeTab === 3 && <div> <strong>Hello</strong> Content</div>}
                    </div>
                </div>
            )}


                </div>
            </div>
            <Footer />
        </div>
    );
}