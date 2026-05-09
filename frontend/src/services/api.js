const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

const getHeaders = (token) => ({
  "Content-Type": "application/json",
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
});

const parseResponse = async (response) => {
  const text = await response.text();
  if (!text) return {};
  try {
    const data = JSON.parse(text);
    if (!response.ok) {
      throw {
        message: data.detail || data.error || "Request failed",
        status: response.status,
        data,
      };
    }
    return data;
  } catch (e) {
    if (e.message) throw e;
    throw { message: "Invalid server response", status: response.status };
  }
};

export const authApi = {
  signup: (email, password) =>
    fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    }).then(parseResponse),

  login: (email, password) =>
    fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    }).then(parseResponse),

  logout: (token) =>
    fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      headers: getHeaders(token),
    }).then(parseResponse),
};

export const paperApi = {
  list: (token) =>
    fetch(`${API_BASE_URL}/papers`, {
      headers: getHeaders(token),
    }).then(parseResponse),

  upload: (token, files) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return fetch(`${API_BASE_URL}/ingest`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }, // FormData sets its own Content-Type
      body: formData,
    }).then(parseResponse);
  },

  get: (token, id) =>
    fetch(`${API_BASE_URL}/papers/${id}`, {
      headers: getHeaders(token),
    }).then(parseResponse),

  analyze: (token, id) =>
    fetch(`${API_BASE_URL}/papers/${id}/analyze`, {
      method: "POST",
      headers: getHeaders(token),
    }).then(parseResponse),
    
  compare: (token, paperIds) =>
    fetch(`${API_BASE_URL}/compare`, {
        method: "POST",
        headers: getHeaders(token),
        body: JSON.stringify({ paper_ids: paperIds }),
    }).then(parseResponse),
};

export const analysisApi = {
  getComprehensive: (token) =>
    fetch(`${API_BASE_URL}/analysis/comprehensive`, {
      headers: getHeaders(token),
    }).then(parseResponse),
    
  getDashboard: (token) =>
    fetch(`${API_BASE_URL}/analysis/dashboard`, {
        headers: getHeaders(token),
    }).then(parseResponse),
};
