import React from 'react';
import { TextField, Box } from '@mui/material';

const UploadJob = ({ jobDescription, setJobDescription }) => {
  return (
    <Box sx={{ my: 2 }}>
      <TextField
        label="Paste Job Description"
        multiline
        fullWidth
        rows={6}
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        variant="outlined"
        slotProps={{ htmlInput: { maxLength: 1000 } }}
      />
    </Box>
  );
};

export default UploadJob;