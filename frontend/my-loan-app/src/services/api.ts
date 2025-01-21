// frontend/src/services/api.ts
import axios from 'axios';

const BASE_URL = "http://127.0.0.1:8000/api";

export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${BASE_URL}/pdf/process`, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  
  return response.data;
};
