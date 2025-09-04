import React from 'react';
import { TextField, Box } from '@mui/material';

const UploadJob = ({ omitWords, setOmitWords }) => {
  return (
    <Box sx={{ my: 2 }}>
      <TextField
        label="Words To Omit (Ex. learning, understanding, field)"
        multiline
        fullWidth
        rows={3}
        value={omitWords}
        onChange={(e) => setOmitWords(e.target.value)}
        variant="outlined"
        slotProps={{ htmlInput: { maxLength: 500} }}
      />
    </Box>
  );
};

export default UploadJob;