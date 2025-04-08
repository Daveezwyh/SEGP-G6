import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import Swal from "sweetalert2";
import { getToken } from "../../utils";

import Header from "../Homepage/Header";

const parseColumnName = (message) => {
    const match = message.match(/column '(.+?)'/);
    return match ? match[1] : null;
};

export default function InfoDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const token = useSelector((state) => state.user.token) || getToken();
    const [details, setDetails] = useState(null);
    const [statusText, setStatusText] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(3);
    const [inputPage, setInputPage] = useState("1");
    const [headers, setHeaders] = useState([]);
    const [activeTab, setActiveTab] = useState(0);
    const [scanResults, setScanResult] = useState([]);
    const [loadingScan, setLoadingScan] = useState(false);
    const [errorScan, setErrorScan] = useState(null);
    const [jumpEnabled, setJumpEnabled] = useState(false);
    const [highlightCell, setHighlightCell] = useState(null);
    const [pendingHighlight, setPendingHighlight] = useState(null);
    const [showProgressModal, setShowProgressModal] = useState(false);
    const [progressUuid, setProgressUuid] = useState("");
    const [progress, setProgress] = useState(0);
    const [progressStatus, setProgressStatus] = useState("processing");
    const [pollingIntervalId, setPollingIntervalId] = useState(null);
    const [expandedDetails, setExpandedDetails] = useState({});

    useEffect(() => {
        if (!id) return;
        fetchDetails();
        fetchStatusText();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id, page, pageSize]);

    useEffect(() => {
        if (activeTab === 1) {
            fetchScanResults();
        }
    }, [activeTab]);

    useEffect(() => {
        if (pendingHighlight && details && details.results && details.results.length > 0) {
            const rowInPage = pendingHighlight.row % pageSize;
            if (rowInPage < details.results.length) {
                setHighlightCell({ row: rowInPage, col: pendingHighlight.col });
                setTimeout(() => {
                    setHighlightCell(null);
                    setPendingHighlight(null);
                }, 1500);
            }
        }
    }, [details, pendingHighlight, pageSize]);

    useEffect(() => {
        return () => {
            if (pollingIntervalId) {
                clearInterval(pollingIntervalId);
            }
        };
    }, [pollingIntervalId]);

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
            if (res.status === 404) {
                setError("File has already been cleaned.");
                setDetails(null);
                setLoading(false);
                return;
            }
            if (!res.ok) throw new Error(`Server error: ${res.status}`);

            const data = await res.json();
            setDetails(data);

            if (data.results?.length > 0) {
                setHeaders(Object.keys(data.results[0].data));
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchStatusText = async () => {
        try {
            const res = await fetch(`http://35.213.150.144:8000/api/imports/${id}/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                const data = await res.json();
                setStatusText(data.status_text);
            }
        } catch (err) {
            console.error("Failed to fetch status_text:", err);
        }
    };

    const fetchScanResults = async () => {
        setLoadingScan(true);
        setErrorScan(null);
        try {
            const res = await fetch(
                `http://35.213.150.144:8000/api/imports/${id}/scan-results/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
            }

            const data = await res.json();

            let rawArray = [];
            if (Array.isArray(data)) {
                rawArray = data;
            } else if (Array.isArray(data.results)) {
                rawArray = data.results;
            }

            const result = rawArray.map((item) => ({
                message: item.message,
                import_scan_result_id: item.id,
                row: item.row,
                col: item.col,
                actions: item.actions || [],
            }));

            setScanResult(result);
        } catch (err) {
            setErrorScan(err.message);
        } finally {
            setLoadingScan(false);
        }
    };

    const handleClean = () => {
        Swal.fire({
            title: "Confirm Cleaning?",
            text: "Are you sure you want to clean this file?",
            icon: "info",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes",
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const res = await fetch("http://35.213.150.144:8000/api/imports/start-clean/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({ id }),
                    });

                    if (res.status === 400) {
                        const errorData = await res.json();
                        Swal.fire("Error", errorData.error, "error");
                        return;
                    }

                    if (!res.ok) {
                        throw new Error(`Cleaning failed: ${res.status}`);
                    }

                    const data = await res.json();
                    if (data.task_progress_uuid) {
                        setProgressUuid(data.task_progress_uuid);
                        setShowProgressModal(true);
                        setProgress(0);
                        setProgressStatus("processing");
                        startPolling(data.task_progress_uuid);
                    } else {
                        Swal.fire("Error", "No task_progress_uuid returned by server.", "error");
                    }
                } catch (err) {
                    Swal.fire("Error", err.message, "error");
                }
            }
        });
    };

    // Fully Automated Cleaning
    const handleFullyAutomatedCleaning = () => {
        Swal.fire({
            title: "Warning",
            text: "This is a fully automated process, it will ignore your current ScanResultActions.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Proceed",
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const res = await fetch("http://35.213.150.144:8000/api/imports/clean-auto/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({ id }),
                    });

                    if (res.status === 400) {
                        const errorData = await res.json();
                        Swal.fire("Error", errorData.error, "error");
                        return;
                    }

                    if (!res.ok) {
                        throw new Error(`Cleaning failed: ${res.status}`);
                    }

                    const data = await res.json();
                    if (data.task_progress_uuid) {
                        setProgressUuid(data.task_progress_uuid);
                        setShowProgressModal(true);
                        setProgress(0);
                        setProgressStatus("processing");
                        startPolling(data.task_progress_uuid);
                    } else {
                        Swal.fire("Error", "No task_progress_uuid returned by server.", "error");
                    }
                } catch (err) {
                    Swal.fire("Error", err.message, "error");
                }
            }
        });
    };

    const handleExport = async () => {
        try {
            const res = await fetch(
                `http://35.213.150.144:8000/api/imports/${id}/export/`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            let errorBody = null;
            if (!res.ok) {
                try {
                    errorBody = await res.json();
                } catch (err) {
                    console.error("Failed to parse error body:", err);
                }
            }

            if (res.status === 400 && errorBody?.error === "Import has not yet been processed.") {
                Swal.fire("Notice", "File is not cleaned yet, please clean it before exporting.", "info");
                return;
            }

            if (res.status === 404) {
                Swal.fire("Notice", "File does not exist or was not found.", "info");
                return;
            }

            if (!res.ok) {
                throw new Error(errorBody?.error || `Export failed: ${res.status}`);
            }

            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.setAttribute("download", `file_${id}.csv`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (err) {
            Swal.fire("Error", err.message, "error");
        }
    };

    const startPolling = (uuid) => {
        if (pollingIntervalId) {
            clearInterval(pollingIntervalId);
        }

        const intervalId = setInterval(() => {
            pollProgress(uuid);
        }, 1000);

        setPollingIntervalId(intervalId);
    };

    const pollProgress = async (uuid) => {
        try {
            const url = `http://35.213.150.144:8000/api/task-progress/${uuid}`;
            const res = await fetch(url, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
            if (!res.ok) {
                throw new Error(`Failed to fetch progress: ${res.status}`);
            }
            const data = await res.json();

            const newProgress = parseFloat(data.percentage || "0");
            setProgress(newProgress);
            setProgressStatus(data.status || "processing");

            if (newProgress >= 100 || data.status === "completed") {
                clearInterval(pollingIntervalId);
                setPollingIntervalId(null);
            }
        } catch (err) {
            console.error("Error fetching progress:", err);
            clearInterval(pollingIntervalId);
            setPollingIntervalId(null);
            Swal.fire("Error", err.message, "error");
        }
    };

    const handleFinish = () => {
      if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
        setPollingIntervalId(null);
      }
      setShowProgressModal(false);
  
      fetchDetails();
      fetchStatusText();
  };  

    const TOTAL_SEGMENTS = 10;
    const segmentsActive = Math.round((progress / 100) * TOTAL_SEGMENTS);
    const toggleActivate = async (scanIdx, actionIdx) => {
        const scanItem = scanResults[scanIdx];
        const action = scanItem.actions[actionIdx];
        const newActivate = !action.activate;

        setScanResult((prev) => {
            const updated = [...prev];
            updated[scanIdx] = {
                ...updated[scanIdx],
                actions: [...updated[scanIdx].actions],
            };
            updated[scanIdx].actions[actionIdx] = {
                ...action,
                activate: newActivate,
            };
            return updated;
        });

        try {
            const response = await fetch("http://35.213.150.144:8000/api/import-scanresult-action/update/", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    id: action.id,
                    import_scan_result_id: scanItem.import_scan_result_id,
                    activate: newActivate,
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to update toggle: ${response.status}`);
            }

            if (newActivate && jumpEnabled) {
                let highlightCol = scanItem.col;
                const colName = parseColumnName(scanItem.message);
                if (colName && headers && headers.length > 0) {
                    const indexInHeaders = headers.indexOf(colName);
                    if (indexInHeaders !== -1) {
                        highlightCol = indexInHeaders;
                    }
                }
                setPendingHighlight({ row: scanItem.row, col: highlightCol });

                const targetPage = Math.floor(scanItem.row / pageSize) + 1;

                if (targetPage !== page) {
                    setPage(targetPage);
                    setTimeout(() => {
                        fetchDetails();
                    }, 800);
                } else {
                    fetchDetails();
                }
                setActiveTab(0);
            }
        } catch (err) {
            Swal.fire("Error", err.message, "error");
            setScanResult((prev) => {
                const updated = [...prev];
                updated[scanIdx] = {
                    ...updated[scanIdx],
                    actions: [...updated[scanIdx].actions],
                };
                updated[scanIdx].actions[actionIdx] = {
                    ...action,
                    activate: action.activate,
                };
                return updated;
            });
        }
    };

    return (
        <div className="min-h-screen min-w-max dark:bg-slate-700 dark:text-cyan-400 relative">
            <Header />
            <div className="flex">
                <div className="flex-1 p-9 rounded-lg shadow-md">
                    <h1 className="text-xl font-bold mb-4">
                        File Details (ID: {id})
                    </h1>
                    {statusText && <p className="mb-4 text-xl font-bold">Status: {statusText}</p>}

                    {/* Tab Section */}
                    <div className="mt-6 border-b border-gray-300 dark:border-gray-700">
                        <ul className="flex space-x-0 border-b dark:border-gray-600">
                            {["Import Data", "Scan Results"].map((tab, index) => (
                                <li
                                    key={index}
                                    className={`p-3 px-3 cursor-pointer ${
                                        activeTab === index
                                            ? "border-b-2 border-blue-500 font-semibold bg-gray-100 dark:bg-gray-700"
                                            : "text-blue-500 hover:text-blue-700 transition-all duration-300"
                                    }`}
                                    onClick={() => setActiveTab(index)}
                                >
                                    {tab}
                                </li>
                            ))}
                        </ul>
                        <div className="p-6 rounded-lg shadow-md transition-opacity duration-300">
                            {/* --- Import Data Tab --- */}
                            {activeTab === 0 && (
                                <div>
                                    <div className="mb-4 flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <span>Page Size:</span>
                                            <input
                                                type="number"
                                                value={pageSize}
                                                onChange={(e) => {
                                                    const newSize = parseInt(e.target.value, 10);
                                                    if (!isNaN(newSize) && newSize > 0) {
                                                        const maxSize = details ? Math.min(newSize, details.count) : newSize;
                                                        setPageSize(maxSize);
                                                        setPage(1);
                                                        setInputPage("1");
                                                    }
                                                }}
                                                className="p-2 border rounded w-20 text-black"
                                                min="1"
                                                max={details?.count || 100}
                                            />
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            {/*Fully Automated Cleaning*/}
                                            <button
                                                onClick={handleFullyAutomatedCleaning}
                                                className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded"
                                            >
                                                Automatic Cleaning
                                            </button>
                                            <button
                                                onClick={handleClean}
                                                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded"
                                            >
                                                Clean
                                            </button>
                                            <button
                                                onClick={handleExport}
                                                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded"
                                            >
                                                Export
                                            </button>
                                        </div>
                                    </div>

                                    {/* File details content */}
                                    <div className=" dark:bg-[#253445] rounded-lg shadow p-4 dark:text-cyan-400">
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
                                                <h3 className="mt-3 mb-3 font-bold">Records:</h3>
                                                {details.results?.length > 0 ? (
                                                    <table className="min-w-full border-collapse">
                                                        <thead>
                                                            <tr>
                                                                {headers.map((header) => (
                                                                    <th
                                                                        key={header}
                                                                        className="px-4 py-2 bg-gray-200 dark:bg-[#2F3C4B] break-words text-left"
                                                                    >
                                                                        {header}
                                                                    </th>
                                                                ))}
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {details.results.map((record, rowIndex) => (
                                                                <tr
                                                                    key={record.id}
                                                                    className="border-b border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-[#253445] hover:bg-gray-300 dark:hover:bg-gray-600"
                                                                >
                                                                    {headers.map((header, colIndex) => {
                                                                        const isHighlight =
                                                                            highlightCell &&
                                                                            highlightCell.row === rowIndex &&
                                                                            highlightCell.col === colIndex;
                                                                        return (
                                                                            <td
                                                                                key={header}
                                                                                className={`px-4 py-2 break-words text-left max-w-[400px] ${
                                                                                    isHighlight ? "bg-yellow-200 border-2 border-red-500 animate-pulse" : ""
                                                                                }`}
                                                                            >
                                                                                {record.data[header] ?? "-"}
                                                                            </td>
                                                                        );
                                                                    })}
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
                                                        className="mb-1 px-4 py-2 bg-gray-700 text-white rounded"
                                                    >
                                                        Back
                                                    </button>
                                                </div>

                                                {/* Paging Controls */}
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
                                                                className={`px-3 py-1 rounded ${
                                                                    num === page
                                                                        ? "bg-blue-500 text-white"
                                                                        : "bg-gray-300 dark:bg-gray-700"
                                                                }`}
                                                                disabled={num === "..."}
                                                            >
                                                                {num}
                                                            </button>
                                                        ))}
                                                        <button
                                                            onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
                                                            disabled={page === totalPages}
                                                            className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded"
                                                        >
                                                            {">"}
                                                        </button>
                                                    </div>

                                                    <div className="flex items-center space-x-2 ml-auto">
                                                        <span className="dark:text-cyan-400">Jump to Page:</span>
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
                                                                const newPage = parseInt(inputPage, 10);
                                                                if (!isNaN(newPage) && newPage > 0 && newPage <= totalPages) {
                                                                    setPage(newPage);
                                                                }
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
                                </div>
                            )}

                            {activeTab === 1 && (
                                <div>
                                    <div className="flex items-center space-x-4 mb-2">
                                        <h2 className="text-lg font-bold">🔥 Scan Results</h2>
                                        <label className="inline-flex items-center cursor-pointer">
                                            <span className="mr-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                                                Enable Jump
                                            </span>
                                            <div className="relative">
                                                <input
                                                    type="checkbox"
                                                    checked={jumpEnabled}
                                                    onChange={() => setJumpEnabled(!jumpEnabled)}
                                                    className="peer sr-only"
                                                />
                                                <div className="w-11 h-6 bg-gray-200 border border-gray-400 rounded-full peer peer-checked:bg-blue-500 transition-colors"></div>
                                                <div className="absolute left-0 top-0 w-6 h-6 border border-gray-400 bg-white rounded-full shadow-md transform transition-transform peer-checked:translate-x-5"></div>
                                            </div>
                                        </label>
                                    </div>
                                    {loadingScan ? (
                                        <p>Loading scan results...</p>
                                    ) : errorScan ? (
                                        <p className="text-red-500 dark:text-gray-300">Error: {errorScan}</p>
                                    ) : scanResults.length > 0 ? (
                                        <div className="space-y-2">
                                            {scanResults.map((scan, idx) => (
                                                <details
                                                    key={idx}
                                                    open={!!expandedDetails[idx]}
                                                    onToggle={(e) => {
                                                        setExpandedDetails((prev) => ({
                                                            ...prev,
                                                            [idx]: e.target.open,
                                                        }));
                                                    }}
                                                    className=" rounded-lg p-3 bg-gray-200 dark:bg-[#253445]"
                                                >
                                                    <summary className="cursor-pointer font-semibold text-red-600 dark:text-red-400">
                                                        Problem detected: {scan.message}
                                                    </summary>

                                                    {scan.actions.length > 0 ? (
                                                        <div className="mt-2 text-gray-700 dark:text-cyan-400">
                                                            {scan.actions.map((action, actionIdx) => (
                                                                <ul key={actionIdx} className="my-4 space-y-3">
                                                                    <li className="rounded-lg dark:border-slate-700 bg-gray-50 dark:bg-slate-700 p-4 shadow-sm">
                                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm ">
                                                                            <div>
                                                                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                                                                    ID:
                                                                                </span>{" "}
                                                                                <span className="text-gray-800 dark:text-white">
                                                                                    {action.id}
                                                                                </span>
                                                                            </div>
                                                                            <div>
                                                                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                                                                    Title:
                                                                                </span>{" "}
                                                                                <span className="text-gray-800 dark:text-white">
                                                                                    {action.title}
                                                                                </span>
                                                                            </div>
                                                                            <div className="sm:col-span-2">
                                                                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                                                                    Description:
                                                                                </span>{" "}
                                                                                <span className="text-gray-800 dark:text-white">
                                                                                    {action.description}
                                                                                </span>
                                                                            </div>
                                                                            <div>
                                                                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                                                                    Cleaner:
                                                                                </span>{" "}
                                                                                <span className="text-blue-500">{action.cleaner}</span>
                                                                            </div>
                                                                            <div className="flex justify-between items-center sm:justify-start sm:gap-3">
                                                                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                                                                    Activate:
                                                                                </span>
                                                                                <span
                                                                                    onClick={() => toggleActivate(idx, actionIdx)}
                                                                                    className={`px-3 py-1 rounded-full text-sm font-semibold transition-colors duration-200 cursor-pointer shadow-sm border ${
                                                                                        action.activate
                                                                                            ? "bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-300"
                                                                                            : "bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-300"
                                                                                    }`}
                                                                                >
                                                                                    {action.activate ? "On" : "Off"}
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    </li>
                                                                </ul>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <p className="mt-2 text-gray-700 dark:text-gray-300">
                                                            No actions available.
                                                        </p>
                                                    )}
                                                </details>
                                            ))}
                                        </div>
                                    ) : (
                                        <p>No errors found.</p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            {/* Progress bar popup */}
            {showProgressModal && (
                <div className="fixed inset-0 flex items-center justify-center bg-opacity-50 backdrop-blur-sm z-50">
                    <div className="bg-yellow-50 border border-black rounded-lg px-8 py-6 shadow-md flex flex-col items-center">
                        <div className="bg-white rounded-lg px-6 py-4 w-[300px] flex flex-col items-center shadow-sm">
                            <div className="text-gray-700 font-medium mb-3 text-lg">
                                Processing...{progress.toFixed(0)}%
                            </div>
                            <div className="flex space-x-2">
                                {Array.from({ length: TOTAL_SEGMENTS }, (_, i) => {
                                    const isActive = i < segmentsActive;
                                    return (
                                        <span
                                            key={i}
                                            className={
                                                "h-4 w-4 rounded-full transition-colors duration-300 " +
                                                (isActive ? "bg-green-500" : "bg-gray-300")
                                            }
                                        />
                                    );
                                })}
                            </div>
                            <p className="text-sm mt-3 text-gray-600">
                                {progressStatus === "completed" || progress >= 100 ? "Completed" : "Processing..."}
                            </p>

                            <button
                                onClick={handleFinish}
                                disabled={progress < 100 && progressStatus !== "completed"}
                                className={`mt-4 px-4 py-2 rounded text-white ${
                                    progress >= 100 || progressStatus === "completed"
                                        ? "bg-blue-500 hover:bg-blue-600"
                                        : "bg-gray-400 cursor-not-allowed"
                                }`}
                            >
                                Completed
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}