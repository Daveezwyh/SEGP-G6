import React, { useRef, useEffect, useState } from "react";
import { getToken } from "../../utils";
import Dropzone from "dropzone";
import "dropzone/dist/dropzone.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Body() {
    const navigate = useNavigate();
    const dropzoneRef = useRef(null);
    const [dropzoneInstance, setDropzoneInstance] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(null);
    const [taskUUID, setTaskUUID] = useState(null);

    useEffect(() => {
        const dz = new Dropzone(dropzoneRef.current, {
            url: "/fake-upload-url",
            acceptedFiles: ".xlsx,.xls,.csv",
            maxFiles: 1,
            autoProcessQueue: false,
            dictDefaultMessage: "Drag and drop your Excel file here, or click to browse",
            init: function () {
                this.on("addedfile", (file) => {
                    setSelectedFile(file);
                    setTimeout(() => {
                        const progressElements = document.querySelectorAll(".dz-progress");
                        progressElements.forEach((el) => (el.style.display = "none"));
                    }, 0);
                });
    
                this.on("error", (file, errorMessage) => {
                    if (errorMessage === "Upload canceled.") {
                        console.warn("⚠️ Ignoring Dropzone cancel error...");
                        return;
                    }
    
                    alert("Upload failed!");
                    console.error("Upload Error:", errorMessage);
                });
            }
        });
    
        setDropzoneInstance(dz);
        return () => dz.destroy();
    }, []);    

    const handleConfirmUpload = async () => {
        if (!selectedFile) {
            alert("Please add a file first.");
            return;
        }
    
        setUploadProgress(0);
        setTaskUUID(null);
    
        const formData = new FormData();
        formData.append("description", "none");
        formData.append("file", selectedFile);
    
        try {
            const response = await axios.post("http://35.213.150.144:8000/api/upload/import", formData, {
                headers: {
                    Authorization: `Bearer ${getToken()}`,
                    "Content-Type": "multipart/form-data",
                    Accept: "application/json"
                }
            });
    
            console.log("✅ Server Response:", response.data);
    
            const taskUUID = response.data.task_progress_uuid;
    
            if (taskUUID) {
                setTaskUUID(taskUUID);
                checkProgress(taskUUID);
            } else {
                alert("❌ Upload successful, but the backend did not return a task ID!");
                console.error("❌ Server response:", response.data);
            }
        } catch (error) {
            if (error.response?.status === 401) {
                alert("Unauthorized, please login again.");
                console.error("Unauthorized error", error.response.data);
            } else {
                alert("Failed to upload file. Please try again.");
                console.error("Upload Error:", error);
            }
        }
    };
    
    const checkProgress = async (uuid) => {
        try {
            const response = await axios.get(`http://35.213.150.144:8000/api/task-progress/${uuid}`, {
                headers: {
                    Authorization: `Bearer ${getToken()}`,
                    Accept: "application/json"
                }
            });
    
            console.log("📊 Progress Response:", response.data);
    
            const serverProgress = parseFloat(response.data.percentage);
            if (!isNaN(serverProgress)) {
                setUploadProgress(serverProgress);
            } else {
                console.error("❌ Invalid progress value:", response.data.percentage);
            }
    
            if (serverProgress >= 100) {
                console.log("✅ Upload complete, waiting 1s before navigating...");
                setTimeout(() => {
                    navigate(`/info`);  // 这里移除了 importId
                }, 1000);
                return;
            }
    
            setTimeout(() => checkProgress(uuid), 2000);
        } catch (error) {
            console.error("❌ Progress check failed:", error);
        }
    };    

    return (
        <div className="flex flex-col items-center fit-h-screen space-y-8 mt-11 dark:text-cyan-400">
            <h1 className="text-center font-bold text-3xl">Upload File for Data Cleaning</h1>

            <div
                ref={dropzoneRef}
                className="dropzone w-[75%] h-50 border-2 border-dashed border-gray-400 rounded flex justify-center items-center text-gray-600 dark:border-gray-500 dark:text-cyan-400"
            ></div>

            {/* Progress Bar */}
            {uploadProgress !== null && (
                <div className="w-[75%] h-5 bg-gray-300 rounded mt-4 relative">
                    <div
                        className="h-full bg-green-500 rounded transition-all"
                        style={{ width: `${uploadProgress}%` }}
                    ></div>
                    <span className="absolute inset-0 flex justify-center items-center text-sm font-bold text-black">
                        {uploadProgress}%
                    </span>
                </div>
            )}

            <button
                onClick={handleConfirmUpload}
                className="bg-main hover:bg-mainHover text-white rounded-2xl font-bold py-4 px-[30%] mt-4"
            >
                Process
            </button>
        </div>
    );
}
