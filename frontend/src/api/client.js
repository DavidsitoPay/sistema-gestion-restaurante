import axios from 'axios'

// En producción usa VITE_API_URL, en desarrollo usa el proxy local de Vite
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
