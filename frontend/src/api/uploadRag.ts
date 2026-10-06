// Intentionally left empty (placeholder for future split)
import axios from "axios";
import { BACKEND_URL } from "./client";

const API_URL = `${BACKEND_URL}/api`;

export async function uploadPDF(file: File) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await axios.post(
    `${API_URL}/upload-rag`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}
