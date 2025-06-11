import { createContext, useState, useContext } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  
  const addFiles = (newFile) => {
    setUploadedFiles([...uploadedFiles, {
      ...newFile,
      type: newFile.type,
      doc_type: newFile.doc_type,
      property_type: newFile.property_type
    }]);
  };

  const removeFile = (fileName) => {
    setUploadedFiles(uploadedFiles.filter(file => file.name !== fileName));
  };
  
  const updateFileAttributes = (fileName, attributes) => {
    setUploadedFiles(uploadedFiles.map(file => 
      file.name === fileName ? { ...file, ...attributes } : file
    ));
  };

  const value = {
    uploadedFiles,
    addFiles,
    removeFile,
    updateFileAttributes,
  };

  return (
    <FileContext.Provider value={value}>
      {children}
    </FileContext.Provider>
  );
};

export const useFiles = () => useContext(FileContext);