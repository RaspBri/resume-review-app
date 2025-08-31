import React, { useState } from 'react';
import { Container, Typography, Button, Box, CircularProgress } from '@mui/material';
import UploadPDF from './components/UploadPDF';
import UploadJobDescription from './components/UploadJobDescription';
import Results from './components/Results';
import UploadJobTitle from './components/UploadJobTitle.js';

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const cleanText = (text) => {
    if (typeof text !== 'string') return '';
    return text
      .split('\n')                      
      .map(line => line.trim())          
      .filter(line => line.length > 0)  
      .join('\n');   
  }
    
  const handleSubmit = async () => {
    if (!file || !jobDescription || !jobTitle) {
      alert("Please upload a resume and enter job details.");
      return;
    }

    const cleanedJobDes = cleanText(jobDescription)

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', cleanedJobDes);
    formData.append('job_title', jobTitle)

    try {
      const response = await fetch('http://localhost:5001/upload', {
        method: 'POST',
        body: formData,
        mode: 'cors'
      });

      const data = await response.json();
      console.log("API Response:", data);
      setResults(data);
    } catch (error) {
        console.error("Error", error);
        alert("Error processing request.");
    } finally {
      setLoading(false);
    }
  };

// TODO: Show in small window pdf file at the top

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom>Resume Analyzer</Typography>

      <UploadPDF file={file} setFile={setFile} />
      <UploadJobTitle jobTitle={jobTitle} setJobTitle={setJobTitle}  />
      <UploadJobDescription jobDescription={jobDescription} setJobDescription={setJobDescription} />

      <Box sx={{ my: 2 }}>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Analyze'}
        </Button>
      </Box>

      {results && <Results data={results} />}
    </Container>
  );
}

export default App;
