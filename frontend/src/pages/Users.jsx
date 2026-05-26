import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const ROLES = ['ADMIN','HOST','MESERO','COCINA','CAJERO']
const ROLE_COLORS = { ADMIN:'badge-red', HOST:'badge-blue', MESERO:'badge-yellow', COCINA:'badge-green', CAJERO:'badge-gray' }

export default function Users() {
  const [users, setUsers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ username:'', password:'', full_name:'', role:'MESERO' })
  const [msg, setMsg] = useState('')

  const load = useCallback(async () => {
    const { data } = await api.get('/users/')
    setUsers(data)
  }, [])

  useEffect(() => { load() }, [load])

  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  const createUser = async () => {
    try {
      await api.post('/users/', form)
      setShowModal(false); setForm({username:'',password:'',full_name:'',role:'MESERO'}); flash('✅ Usuario creado'); load()
    } catch(e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  const toggle = async user => {
    await api.put(`/users/${user.user_id}`, { active: !user.active })
    flash(user.active ? '⚠️ Usuario desactivado' : '✅ Usuario activado'); load()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title" style={{marginBottom:0}}>👥 Usuarios y Roles</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Nuevo Usuario</button>
      </div>
      {msg && <div className={`alert ${msg.startsWith('❌') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Nombre completo</th><th>Usuario</th><th>Rol</th><th>Estado</th><th>Acción</th></tr></thead>
            <tbody>
              {users.map(u => (
                <tr key={u.user_id}>
                  <td>{u.full_name}</td>
                  <td><code>{u.username}</code></td>
                  <td><span className={`badge ${ROLE_COLORS[u.role]}`}>{u.role}</span></td>
                  <td>{u.active
                    ? <span className="badge badge-green">Activo</span>
                    : <span className="badge badge-gray">Inactivo</span>}
                  </td>
                  <td>
                    <button className={`btn btn-sm ${u.active ? 'btn-danger' : 'btn-success'}`} onClick={() => toggle(u)}>
                      {u.active ? 'Desactivar' : 'Activar'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Nuevo Usuario</div>
            <div className="form-group">
              <label>Nombre completo</label>
              <input className="form-control" value={form.full_name} onChange={e => setForm(f => ({...f, full_name: e.target.value}))} />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input className="form-control" value={form.username} onChange={e => setForm(f => ({...f, username: e.target.value}))} />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <input type="password" className="form-control" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))} />
            </div>
            <div className="form-group">
              <label>Rol</label>
              <select className="form-control" value={form.role} onChange={e => setForm(f => ({...f, role: e.target.value}))}>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={createUser}
                disabled={!form.username || !form.password || !form.full_name}>Crear</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
