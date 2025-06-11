import React, { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../styles/final.css";
import DownloadIcon from "@mui/icons-material/Download";
import EditIcon from "@mui/icons-material/Edit";

export default function Final() {
  const location = useLocation();

  const parsedResults = location.state?.uploadedData || [];
  const fileMeta = location.state?.originalMeta || [];

  // Initialize state for UI controls and edited data
  const [editingStates, setEditingStates] = useState(
    parsedResults.map(() => ({
      isEditing: false,
      showAllFields: false
    }))
  );

  // Store the actual data separate from the UI state
  const [jsonData, setJsonData] = useState(
    parsedResults.map(result => result.draft_json || result)
  );
  
  // Store the edit state to avoid re-renders during typing
  const editBuffers = useRef(
    parsedResults.map(result => ({ ...result.draft_json || result }))
  );

  const propertyAbbreviations = {
    "multi-family": "MF",
    commercial: "Com",
  };

  const documentAbbreviations = {
    om: "OM",
    "rent-roll": "RR",
    lease: "Lease",
  };

  const formatFileName = (meta) => {
    const prop = propertyAbbreviations[meta.propertyType] || "UNK";
    const doc = documentAbbreviations[meta.documentType] || "DOC";
    const baseName = meta.name.replace(/\.[^/.]+$/, "");
    return `${prop}_${doc}_${baseName}.json`;
  };

  const handleDownload = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadAll = () => {
    jsonData.forEach((data, i) => {
      const filename = formatFileName(fileMeta[i]);
      handleDownload(data, filename);
    });
  };

  const toggleEdit = (index) => {
    // When opening editor, copy current data to edit buffer
    if (!editingStates[index].isEditing) {
      editBuffers.current[index] = { ...jsonData[index] };
    }
    
    setEditingStates(prev => {
      const newStates = [...prev];
      newStates[index] = {
        ...newStates[index],
        isEditing: !newStates[index].isEditing
      };
      return newStates;
    });
  };

  const toggleShowAll = (index) => {
    setEditingStates(prev => {
      const newStates = [...prev];
      newStates[index] = {
        ...newStates[index],
        showAllFields: !newStates[index].showAllFields
      };
      return newStates;
    });
  };

  const handleFieldChange = (index, key, newValue) => {
    // Update buffer instead of state to avoid re-renders
    editBuffers.current[index] = {
      ...editBuffers.current[index],
      [key]: newValue
    };
  };

  const handleSaveEdit = (index) => {
    // Update the actual data state with the buffer content
    setJsonData(prev => {
      const newData = [...prev];
      newData[index] = { ...editBuffers.current[index] };
      return newData;
    });
    
    // Close the edit panel
    setEditingStates(prev => {
      const newStates = [...prev];
      newStates[index] = {
        ...newStates[index],
        isEditing: false
      };
      return newStates;
    });
  };

  const JsonTableView = ({ data, index }) => {
    const { showAllFields } = editingStates[index];
    const tableRef = useRef(null);
    const [scrollPosition, setScrollPosition] = useState(0);

    // Use effect to maintain scroll position
    useEffect(() => {
      if (tableRef.current && scrollPosition > 0) {
        tableRef.current.scrollTop = scrollPosition;
      }
    }, [showAllFields, scrollPosition]);

    // Save scroll position when scrolling
    const handleScroll = (e) => {
      setScrollPosition(e.target.scrollTop);
    };

    // Use the buffer for rendering to avoid re-renders during typing
    const editBuffer = editBuffers.current[index];
    
    const entries = Object.entries(editBuffer).filter(
      ([, value]) => showAllFields || (value !== null && value !== "")
    );

return (
  <div className="json-table-container">
    {/* Buttons container outside the scrollable area */}
    <div className="json-table-buttons">
      <button 
        className="toggle-btn" 
        onClick={() => toggleShowAll(index)}
      >
        {showAllFields ? "Hide Empty Fields" : "Show All Fields"}
      </button>
    </div>
    
    {/* Scrollable table area */}
    <div 
      className="json-table-wrapper" 
      ref={tableRef}
      onScroll={handleScroll}
    >
      <table className="json-table">
        <thead>
          <tr>
            <th>Field</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([key, value]) => (
            <tr key={key}>
              <td className="json-key">{key}</td>
              <td className="json-value">
                <input
                  type="text"
                  defaultValue={value ?? ""}
                  onChange={(e) => handleFieldChange(index, key, e.target.value)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    
    {/* Optional bottom button container */}
    <div className="json-table-buttons bottom">
      <button
        className="save-edit-btn"
        onClick={() => handleSaveEdit(index)}
      >
        Save & Close
      </button>
    </div>
  </div>
);
  };

  return (
    <div className="final-wrapper">
      <main className="final-content">
        <div className="file-table">
          <div className="table-header">
            <span>File Name</span>
            <span>Download</span>
            <span>Edit</span>
          </div>

          {jsonData.map((data, index) => {
            const meta = fileMeta[index] || {};
            const formattedName = formatFileName(meta);
            const isEditing = editingStates[index].isEditing;

            return (
              <div key={index} className="table-row-group">
                <div className="table-row">
                  <span className="file-name">{formattedName}</span>
                  <span className="icon-cell">
                    <DownloadIcon
                      className="icon"
                      onClick={() => handleDownload(data, formattedName)}
                    />
                  </span>
                  <span className="icon-cell">
                    <EditIcon
                      className="icon"
                      onClick={() => toggleEdit(index)}
                    />
                  </span>
                </div>

                {isEditing && (
                  <JsonTableView 
                    data={data} 
                    index={index} 
                  />
                )}
              </div>
            );
          })}
        </div>

        <button className="download-all-btn" onClick={handleDownloadAll}>
          Download All <DownloadIcon />
        </button>
      </main>

      <footer className="footer-bar">© 2025</footer>
    </div>
  );
}