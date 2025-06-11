import React, { useState } from "react";
import UploadSection from "./components/UploadSection"; // left side
import FileUploader from "./components/FileList"; // right side
import LoadingPage from "./components/LoadingPage";
import Final from "./components/Final"; // displays parsed JSON with edit and download options
import "./styles/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
export default function App() {
  // local state to store all uploaded files and their metadata
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // callback to add a new uploaded file to the state
  const handleFileUpload = (fileData) => {
    setUploadedFiles((prevFiles) => [...prevFiles, fileData]);
  };

  // callback to remove a file by index
  const handleDeleteFile = (index) => {
    setUploadedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  return (
    <BrowserRouter>
      <NavBar></NavBar>
      <Routes>
        <Route
          path="/"
          element={
            <div className="page-container">
              <UploadSection onFileUpload={handleFileUpload} />
              <FileUploader
                uploadedFiles={uploadedFiles}
                onDeleteFile={handleDeleteFile}
              />
            </div>
          }
        />
        <Route path="/loading" element={<LoadingPage />} />
        <Route path="/final" element={<Final />} />
      </Routes>
    </BrowserRouter>
  );
}
