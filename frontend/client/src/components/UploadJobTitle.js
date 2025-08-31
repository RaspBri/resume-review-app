import React from 'react';
import { TextField, Box } from '@mui/material';

const UploadJobTitle = ({ jobTitle, setJobTitle }) => {
  return (
    <Box sx={{ my: 1 }}>
      <TextField
        label="Paste Job Title"
        multiline = {false}
        fullWidth
        rows={1}
        value={jobTitle}
        onChange={(e) => setJobTitle(e.target.value)}
        variant="outlined"
        slotProps={{ htmlInput: { maxLength: 50 } }}
      />
    </Box>
  );
};

export default UploadJobTitle;