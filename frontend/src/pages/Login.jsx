import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async e => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      await login(form.username, form.password)
      navigate('/')
    } catch {
      setError('Usuario o contraseña incorrectos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-title">🍴 RestaurantePRO</div>
        <div className="login-sub">Sistema de Gestión de Restaurante</div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handle}>
          <div className="form-group">
            <label>Usuario</label>
            <input className="form-control" autoFocus value={form.username}
              onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input className="form-control" type="password" value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />
          </div>
          <button className="btn btn-primary" style={{width:'100%',justifyContent:'center',marginTop:8}}
            disabled={loading}>{loading ? 'Ingresando...' : 'Ingresar'}</button>
        </form>
        <div style={{marginTop:16,fontSize:12,color:'#9ca3af',textAlign:'center'}}>
          admin/admin123 · mesero1/mesero123 · cocina1/cocina123 · cajero1/cajero123
        </div>
      </div>
    </div>
  )
}
