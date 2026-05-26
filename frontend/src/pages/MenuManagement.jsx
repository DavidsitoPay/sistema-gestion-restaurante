import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

export default function MenuManagement() {
  const [categories, setCategories] = useState([])
  const [items, setItems] = useState([])
  const [tab, setTab] = useState('items')
  const [msg, setMsg] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', price: '', category_id: '' })
  const [catForm, setCatForm] = useState('')

  const load = useCallback(async () => {
    const [c, i] = await Promise.all([
      api.get('/menu/categories').then(r => r.data),
      api.get('/menu/items').then(r => r.data)
    ])
    setCategories(c); setItems(i)
  }, [])

  useEffect(() => { load() }, [load])

  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  const createItem = async () => {
    try {
      await api.post('/menu/items', { ...form, price: Number(form.price), category_id: Number(form.category_id) })
      setShowModal(false); setForm({ name:'',description:'',price:'',category_id:'' }); flash('✅ Producto creado'); load()
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  const toggleStock = async item => {
    await api.put(`/menu/items/${item.item_id}`, { out_of_stock: !item.out_of_stock })
    flash(item.out_of_stock ? '✅ Disponible' : '⚠️ Marcado agotado'); load()
  }

  const deleteItem = async id => {
    if (!confirm('¿Eliminar producto?')) return
    await api.delete(`/menu/items/${id}`); flash('✅ Eliminado'); load()
  }

  const createCat = async () => {
    if (!catForm.trim()) return
    try {
      await api.post('/menu/categories', { name: catForm }); setCatForm(''); flash('✅ Categoría creada'); load()
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  return (
    <div>
      <h1 className="page-title">🍽️ Administración de Menú</h1>
      {msg && <div className={`alert ${msg.startsWith('❌') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}

      <div className="flex gap-2 mb-4">
        <button className={`btn btn-sm ${tab==='items'?'btn-primary':'btn-outline'}`} onClick={() => setTab('items')}>Productos ({items.length})</button>
        <button className={`btn btn-sm ${tab==='cats'?'btn-primary':'btn-outline'}`} onClick={() => setTab('cats')}>Categorías</button>
      </div>

      {tab === 'items' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <span style={{fontWeight:600}}>{items.length} productos activos</span>
            <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>+ Nuevo producto</button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Nombre</th><th>Categoría</th><th>Precio</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {items.map(i => (
                  <tr key={i.item_id}>
                    <td>{i.name}</td>
                    <td>{categories.find(c => c.category_id === i.category_id)?.name || '-'}</td>
                    <td>Q{Number(i.price).toFixed(2)}</td>
                    <td>{i.out_of_stock
                      ? <span className="badge badge-red">Agotado</span>
                      : <span className="badge badge-green">Disponible</span>}
                    </td>
                    <td className="flex gap-2">
                      <button className="btn btn-warning btn-sm" onClick={() => toggleStock(i)}>
                        {i.out_of_stock ? 'Disponible' : 'Agotar'}
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => deleteItem(i.item_id)}>✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'cats' && (
        <div className="card">
          <div className="flex gap-2 mb-4">
            <input className="form-control" placeholder="Nueva categoría" value={catForm}
              onChange={e => setCatForm(e.target.value)} style={{maxWidth:240}}
              onKeyDown={e => e.key === 'Enter' && createCat()} />
            <button className="btn btn-primary" onClick={createCat}>Agregar</button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Nombre</th><th>Estado</th></tr></thead>
              <tbody>
                {categories.map(c => (
                  <tr key={c.category_id}>
                    <td>{c.category_id}</td>
                    <td>{c.name}</td>
                    <td><span className="badge badge-green">Activa</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Nuevo Producto</div>
            <div className="form-group">
              <label>Nombre</label>
              <input className="form-control" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} />
            </div>
            <div className="form-group">
              <label>Descripción (opcional)</label>
              <input className="form-control" value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))} />
            </div>
            <div className="form-group">
              <label>Precio (Q)</label>
              <input type="number" className="form-control" value={form.price}
                onChange={e => setForm(f => ({...f, price: e.target.value}))} min="0" step="0.01" />
            </div>
            <div className="form-group">
              <label>Categoría</label>
              <select className="form-control" value={form.category_id} onChange={e => setForm(f => ({...f, category_id: e.target.value}))}>
                <option value="">-- Seleccionar --</option>
                {categories.map(c => <option key={c.category_id} value={c.category_id}>{c.name}</option>)}
              </select>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={createItem}
                disabled={!form.name || !form.price || !form.category_id}>Crear</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
