import React, {useState} from 'react'
// useState - create state variable that holds data retrieved from backend
// useEffect - fetches backend API on first render

function App() {

  const [selectedFile, setSelectedFile] = useState(null)

  // Get uploaded file
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  }

  const handleUpload = () => {
    if (!selectedFile){
      alert('No File Selected!')
      return;
    }
  

  const formData = new FormData() 
  formData.append('file', selectedFile) // Append formData object with file

  fetch('http://localhost:5001/upload', {
    method: 'POST',
    body: formData,
    mode: 'cors',
    })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP error! ${response.status}`);
          return response.json()
      })
      .then((data) => {
        alert('Upload Successful!')
        console.log('Server Response: ', data)
      })
      .catch(async (error) => {
        console.error('Upload Failed', error)
        alert('Upload Failed')
      })

  }

  return (
    <div>
      <h2>Upload a File</h2>

      {/* Take in uploaded file */}
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      
      <button onClick={handleUpload} style={{ marginLeft: '10px' }}>
        Upload
      </button>

      {selectedFile && (
        <div style={{ marginTop: '10px' }}>
          <strong>Selected file:</strong> {selectedFile.name}
        </div>
      )}
    </div>
  )
}

export default App