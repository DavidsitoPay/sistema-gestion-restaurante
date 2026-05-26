import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

export default function Billing() {
  const [orders, setOrders] = useState([])
  const [tables, setTables] = useState([])
  const [menuItems, setMenuItems] = useState([])
  const [selected, setSelected] = useState(null)
  const [bill, setBill] = useState(null)
  const [amount, setAmount] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    const [o, t, m] = await Promise.all([
      api.get('/orders/').then(r => r.data),
      api.get('/tables/').then(r => r.data),
      api.get('/menu/items').then(r => r.data),
    ])
    setOrders(o.filter(o => o.status !== 'CERRADO')); setTables(t); setMenuItems(m)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 3000) }
  const tableName = id => tables.find(t => t.table_id === id)?.code || `Mesa #${id}`
  const itemName = id => menuItems.find(m => m.item_id === id)?.name || `#${id}`

  const openBilling = async order => {
    setSelected(order); setBill(null); setAmount('')
    try {
      const { data } = await api.get(`/billing/orders/${order.order_id}/bill`)
      setBill(data)
    } catch {} // eslint-disable-line no-empty
  }

  const generateBill = async () => {
    try {
      const { data } = await api.post(`/billing/orders/${selected.order_id}/bill`)
      setBill(data); flash('✅ Cuenta generada')
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  const payBill = async () => {
    if (!amount || Number(amount) <= 0) return flash('❌ Ingresa el monto')
    try {
      await api.post(`/billing/orders/${selected.order_id}/pay`, { amount: Number(amount) })
      flash('✅ Pago registrado. Mesa liberada.'); setSelected(null); load()
    } catch (e) { flash('❌ ' + (e.response?.data?.detail || 'Error')) }
  }

  if (loading) return <div className="spinner" />

  return (
    <div>
      <h1 className="page-title">💳 Caja / Facturación</h1>
      {msg && <div className={`alert ${msg.startsWith('❌') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Pedido</th><th>Mesa</th><th>Estado</th><th>Ítems</th><th>Acción</th></tr></thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.order_id}>
                  <td>#{o.order_id}</td>
                  <td>{tableName(o.table_id)}</td>
                  <td><span className="badge badge-yellow">{o.status}</span></td>
                  <td>{o.items?.filter(i => !i.canceled).length}</td>
                  <td><button className="btn btn-primary btn-sm" onClick={() => openBilling(o)}>Facturar</button></td>
                </tr>
              ))}
              {orders.length === 0 && (
                <tr><td colSpan={5} style={{textAlign:'center',color:'#9ca3af',padding:24}}>Sin pedidos pendientes de cobro</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Cuenta — Pedido #{selected.order_id} · {tableName(selected.table_id)}</div>

            <div style={{fontSize:13}}>
              {selected.items?.filter(i => !i.canceled).map(i => (
                <div key={i.order_item_id} className="flex justify-between"
                  style={{padding:'4px 0',borderBottom:'1px solid #f3f4f6'}}>
                  <span>{i.quantity}x {itemName(i.item_id)}</span>
                  <span>Q{(Number(i.unit_price_snapshot) * i.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>

            {bill && (
              <div style={{marginTop:12,background:'#f9fafb',borderRadius:6,padding:12}}>
                <div className="flex justify-between text-muted">
                  <span>Subtotal (sin IVA)</span><span>Q{Number(bill.subtotal).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>IVA 12%</span><span>Q{Number(bill.tax_amount).toFixed(2)}</span>
                </div>
                <hr className="divider" />
                <div className="flex justify-between" style={{fontWeight:700,fontSize:16}}>
                  <span>TOTAL</span><span>Q{Number(bill.total).toFixed(2)}</span>
                </div>
              </div>
            )}

            {!bill && (
              <button className="btn btn-warning mt-4" style={{width:'100%',justifyContent:'center'}} onClick={generateBill}>
                Generar Cuenta
              </button>
            )}

            {bill && !bill.paid && (
              <div className="mt-4">
                <div className="form-group">
                  <label>Monto recibido (Q)</label>
                  <input type="number" className="form-control" value={amount}
                    onChange={e => setAmount(e.target.value)} min={Number(bill.total)} step="0.01" />
                </div>
                {amount && Number(amount) >= Number(bill.total) && (
                  <div className="text-muted mb-4">Cambio: Q{(Number(amount) - Number(bill.total)).toFixed(2)}</div>
                )}
                <button className="btn btn-success" style={{width:'100%',justifyContent:'center'}} onClick={payBill}>
                  Registrar Pago ✓
                </button>
              </div>
            )}

            {bill?.paid && <div className="alert alert-success mt-4">✅ Esta cuenta ya fue pagada</div>}

            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setSelected(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
