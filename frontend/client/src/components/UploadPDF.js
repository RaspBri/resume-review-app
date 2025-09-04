import React from 'react';
import { Button, Typography, Box } from '@mui/material';

const UploadPDF = ({ file, setFile }) => {
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  return (
    <Box sx={{ my: 2 }}>
      <Button variant="contained" component="label">
        Upload Resume (PDF)
        <input hidden type="file" accept=".pdf" onChange={handleFileChange} />
      </Button>
      {file && (
        <Typography variant="body2" sx={{ mt: 1 }}>
          Selected: {file.name}
        </Typography>
      )}
    </Box>
  );
};

export default UploadPDF;