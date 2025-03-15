import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ProgressBar({ taskUuid }) {
  // If your API returns progress from 0 to 100, let’s store it in this state:
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  // Poll the server for real progress
  useEffect(() => {
    // Poll every 1 second
    const interval = setInterval(() => {
      fetchProgressFromServer(taskUuid);
    }, 1000);

    // Cleanup if component unmounts
    return () => clearInterval(interval);
  }, [taskUuid]);

  // This function calls your task-progress endpoint
  function fetchProgressFromServer(uuid) {
    const url = `http://35.213.150.144:8000/api/task-progress/${uuid}`;
    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // Suppose the API returns { progress: 75 } for 75%
        const serverProgress = data.progress; 
        setProgress(serverProgress);

        // If the task is finished, e.g. progress >= 100, navigate away
        if (serverProgress >= 100) {
          navigate("/info");
        }
      })
      .catch((err) => {
        console.error("Error fetching progress:", err);
        // Optionally handle errors if needed
      });
  }

  // Convert progress to how many “segments” you want to display.
  // E.g. you have a bar of 10 segments, so if the server’s at 75%,
  // that’s 7 or 8 segments.
  const TOTAL_SEGMENTS = 10;
  // We turn 0-100 into a fraction of TOTAL_SEGMENTS
  const segmentsActive = Math.round((progress / 100) * TOTAL_SEGMENTS);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      {/* Popup Box */}
      <div className="bg-yellow-50 border border-black rounded-lg px-8 py-6 shadow-md flex flex-col items-center">
        {/* Inner Box */}
        <div className="bg-white rounded-lg px-6 py-4 w-[400px] flex flex-col items-center shadow-sm">
          {/* Loading Text */}
          <div className="text-gray-700 font-medium mb-3 text-lg">
            Data Loading... {progress}%
          </div>

          {/* Progress Bar */}
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
        </div>
      </div>
    </div>
  );
}
