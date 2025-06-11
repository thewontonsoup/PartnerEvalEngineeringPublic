import React, { useState } from "react";
import { Box, Typography, IconButton, CircularProgress } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete"; 
import { useNavigate } from 'react-router-dom';

export default function FileUploader({ uploadedFiles, onDeleteFile }) {
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();
  
  // Property and document abbreviations
  const propertyAbbreviations = {
    "multi-family": "MF",
    "commercial": "COM"
  };
  
  const documentAbbreviations = {
    "om": "OM",
    "rent-roll": "RR",
    "lease": "LS"
  };
  
  // triggered when the user clicks "start scanning" button
  const handleStartScanning = async () => {
    if (!uploadedFiles || uploadedFiles.length === 0) {
      console.warn("No files to upload");
      return;
    }

    // navigate to the loading screen and pass uploaded file metadata
    navigate("/loading", {
      state: {
        uploadedFiles,
      },
    });
  };
  
  return (
    <Box className="right-section">

      <Typography className="upload-status-title">File List</Typography>
      <Box className="file-list-container">
        {(!uploadedFiles || uploadedFiles.length === 0) ? (
          <Typography className="no-files-text">
            No Files Attached <br /> Waiting for Upload <br />📄⏳
          </Typography>
        ) : (
          uploadedFiles.map((file, index) => {
            const prop = propertyAbbreviations[file.propertyType || file.property_type] || "UNK";
            const doc = documentAbbreviations[file.documentType || file.doc_type] || "DOC";
            const fileName = file.name || (file.fileObject && file.fileObject.name) || `File ${index + 1}`;
            const filename = `${prop}_${doc}_${fileName}`;
            
            return (
              <Box key={index} className="file-item">
                <Box className="file-info">
                  📄
                  <Box className="file-details">
                    <Typography variant="body1" className="file-name">
                      {filename}
                    </Typography>
                  </Box>
                </Box>
                <IconButton onClick={() => onDeleteFile(index)} className="delete-button">
                  <DeleteIcon />
                </IconButton>
              </Box>
            );
          })
        )}
      </Box>
      
      {uploadedFiles && uploadedFiles.length > 0 && (
        <button  className="start-scanning-button" onClick={handleStartScanning} disabled={isUploading}>
          {isUploading ? (
            <>  
              {/* uses react fragment to avoid unnecessary HTML clutter */}
              <CircularProgress size={20} style={{ marginRight: '8px' }} color="inherit" />
              Scanning...
            </>
          ) : (
            "Start Scanning"
          )}
        </button>
      )}

    </Box>
  );
}
