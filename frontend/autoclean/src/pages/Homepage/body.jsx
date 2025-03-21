import React, { useRef, useEffect, useState } from "react";
import { getToken } from "../../utils";
import Dropzone from "dropzone";
import "dropzone/dist/dropzone.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";

export default function Body() {
  const navigate = useNavigate();
  const dropzoneRef = useRef(null);
  const [dropzoneInstance, setDropzoneInstance] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgresses, setUploadProgresses] = useState({});
  const [completedFileIds, setCompletedFileIds] = useState({});
  const [navigated, setNavigated] = useState(false);

  useEffect(() => {
    const dz = new Dropzone(dropzoneRef.current, {
      url: "/fake-upload-url",
      acceptedFiles: ".xlsx,.xls,.csv",
      maxFiles: 5,
      autoProcessQueue: false,
      dictDefaultMessage: "Drag and drop your Excel file here, or click to browse",
      previewTemplate: `
            <div class="dz-preview dz-file-preview relative p-2 flex flex-col items-center">
                <div
                    class="flex flex-col items-center justify-center bg-gray-200 rounded-lg shadow-md"
                    style="width: 120px; height: 120px; position: relative;"
                >
                    <div
                        class="dz-progress bg-black rounded-full flex items-center justify-center"
                        style="width: 40px; height: 20px; color: white;"
                        data-dz-uploadprogress
                    >
                        <span class="text-xs" data-dz-uploadprogress>%</span>
                    </div>

                    <!-- File Size Display -->
                    <div
                        class="text-sm font-bold text-black bg-white px-2 py-1 rounded mt-2"
                        style="min-width: 50px;"
                        data-dz-size
                    ></div>

                    <!-- Remove Button -->
                    <button
                        class="dz-remove"
                        title="Remove File"
                        style="
                            position: absolute;
                            top: 5px;
                            right: 5px;
                            background-color: #f56565;
                            color: white;
                            border: none;
                            border-radius: 50%;
                            width: 20px;
                            height: 20px;
                            font-size: 14px;
                            line-height: 1;
                            cursor: pointer;
                            z-index: 10;
                        "
                        data-dz-remove
                    >&times;</button>
                </div>

                <!-- File Name Display -->
                <div class="text-sm text-center mt-2" data-dz-name></div>
            </div>
        `,
      init: function () {
        this.on("addedfile", (file) => {
          setSelectedFiles((prevFiles) => [...prevFiles, file]);
          setTimeout(() => {
            const progressElements = document.querySelectorAll(".dz-progress");
            progressElements.forEach((el) => (el.style.display = "none"));
          }, 0);
        });

        this.on("removedfile", (file) => {
          setSelectedFiles((prevFiles) => prevFiles.filter((f) => f !== file));
        });

        this.on("error", (file, errorMessage) => {
          if (errorMessage === "Upload canceled.") {
            console.warn("⚠️ Ignoring Dropzone cancel error...");
            return;
          }
          alert("Upload failed!");
          console.error("Upload Error:", errorMessage);
        });
      },
    });

    setDropzoneInstance(dz);
    return () => dz.destroy();
  }, []);

  const handleConfirmUpload = async () => {
    if (selectedFiles.length === 0) {
      alert("Please add at least one file.");
      return;
    }
    setUploadProgresses({});
    setCompletedFileIds({});
    setNavigated(false);

    selectedFiles.forEach((file, index) => {
      uploadFile(file, index);
    });
  };

  const uploadFile = async (file, index) => {
    const formData = new FormData();
    formData.append("description", "none");
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://35.213.150.144:8000/api/upload/import",
        formData,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
            "Content-Type": "multipart/form-data",
            Accept: "application/json",
          },
        }
      );

      console.log("✅ Server Response:", response.data);

      const taskUUID = response.data.task_progress_uuid;
      const newFileId = response.data.id;

      if (taskUUID && newFileId) {
        checkProgress(taskUUID, newFileId, index);
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

  const checkProgress = async (uuid, fileId, index) => {
    try {
      const response = await axios.get(
        `http://35.213.150.144:8000/api/task-progress/${uuid}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
            Accept: "application/json",
          },
        }
      );

      console.log("📊 Progress Response for file", fileId, response.data);

      // Handle status from the response
      if (response.data.status === "error") {
        alert(`❌ File upload failed: ${response.data.error}`);
        console.error("❌ Upload error:", response.data.error);
        return; // Stop further processing
    }

    if (response.data.status === "pending") {
        console.log(`⏳ Processing file ${fileId}...`);
        setTimeout(() => checkProgress(uuid, fileId, index), 2000);
        return;
    }

      const serverProgress = parseFloat(response.data.percentage);
      if (!isNaN(serverProgress)) {
        setUploadProgresses((prev) => ({ ...prev, [index]: serverProgress }));
      } else {
        console.error("❌ Invalid progress value:", response.data.percentage);
      }

      if (serverProgress < 100) {
        setTimeout(() => checkProgress(uuid, fileId, index), 2000);
      } else {
        console.log(`✅ File ${fileId} upload complete.`);
        setCompletedFileIds((prev) => ({ ...prev, [index]: fileId }));
      }
    } catch (error) {
      console.error("❌ Progress check failed for file", fileId, error);
    }
  };

  useEffect(() => {
    if (
      !navigated &&
      selectedFiles.length > 0 &&
      Object.keys(completedFileIds).length === selectedFiles.length
    ) {
      setNavigated(true);

      const sortedKeys = Object.keys(completedFileIds)
        .map((k) => parseInt(k, 10))
        .sort((a, b) => a - b);

      const fileIdsArray = sortedKeys.map((k) => ({
        index: k,
        fileId: completedFileIds[k],
      }));

      const uploadedFilesInStorage = fileIdsArray.map((obj) => String(obj.fileId));
      localStorage.setItem("uploadedFiles", JSON.stringify(uploadedFilesInStorage));

      if (fileIdsArray.length === 1) {
        const onlyFileId = fileIdsArray[0].fileId;
        console.log("Only 1 file, auto-navigating to details of", onlyFileId);
        setTimeout(() => {
          navigate(`/info/${onlyFileId}`);
        }, 1000);
      } else {
        const fileOptions = {};
        fileIdsArray.forEach(({ index, fileId }) => {
          const fileName = selectedFiles[index].name;
          fileOptions[fileId] = fileName;
        });
  
        Swal.fire({
          title: "Multiple files have been uploaded",
          text: "Which file details do you want to see?",
          input: "select",
          inputOptions: fileOptions,
          inputPlaceholder: "Select a file",
          showCancelButton: true,
        }).then((result) => {
          if (result.isConfirmed && result.value) {
            navigate(`/info/${result.value}`);
          }
        });
      }
    }
  }, [completedFileIds, selectedFiles, navigated, navigate]);  

  return (
    <div className="flex flex-col items-center fit-h-screen space-y-8 mt-11 dark:text-cyan-400">
      <h1 className="text-center font-bold text-3xl">
        Upload File for Data Cleaning
      </h1>

      {/* Dropzone */}
      <div
        ref={dropzoneRef}
        className="dropzone w-[75%] h-50 border-2 border-dashed border-gray-400 rounded flex justify-center items-center text-gray-600 dark:border-gray-500 dark:text-cyan-400"
      ></div>

      {/* Multi-file progress bar */}
      {selectedFiles.length > 0 && (
        <div className="w-[75%] mt-4 space-y-4">
          {selectedFiles.map((file, index) => (
            <div key={index}>
              <p className="mb-1">{file.name}</p>
              <div className="w-full h-5 bg-gray-300 rounded relative">
                <div
                  className="h-full bg-green-500 rounded transition-all"
                  style={{ width: `${uploadProgresses[index] || 0}%` }}
                ></div>
                <span className="absolute inset-0 flex justify-center items-center text-sm font-bold text-black">
                  {uploadProgresses[index]
                    ? `${uploadProgresses[index]}%`
                    : "0%"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Handling Buttons */}
      <button
        onClick={handleConfirmUpload}
        className="bg-main hover:bg-mainHover text-white rounded-2xl font-bold py-4 px-[30%] mt-4"
      >
        Upload File
      </button>
    </div>
  );
}