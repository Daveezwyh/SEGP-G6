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
    response => {
      console.log('Response Received:', response);
      return response;
    },
    error => {
      if (error.response.status === 401) {
        console.error('Unauthorized, redirecting to login...');
      } else if (error.response.status === 500) {
        console.error('Server Error');
      }
      return Promise.reject(error);
    }
);
  
export {request}