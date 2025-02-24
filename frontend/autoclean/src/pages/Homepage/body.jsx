import React, { useRef, useEffect, useState } from 'react';
import { getToken } from '../../utils'
import Dropzone from "dropzone";
import "dropzone/dist/dropzone.css";
import axios from "axios";

export default function Body() {
    const dropzoneRef = useRef(null);  
    const [fileAdded, setFileAdded] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);

    useEffect(() => {
        const dropzone = new Dropzone(dropzoneRef.current, {
            url: "/upload",
            acceptedFiles: ".xlsx,.xls,.csv",
            maxFiles: 1,
            autoProcessQueue: false, 
            dictDefaultMessage: "Drag and drop your Excel file here, or click to browse",
            init: function () {
                this.on("addedfile", (file) => {
                    setFileAdded(true); 
                    setSelectedFile(file);
                });
            
                this.on("error", (file, errorMessage) => {
                    alert("Upload failed!");
                    console.error("Upload Error:",errorMessage)
                });
            }
        });

        return () => dropzone.destroy(); 
    }, []);

    const handleConfirmUpload = async () => {
        if (!fileAdded || !selectedFile){
            alert("Please add a file first.");
            return;
        }

        const description = "none";
        const formData = new FormData();
        formData.append("description", description);
        formData.append("file", selectedFile);

        try{
            const response = await axios.post("http://35.213.150.144:8000/api/upload/import", formData, {
                headers: {
                    'Authorization': `Bearer ${getToken()}`,
                    'Content-Type': 'multipart/form-data',
                    'Accept': 'application/json',
                }
            });
            alert("File uploaded successfully!");
            console.log("Server Response",response.data);
        } catch (error){
            if(error.response?.status == 401 ){
                alert("Unauthorized, please login again.");
                console.error("unauthorized error", error.response.data)
            }
            alert("Failed to upload file. Please try again.");
            console.error("Upload Error:", error);
        }
    };

    return (
        <div className="flex flex-col items-center fit-h-screen space-y-8 mt-11 dark:text-cyan-400">
            <h1 className="text-center font-bold text-3xl">Upload File for Data Cleaning</h1>

            <div
                ref={dropzoneRef} 
                className="dropzone w-[75%] h-50 border-2 border-dashed border-gray-400 rounded flex justify-center items-center text-gray-600 dark:border-gray-500 dark:text-cyan-400"
            >
            </div>

            <button onClick={handleConfirmUpload} className="bg-main hover:bg-mainHover text-white rounded-2xl font-bold py-4 px-[30%] mt-4" >
                Process
            </button> 
        </div>
    );
}