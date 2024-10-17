import React, { useState } from 'react';
import { useMutation } from 'react-query';
import axios from 'axios';
import { Upload, FileText, Code, GitBranch } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [repoUrl, setRepoUrl] = useState('');

  const uploadMutation = useMutation((formData: FormData) => 
    axios.post(`${API_URL}/upload`, formData)
  );

  const generateCodeMutation = useMutation((prompt: string) => 
    axios.post(`${API_URL}/generate`, { prompt })
  );

  const addRepoMutation = useMutation((url: string) => 
    axios.post(`${API_URL}/add_repo`, { url })
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);
      await uploadMutation.mutateAsync(formData);
    }
  };

  const handleGenerateCode = async () => {
    if (input) {
      const result = await generateCodeMutation.mutateAsync(input);
      console.log(result.data);
    }
  };

  const handleAddRepo = async () => {
    if (repoUrl) {
      await addRepoMutation.mutateAsync(repoUrl);
      setRepoUrl('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-8">Ollama RAG App</h1>
      
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
        <input
          type="file"
          onChange={handleFileChange}
          className="mb-4"
        />
        <button
          onClick={handleUpload}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 flex items-center justify-center"
          disabled={!selectedFile || uploadMutation.isLoading}
        >
          <Upload className="mr-2" size={20} />
          {uploadMutation.isLoading ? 'Uploading...' : 'Upload'}
        </button>
        {uploadMutation.isSuccess && (
          <p className="text-green-600 mt-2">File uploaded successfully!</p>
        )}
      </div>

      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Add Git Repository</h2>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter Git repository URL"
          className="w-full p-2 border rounded mb-4"
        />
        <button
          onClick={handleAddRepo}
          className="w-full bg-purple-500 text-white py-2 px-4 rounded hover:bg-purple-600 flex items-center justify-center"
          disabled={!repoUrl || addRepoMutation.isLoading}
        >
          <GitBranch className="mr-2" size={20} />
          {addRepoMutation.isLoading ? 'Adding...' : 'Add Repository'}
        </button>
        {addRepoMutation.isSuccess && (
          <p className="text-green-600 mt-2">Repository added successfully!</p>
        )}
      </div>

      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Generate Code</h2>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your prompt here..."
          className="w-full h-32 p-2 border rounded mb-4"
        />
        <button
          onClick={handleGenerateCode}
          className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 flex items-center justify-center"
          disabled={!input || generateCodeMutation.isLoading}
        >
          <Code className="mr-2" size={20} />
          {generateCodeMutation.isLoading ? 'Generating...' : 'Generate Code'}
        </button>
        {generateCodeMutation.isSuccess && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Generated Code:</h3>
            <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
              {generateCodeMutation.data?.data.generated_code}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;