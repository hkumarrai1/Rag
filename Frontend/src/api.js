import axios from "axios";

const BASE_URL = import.meta?.env?.VITE_BASE_URL;

const API = axios.create({
  baseURL: BASE_URL, // Backend URL (from VITE_BASE_URL, fallback to localhost)
});

export const uploadFiles = (formData) => API.post("/admin/upload", formData);
export const resetFiles = (formData) =>
  API.post("/admin/reset_upload", formData);
export const askQuestion = (question) =>
  API.get("/ask", { params: { question } });
