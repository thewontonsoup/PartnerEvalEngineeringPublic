import React, { useState } from "react";
import {
  Box,
  Button,
  Select,
  MenuItem,
  Typography,
  IconButton,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import "../styles/index.css";
import UploadIcon from "../images/Upload icon.png";

export default function UploadSection({ onFileUpload }) {
  // local state for selected files and dropdown selections
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [propertyType, setPropertyType] = useState("");
  const [documentType, setDocumentType] = useState("");

  // when files are selected, add them to local state
  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles((prevFiles) => [...prevFiles, ...files]);
  };

  // upload files to the parent component (via props)
  const handleUpload = () => {
    if (selectedFiles.length === 0 || !propertyType || !documentType) {
      alert("Please complete all fields.");
      return;
    }

    // for each file, send metada + actual file to parent state
    selectedFiles.forEach((file) => {
      onFileUpload({
        fileObject: file,
        name: file.name,
        propertyType,
        documentType,
        status: "uploading",
      });
    });

    // clear selected files after upload
    setSelectedFiles([]);
  };

  // remove a specific file by index
  const handleRemoveFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <Box className="left-section">
      <Box className="dropdown-container">
        <Box className="dropdown-box">
          <Typography fontWeight="bold" fontSize={20}>
            Property Type
          </Typography>
          <Select
            value={propertyType}
            onChange={(e) => setPropertyType(e.target.value)}
            className="dropdown"
          >
            <MenuItem value="multi-family">Multi-Family</MenuItem>
            <MenuItem value="commercial">Commercial</MenuItem>
          </Select>
        </Box>

        <Box className="dropdown-box">
          <Typography fontWeight="bold" fontSize={20}>
            Document Type
          </Typography>
          <Select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            className="dropdown"
          >
            <MenuItem value="om">OM</MenuItem>
            <MenuItem value="rent-roll">Rent Roll</MenuItem>
            <MenuItem value="lease">Lease</MenuItem>
            <MenuItem value="portfolio">Portfolio</MenuItem>
          </Select>
        </Box>
      </Box>

      {/* Upload Box */}
      <Box className="upload-box">
        <img src={UploadIcon} alt="Upload Icon" className="upload-icon" />
        <input
          type="file"
          onChange={handleFileChange}
          hidden
          id="file-upload"
          multiple
        />
        <label htmlFor="file-upload" className="upload-label">
          <u>Browse Files</u>
        </label>

        <Box className="selected-files-list">
          {selectedFiles.map((file, index) => (
            <Box key={index} className="file-list-row">
              <Typography className="file-name">{file.name}</Typography>
              <IconButton
                size="small"
                onClick={() => handleRemoveFile(index)}
                className="remove-btn"
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
        </Box>
      </Box>

      <Button
        variant="contained"
        className="upload-button"
        onClick={handleUpload}
      >
        Add Files ({selectedFiles.length})
      </Button>
    </Box>
  );
}
