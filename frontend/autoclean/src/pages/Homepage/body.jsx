import React from 'react';

export default function Body() {
    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            alert(`File uploaded: ${file.name}`);
        }
    };

    return (
        <div className="flex flex-col  items-center fit-h-screen space-y-8 mt-11">
            <h1 className="text-center font-bold text-3xl">Upload File for Data Cleaning</h1>
            <button 
                onClick={() => document.getElementById('excelUpload').click()} 
                className="bg-red-500 hover:bg-red-700 text-white rounded font-bold py-4 px-20"
            >
                Upload Excel File
            </button>
            <input 
                type="file" 
                id="excelUpload" 
                accept=".xlsx, .xls" 
                className="hidden" 
                onChange={handleFileUpload} 
            />
        </div>
    );
}
