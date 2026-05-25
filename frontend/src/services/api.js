import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000,
});

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Upload failed. Please try again.";
    throw new Error(message);
  }
}

export async function createUploadUrl(filename) {
  try {
    const response = await api.post("/upload-url", { filename });
    return response.data;
  } catch (error) {
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Unable to create an upload URL.";
    throw new Error(message);
  }
}

export async function startProcessing(jobId, storagePath) {
  try {
    const response = await api.post("/process", {
      job_id: jobId,
      storage_path: storagePath,
    });
    return response.data;
  } catch (error) {
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Unable to start processing.";
    throw new Error(message);
  }
}

export async function uploadToSignedUrl(url, file) {
  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": file.type || "application/octet-stream",
    },
    body: file,
  });

  if (!response.ok) {
    throw new Error("Upload to storage failed.");
  }
}

export async function getProgress(jobId) {
  try {
    const response = await api.get(`/progress/${jobId}`);
    return response.data;
  } catch (error) {
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Unable to fetch progress.";
    throw new Error(message);
  }
}
