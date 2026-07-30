// Intentionally left empty (placeholder for future split)
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

export async function uploadPDF(file: File) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await axios.post(
    "http://127.0.0.1:8000/api/upload-rag",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

