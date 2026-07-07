import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes — Gemini + embedding can be slow on first call
});

/**
 * Analyse a resume PDF against a job description.
 *
 * @param {File} resumeFile - The PDF file object from the file input
 * @param {string} jdText - The raw job description text
 * @returns {Promise<AnalyzeResponse>} The full analysis response
 */
export async function analyzeResume(resumeFile, jdText) {
  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("jd_text", jdText);

  const response = await apiClient.post("/api/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export default apiClient;
