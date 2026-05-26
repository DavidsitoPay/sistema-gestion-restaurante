import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const COLS = [
  { status: 'ENVIADO',        label: '📥 Recibido',       next: 'EN_PREPARACION', nextLabel: 'Iniciar preparación' },
  { status: 'EN_PREPARACION', label: '🔥 En Preparación', next: 'LISTO',          nextLabel: 'Marcar listo ✓' },
  { status: 'LISTO',          label: '✅ Listo',          next: 'ENTREGADO',      nextLabel: 'Marcar entregado' },
]

export default function KitchenDisplay() {
  const [orders, setOrders] = useState([])
  const [tables, setTables] = useState([])
  const [menuItems, setMenuItems] = useState([])
  const [msg, setMsg] = useState('')

  const load = useCallback(async () => {
    const [o, t, m] = await Promise.all([
      api.get('/orders/').then(r => r.data),
      api.get('/tables/').then(r => r.data),
      api.get('/menu/items').then(r => r.data),
    ])
    setOrders(o.filter(o => ['ENVIADO','EN_PREPARACION','LISTO'].includes(o.status)))
    setTables(t); setMenuItems(m)
  }, [])

  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t) }, [load])

  const advance = async (orderId, newStatus) => {
    try {
      await api.post(`/orders/${orderId}/kitchen-status`, null, { params: { new_status: newStatus } })
      setMsg('✅ Estado actualizado'); setTimeout(() => setMsg(''), 2000); load()
    } catch (e) { setMsg('❌ ' + (e.response?.data?.detail || 'Error')); setTimeout(() => setMsg(''), 3000) }
  }

  const tableName = id => tables.find(t => t.table_id === id)?.code || `#${id}`
  const itemName = id => menuItems.find(m => m.item_id === id)?.name || `Producto #${id}`

  const elapsedMin = sentAt => {
    if (!sentAt) return 0
    return Math.floor((Date.now() - new Date(sentAt).getTime()) / 60000)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title" style={{marginBottom:0}}>🍳 Pantalla de Cocina (KDS)</h1>
        <button className="btn btn-outline btn-sm" onClick={load}>↻ Actualizar</button>
      </div>
      {msg && <div className={`alert ${msg.startsWith('❌') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}

      <div className="kds-grid">
        {COLS.map(col => {
          const colOrders = orders.filter(o => o.status === col.status)
          return (
            <div key={col.status} className="kds-col">
              <div className="kds-col-header" style={{
                background: col.status==='LISTO' ? '#d1fae5' : col.status==='EN_PREPARACION' ? '#fef3c7' : '#f3f4f6'
              }}>
                {col.label} <span style={{fontWeight:400,fontSize:12}}>({colOrders.length})</span>
              </div>
              {colOrders.length === 0 && (
                <div className="kds-order text-muted" style={{textAlign:'center',padding:24}}>Sin pedidos</div>
              )}
              {colOrders.map(o => {
                const mins = elapsedMin(o.sent_to_kitchen_at)
                return (
                  <div key={o.order_id} className="kds-order">
                    <div className="flex justify-between items-center">
                      <strong>Mesa {tableName(o.table_id)}</strong>
                      <span className={`badge ${mins > 15 ? 'badge-red' : mins > 8 ? 'badge-yellow' : 'badge-green'}`}>
                        {mins} min
                      </span>
                    </div>
                    <div className="kds-order-meta">Pedido #{o.order_id}</div>
                    <ul className="kds-items mt-2">
                      {o.items?.filter(i => !i.canceled).map(i => (
                        <li key={i.order_item_id}>
                          <strong>{i.quantity}x</strong> {itemName(i.item_id)}
                          {i.notes && <span className="text-muted"> — {i.notes}</span>}
                        </li>
                      ))}
                    </ul>
                    <button className="btn btn-primary btn-sm mt-2" style={{width:'100%',justifyContent:'center'}}
                      onClick={() => advance(o.order_id, col.next)}>
                      {col.nextLabel}
                    </button>
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
