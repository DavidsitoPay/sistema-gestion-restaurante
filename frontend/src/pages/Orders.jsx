import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const STATUS_COLORS = { ABIERTO:'badge-gray', ENVIADO:'badge-yellow', EN_PREPARACION:'badge-blue', LISTO:'badge-green', ENTREGADO:'badge-green', CERRADO:'badge-gray' }

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [tables, setTables] = useState([])
  const [menuItems, setMenuItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({ table_id: '', notes: '' })
  const [addItem, setAddItem] = useState({ item_id: '', quantity: 1, notes: '' })
  const [msg, setMsg] = useState('')

  const load = useCallback(async () => {
    const [o, t, m] = await Promise.all([
      api.get('/orders/').then(r => r.data),
      api.get('/tables/').then(r => r.data),
      api.get('/menu/items').then(r => r.data),
    ])
    setOrders(o); setTables(t); setMenuItems(m)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  const openOrder = async () => {
    try {
      await api.post('/orders/', { table_id: Number(createForm.table_id), notes: createForm.notes })
      setShowCreate(false); setCreateForm({ table_id: '', notes: '' }); flash('✅ Pedido creado'); load()
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  const sendToKitchen = async id => {
    try { await api.post(`/orders/${id}/send-to-kitchen`); flash('✅ Enviado a cocina'); load() }
    catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  const doAddItem = async () => {
    if (!addItem.item_id) return
    try {
      await api.post(`/orders/${selected.order_id}/items`, {
        item_id: Number(addItem.item_id), quantity: Number(addItem.quantity), notes: addItem.notes
      })
      setAddItem({ item_id: '', quantity: 1, notes: '' }); flash('✅ Ítem agregado'); load()
      const { data } = await api.get(`/orders/${selected.order_id}`); setSelected(data)
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  if (loading) return <div className="spinner" />

  const freeTables = tables.filter(t => t.status === 'LIBRE')
  const openOrders = orders.filter(o => o.status !== 'CERRADO')

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title" style={{marginBottom:0}}>Pedidos</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Nuevo Pedido</button>
      </div>
      {msg && <div className={`alert ${msg.startsWith('❌') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Mesa</th><th>Estado</th><th>Ítems</th><th>Hora</th><th>Acciones</th></tr></thead>
            <tbody>
              {openOrders.map(o => (
                <tr key={o.order_id}>
                  <td>#{o.order_id}</td>
                  <td>{tables.find(t => t.table_id === o.table_id)?.code || o.table_id}</td>
                  <td><span className={`badge ${STATUS_COLORS[o.status]}`}>{o.status}</span></td>
                  <td>{o.items?.filter(i => !i.canceled).length || 0} ítems</td>
                  <td>{o.opened_at ? new Date(o.opened_at).toLocaleTimeString() : '-'}</td>
                  <td className="flex gap-2">
                    <button className="btn btn-outline btn-sm" onClick={() => setSelected(o)}>Ver</button>
                    {o.status === 'ABIERTO' && <button className="btn btn-primary btn-sm" onClick={() => sendToKitchen(o.order_id)}>→ Cocina</button>}
                  </td>
                </tr>
              ))}
              {openOrders.length === 0 && <tr><td colSpan={6} style={{textAlign:'center',color:'#9ca3af',padding:24}}>No hay pedidos abiertos</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Nuevo Pedido</div>
            <div className="form-group">
              <label>Mesa disponible</label>
              <select className="form-control" value={createForm.table_id} onChange={e => setCreateForm(f => ({...f, table_id: e.target.value}))}>
                <option value="">-- Seleccionar --</option>
                {freeTables.map(t => <option key={t.table_id} value={t.table_id}>{t.code} ({t.area})</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Notas (opcional)</label>
              <input className="form-control" value={createForm.notes} onChange={e => setCreateForm(f => ({...f, notes: e.target.value}))} />
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowCreate(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={openOrder} disabled={!createForm.table_id}>Crear Pedido</button>
            </div>
          </div>
        </div>
      )}

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">
              Pedido #{selected.order_id} · Mesa {tables.find(t => t.table_id === selected.table_id)?.code}
            </div>
            <span className={`badge ${STATUS_COLORS[selected.status]}`}>{selected.status}</span>
            <hr className="divider" />
            <div style={{marginBottom:12}}>
              {selected.items?.filter(i => !i.canceled).map(i => {
                const mi = menuItems.find(m => m.item_id === i.item_id)
                return (
                  <div key={i.order_item_id} className="flex justify-between" style={{padding:'4px 0',borderBottom:'1px solid #f3f4f6'}}>
                    <span>{i.quantity}x {mi?.name || `Item #${i.item_id}`}
                      {i.notes ? <span className="text-muted"> ({i.notes})</span> : ''}
                    </span>
                    <span>Q{(Number(i.unit_price_snapshot) * i.quantity).toFixed(2)}</span>
                  </div>
                )
              })}
              {selected.items?.filter(i => !i.canceled).length === 0 && (
                <p className="text-muted">Sin ítems aún.</p>
              )}
            </div>
            {selected.status === 'ABIERTO' && (
              <>
                <div style={{fontWeight:600,marginBottom:8}}>Agregar ítem</div>
                <div className="flex gap-2" style={{flexWrap:'wrap'}}>
                  <select className="form-control" style={{flex:2}} value={addItem.item_id}
                    onChange={e => setAddItem(a => ({...a, item_id: e.target.value}))}>
                    <option value="">-- Producto --</option>
                    {menuItems.filter(m => !m.out_of_stock).map(m =>
                      <option key={m.item_id} value={m.item_id}>{m.name} Q{Number(m.price).toFixed(2)}</option>
                    )}
                  </select>
                  <input type="number" min={1} className="form-control" style={{width:60}}
                    value={addItem.quantity} onChange={e => setAddItem(a => ({...a, quantity: e.target.value}))} />
                  <input className="form-control" style={{flex:2}} placeholder="Nota"
                    value={addItem.notes} onChange={e => setAddItem(a => ({...a, notes: e.target.value}))} />
                  <button className="btn btn-success" onClick={doAddItem}>+</button>
                </div>
              </>
            )}
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setSelected(null)}>Cerrar</button>
              {selected.status === 'ABIERTO' && (
                <button className="btn btn-primary" onClick={() => { sendToKitchen(selected.order_id); setSelected(null) }}>
                  Enviar a Cocina
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
