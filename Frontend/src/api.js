import axios from "axios";

const BASE_URL = import.meta?.env?.VITE_BASE_URL || "http://localhost:8000";

const API = axios.create({
  baseURL: BASE_URL, // Backend URL (from VITE_BASE_URL)
  timeout: 120000, // 2 minutes
  maxContentLength: Infinity,
  maxBodyLength: Infinity,
});

// Request logger
API.interceptors.request.use((cfg) => {
  try {
    console.debug(
      "API request:",
      (cfg.method || "").toUpperCase(),
      (cfg.baseURL || "") + (cfg.url || "")
    );
  } catch (e) {
    // ignore
  }
  return cfg;
});

// Response/error logger
API.interceptors.response.use(
  (res) => res,
  (err) => {
    try {
      console.error(
        "API error:",
        (err.config?.method || "").toUpperCase(),
        (err.config?.baseURL || "") + (err.config?.url || ""),
        "status:",
        err.response?.status,
        "body:",
        err.response?.data
      );
    } catch (e) {
      // ignore
    }
    return Promise.reject(err);
  }
);

export const uploadFiles = (formData, config = {}) =>
  API.post("/admin/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    ...config,
  });

export const resetFiles = (formData, config = {}) =>
  API.post("/admin/reset_upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    ...config,
  });

export const askQuestion = (question) =>
  API.get("/ask", { params: { question } });

export default API;
