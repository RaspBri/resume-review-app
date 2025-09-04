import React, { use, useState } from 'react';
import { Container, Typography, Button, Box, CircularProgress } from '@mui/material';
import UploadPDF from './components/UploadPDF';
import UploadJobDescription from './components/UploadJobDescription';
import Results from './components/Results';
import UploadJobTitle from './components/UploadJobTitle.js';
import OmitWords from './components/OmitWords.js'
import Alert from '@mui/material/Alert';
import CheckIcon from '@mui/icons-material/Check';
import './App.css'

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [omitWords, setOmitWords] = useState(' ')
  
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
    formData.append('omit_words', omitWords)
    const REACT_APP_URL = process.env.REACT_APP_URL || 'http://localhost:5001';

    try {
      const response = await fetch(`${REACT_APP_URL}/upload`, {
        method: 'POST',
        body: formData,
        mode: 'cors',
        credentials: "include"
      });

      const data = await response.json();

      if (!response.ok) {
        // Backend responded with error status
        console.error("Backend error:", data.error || data);
        alert("Error from server: " + (data.error || "Unknown error"));
        setResults(null);
      } else {
        // Success response
        console.log("API Response:", data);
        setResults(data);
      }
    } catch (error) {
        console.error("Error", error);
        alert("Error processing request.");
        setResults(null)
    } finally {
      setIsVisible(true);
      setLoading(false);

      setTimeout(() => {
        setIsVisible(false);
      }, 5000)
    }
  };

// TODO: Show in small window pdf file at the top

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <div className='top-color-band'/> 
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, zIndex: 1000}}>
        {
          isVisible && (
            <Alert icon={<CheckIcon fontSize="inherit" />} severity="success">
              Form submission successful.
            </Alert>
          )
        }
      </div>
      <br  />
      <Typography variant="h4" gutterBottom>Resume Analyzer</Typography>
      <Typography variant="h6" gutterBottom>This tool is designed to help job seekers optimize their resumes for specific job postings and ensure resume is ATS-Friendly.</Typography>
      <br  />
      <UploadJobTitle jobTitle={jobTitle} setJobTitle={setJobTitle}  />
      <UploadJobDescription jobDescription={jobDescription} setJobDescription={setJobDescription} />
      <OmitWords omitWords={omitWords} setOmitWords={setOmitWords}  />
      <UploadPDF file={file} setFile={setFile} />

      <Box sx={{ my: 2 }}>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Submit'}
        </Button>
      </Box>

      {results && <Results data={results} />}
    </Container>
  );
}

export default App;