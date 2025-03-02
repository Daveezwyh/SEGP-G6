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
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState({});
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        const dz = new Dropzone(dropzoneRef.current, {
            url: "/fake-upload-url",
            acceptedFiles: ".xlsx,.xls,.csv",
            maxFiles: 5,
            autoProcessQueue: false,
            dictDefaultMessage: "Drag and drop up to 5 files here, or click to browse",
            init: function () {
                this.on("addedfile", (file) => {
                    setSelectedFiles((prevFiles) => [...prevFiles, file]);
                    setUploadProgress((prevProgress) => ({
                        ...prevProgress,
                        [file.name]: 0,
                    }));
                    
                    setTimeout(() => {
                        document.querySelectorAll(".dz-progress").forEach((el) => (el.style.display = "none"));
                    }, 0);
                });

                this.on("removedfile", (file) => {
                    setSelectedFiles((prevFiles) => prevFiles.filter(f => f !== file));
                    setUploadProgress((prevProgress) => {
                        const newProgress = { ...prevProgress };
                        delete newProgress[file.name];
                        return newProgress;
                    });
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

    const checkProgress = async (uuid, importId, fileName) => {
        try {
            const response = await axios.get(`http://35.213.150.144:8000/api/task-progress/${uuid}`, {
                headers: {
                    Authorization: `Bearer ${getToken()}`,
                    Accept: "application/json"
                }
            });

            const serverProgress = parseFloat(response.data.percentage);
            if (!isNaN(serverProgress)) {
                setUploadProgress((prevProgress) => ({
                    ...prevProgress,
                    [fileName]: serverProgress,
                }));
            }

            if (serverProgress >= 100) {
                completedFiles.current += 1;
            } else {
                setTimeout(() => checkProgress(uuid, importId, fileName, completedFiles), 2000);
                return;
            }
    
            if (completedFiles.current === selectedFiles.length) {
                setTimeout(() => {
                    navigate(`/info?importId=${importId}`);
                }, 1000);
            }

            setTimeout(() => checkProgress(uuid, importId, fileName), 2000);
        } catch (error) {
            console.error("❌ Progress check failed:", error);
        }
    };

    const handleConfirmUpload = async () => {
        if (selectedFiles.length === 0) {
            alert("Please add at least one file.");
            return;
        }
    
        setUploading(true);
        setUploadProgress({});
        
        let importIds = []; // Store all import IDs
        let completedUploads = 0;
        const totalFiles = selectedFiles.length;
    
        const uploadPromises = selectedFiles.map(async (file) => {
            const formData = new FormData();
            formData.append("description", file.name);
            formData.append("file", file);
    
            try {
                const response = await axios.post("http://35.213.150.144:8000/api/upload/import", formData, {
                    headers: {
                        Authorization: `Bearer ${getToken()}`,
                        "Content-Type": "multipart/form-data",
                        Accept: "application/json",
                    },
                    onUploadProgress: (progressEvent) => {
                        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress((prevProgress) => ({
                            ...prevProgress,
                            [file.name]: percentCompleted,
                        }));
                    },
                });
    
                if (response.data.id) {
                    importIds.push(response.data.id); 
                }
    
                const taskUUID = response.data.task_progress_uuid;
                if (taskUUID) {
                    await checkProgress(taskUUID, response.data.id, file.name);
                }
    
            } catch (error) {
                alert("Failed to upload file. Please try again.");
                console.error("Upload Error:", error);
            } finally {
                completedUploads++;
                if (completedUploads === totalFiles && importIds.length > 0) {
                    navigate(`/info?importIds=${importIds.join(",")}`);
                }
            }
        });
    
        await Promise.all(uploadPromises);
    };
    

    return (
        <div className="flex flex-col items-center fit-h-screen space-y-8 mt-11 dark:text-cyan-400">
            <h1 className="text-center font-bold text-3xl">Upload Files for Data Cleaning</h1>

            <div
                ref={dropzoneRef}
                className="dropzone w-[75%] h-50 border-2 border-dashed border-gray-400 rounded flex justify-center items-center text-gray-600 dark:border-gray-500 dark:text-cyan-400"
            ></div>

            {uploading && selectedFiles.map((file) => (
                <div key={file.name} className="w-[75%] h-5 bg-gray-300 rounded mt-4 relative">
                    <div
                        className="h-full bg-green-500 rounded transition-all" 
                        style={{ width: `${uploadProgress[file.name] || 0}%` }}
                    ></div>
                    <span className="absolute inset-0 flex justify-center items-center text-sm font-bold text-black">
                        {uploadProgress[file.name] || 0}%
                    </span>
                </div>
            ))}

            <button
                onClick={handleConfirmUpload}
                className="bg-main hover:bg-mainHover text-white rounded-2xl font-bold py-4 px-[30%] mt-4"
            >
                Process
            </button>
        </div>
    );
}
