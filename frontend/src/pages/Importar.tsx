import React, { useState } from 'react';
import axios from 'axios';
import { Spinner, Alert, Button } from 'react-bootstrap';

const Importar: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setPreviewData([]);
      setErrorMsg(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setErrorMsg(null);

    try {
      const response = await axios.post('/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setPreviewData(response.data);
    } catch (error) {
      console.error(error);
      setErrorMsg('Hubo un problema al cargar el archivo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <h2 className="text-2xl font-bold mb-4">Importar archivo</h2>

      <div className="mb-3">
        <input
          type="file"
          accept=".csv,.xlsx"
          className="form-control"
          onChange={handleFileChange}
        />
      </div>

      <Button
        variant="primary"
        onClick={handleUpload}
        disabled={!file || loading}
        className="mb-4"
      >
        {loading ? <Spinner size="sm" animation="border" /> : 'Subir archivo'}
      </Button>

      {errorMsg && (
        <Alert variant="danger" className="mt-3">
          {errorMsg}
        </Alert>
      )}

      {previewData.length > 0 && (
        <div className="overflow-auto mt-4">
          <h4 className="mb-2">Vista previa de los datos</h4>
          <table className="table table-bordered table-striped">
            <thead className="table-light">
              <tr>
                {Object.keys(previewData[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewData.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((val, i) => (
                    <td key={i}>{String(val)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Importar; 