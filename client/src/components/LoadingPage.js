import React, { useEffect, useState, useRef, useMemo} from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "../styles/loading.css";

export default function LoadingPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // extract uploaded files passed through route state 
  const uploadedFiles = useMemo(() => {
    return location.state?.uploadedFiles || [];
  }, [location.state?.uploadedFiles]);

  // total num of files for progress tracking 
  const totalFiles = uploadedFiles.length || 1;

  // used to 'visually' track how many files have been processed  
  const [currentFile, setCurrentFile] = useState(0);

  // prevent ui from rendering
  const [initialized, setInitialized] = useState(false); 


  //To track uploading to live across Strictmode
  const hasUploaded = useRef(false);

  // handles file upload when component is mounted 
  useEffect(() => {
    
    if (hasUploaded.current) return;
    hasUploaded.current = true;

    if (!location.state?.uploadedFiles) {
      setInitialized(true); // still initialize to prevent loading state 
      return;
    }

    setInitialized(true);  //begin processing and show loading UI 

    const sendToBackend = async () => {
      const formData = new FormData();


      // append each file and its metadad to the formData
      uploadedFiles.forEach((fileData) => {
        const file = fileData.fileObject || fileData;
        formData.append("file", file);
        formData.append("doc_types", fileData.documentType || fileData.doc_type || '');
        formData.append("property_types", fileData.propertyType || fileData.property_type || '');
      });

      try {
        // send data to backend
        const response = await fetch("http://127.0.0.1:5000/upload", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        // navigate to final page with uploaded result and original metadata
        setTimeout(() => {
          navigate("/final", {
            state: {
              uploadedData: Array.isArray(data) ? data : [data],
              originalMeta: uploadedFiles,
            },
          });
        }, 1000); // wait 1 sec after upload for smoother transition
      } catch (error) {
        console.error("Upload failed:", error);
        alert("Upload failed. Check console for details.");
      }
    };

    sendToBackend();
  }, [location.state, uploadedFiles, navigate]);

  // Animate loading bar
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFile((prev) => {
        if (prev >= totalFiles) {
          clearInterval(interval);
          return totalFiles;
        }
        return prev + 1;
      });
    }, 7000); // 7 sec per file

    return () => clearInterval(interval);
  }, [totalFiles]);

  const progress = (currentFile / totalFiles) * 100;

  if (!initialized) return null;

  // if no file data was passed
  if (!location.state?.uploadedFiles) {
    return (
      <div className="loading-wrapper">
        <div className="center-content">
          <p style={{ textAlign: "center", marginTop: "40px" }}>
            You accessed this page without uploading any files.<br />
            Please return to the homepage and try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="loading-wrapper">
      <div className="center-content">
        <div className="loading-box">
          <p className="loading-text">
            Extracting Files ({currentFile}/{totalFiles})...
          </p>
          <div className="progress-bar-background">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      <footer className="footer-bar">© 2025</footer>
    </div>
  );
}
