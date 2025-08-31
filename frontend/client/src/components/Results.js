import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

// TODO: Show matching keywords

const Results = ({ data }) => {
  const keywordMatch = data?.keyword_match ?? "Loading...";
  const resumeSentiment = data?.resume_to_job_similarity ?? "Loading...";
  const jobSimilarity = data?.similarity_score_note?? "Loading...";
  const missingKeywords = Array.isArray(data?.missing_keywords) ? data.missing_keywords.join(', ') : "Loading...";
  const upskillingAdvice = data?.upskilling_advice ?? "Loading...";

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" gutterBottom>Results</Typography>

      <Typography><strong>Keyword Match: %</strong>{keywordMatch}</Typography>
      <Typography><strong>Resume to Job Similarity: %</strong>{resumeSentiment}</Typography>
      <Typography><strong>Similarity Note:</strong> {jobSimilarity}</Typography>
      <Typography><strong>Missing Keywords:</strong> {missingKeywords}</Typography>

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1"><strong>Upskilling Advice:</strong></Typography>
        <Typography variant="body2">{upskillingAdvice}</Typography>
      </Box>
    </Paper>
  );
};


export default Results;