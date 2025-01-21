// src/services/api.ts
import axios from "axios";

// Base URL for your backend API (adjust if necessary)
const BASE_URL = "http://127.0.0.1:8000";

export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await axios.post(`${BASE_URL}/process-pdf`, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
