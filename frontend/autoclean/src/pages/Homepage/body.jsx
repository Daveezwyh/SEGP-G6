import Dropzone from "dropzone";
import "dropzone/dist/dropzone.css";
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Body() {
    const dropzoneRef = useRef(null);  
    const [fileAdded, setFileAdded] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const dropzone = new Dropzone(dropzoneRef.current, {
            url: "/upload",
            acceptedFiles: ".xlsx, .xls .csv",
            maxFiles: 1,
            autoProcessQueue: false, 
            dictDefaultMessage: "Drag and drop your Excel file here, or click to browse",
            init: function () {
                this.on("addedfile", (file) => {
                    setFileAdded(true); // Set fileAdded to true when a file is added
                    alert(`File added: ${file.name}`);
                });
            }
        });

        return () => dropzone.destroy(); 
    }, []);

    const handleConfirmUpload = () => {
        const dropzone = dropzoneRef.current.dropzone;
        if (fileAdded) {
            dropzone.processQueue();
            navigate("/progressbar");
        } else {
            alert("Please add a file first.");
        }
    };

    return (
        <div className="flex flex-col items-center fit-h-screen space-y-8 mt-11 dark:text-cyan-400">
            <h1 className="text-center font-bold text-3xl">Upload File for Data Cleaning</h1>
            
            {/* Dropzone Container */}
            <div
                ref={dropzoneRef} 
                className="dropzone w-[75%] h-50 border-2 border-dashed border-gray-400 rounded 
                           flex justify-center items-center text-gray-600 
                           dark:border-gray-500 dark:text-cyan-400"
            >
            </div>

            {/* Process Button */}
            <button
                onClick={handleConfirmUpload}
                className="bg-main hover:bg-mainHover text-white rounded-2xl font-bold py-4 px-[30%] mt-4"
            >
                Process
            </button> 
        </div>
    );
}
