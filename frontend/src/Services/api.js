import axios from "axios";

const normalizeBaseUrl = (url) => {
  if (!url) {
    return "http://127.0.0.1:8000/api/";
  }
  return url.endsWith("/") ? url : `${url}/`;
};

const baseURL = normalizeBaseUrl(process.env.REACT_APP_API_BASE_URL);

const API = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
    return Promise.reject(error);
  }
);

export default API;
