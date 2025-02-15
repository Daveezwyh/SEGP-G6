import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import for navigation

export default function ProgressBar() {
  const TOTAL_SEGMENTS = 10; // Number of progress steps
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate(); // Initialize navigation

  useEffect(() => {
    // Increment progress every 500ms
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev < TOTAL_SEGMENTS) {
          return prev + 1;
        } else {
          clearInterval(interval); // Stop progress animation
          return prev;
        }
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Once progress reaches TOTAL_SEGMENTS, navigate back to homepage
    if (progress === TOTAL_SEGMENTS) {
      setTimeout(() => {
        navigate("/homepage");
      }, 1000);
    }
  }, [progress, navigate]); // Runs when progress updates

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      {/* Popup Box */}
      <div className="bg-yellow-50 border border-black rounded-lg px-8 py-6 shadow-md flex flex-col items-center">
        
        {/* Inner Box*/}
        <div className="bg-white rounded-lg px-6 py-4 w-[400px] flex flex-col items-center shadow-sm">
          {/* Loading Text */}
          <div className="text-gray-700 font-medium mb-3 text-lg">
            Data Loading...
          </div>

          {/* Progress Bar */}
          <div className="flex space-x-2">
            {Array.from({ length: TOTAL_SEGMENTS }, (_, i) => {
              const isActive = i < progress;
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
