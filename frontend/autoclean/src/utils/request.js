//axios
import axios from 'axios'
import { getToken } from './token';

const request = axios.create({
    baseUrl: 'http://35.213.150.144:8000/api/doc#/token/token_create',
    timeout: 5000
})

//Request Interceptor
request.interceptors.request.use((config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
      return config;
    },
    error => {
      return Promise.reject(error);
    }
);

//Response Interceptor
request.interceptors.response.use(
  response => response,
  async error => {
      const originalRequest = error.config;
      if (error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const refreshToken = getRefreshToken();

          if (refreshToken) {
              try {
                  const res = await axios.post('http://35.213.150.144:8000/api/token/refresh', { refresh: refreshToken });
                  const newAccessToken = res.data.access;

                  setToken(newAccessToken, refreshToken);
                  originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                  return request(originalRequest);
              } catch (refreshError) {
                  console.error('Refresh token failed:', refreshError);
              }
          }
      }
      return Promise.reject(error);
    }
);
  
export {request}