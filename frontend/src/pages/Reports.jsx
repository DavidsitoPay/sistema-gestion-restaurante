import { useState } from 'react'
import api from '../api/client'

export default function Reports() {
  const [tab, setTab] = useState('sales')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [salesData, setSalesData] = useState(null)
  const [topData, setTopData] = useState([])
  const [auditData, setAuditData] = useState([])
  const [loading, setLoading] = useState(false)

  const params = () => {
    const p = {}
    if (dateFrom) p.date_from = dateFrom
    if (dateTo) p.date_to = dateTo
    return p
  }

  const fetch = async () => {
    setLoading(true)
    try {
      if (tab === 'sales') {
        const { data } = await api.get('/reports/sales', { params: params() })
        setSalesData(data)
      } else if (tab === 'top') {
        const { data } = await api.get('/reports/top-products', { params: params() })
        setTopData(data)
      } else {
        const { data } = await api.get('/reports/audit', { params: params() })
        setAuditData(data)
      }
    } finally { setLoading(false) }
  }

  return (
    <div>
      <h1 className="page-title">📊 Reportes</h1>

      <div className="flex gap-2 mb-4">
        {[['sales','Ventas por Fecha'],['top','Top Productos'],['audit','Bitácora']].map(([k,v]) => (
          <button key={k} className={`btn btn-sm ${tab===k?'btn-primary':'btn-outline'}`} onClick={() => setTab(k)}>{v}</button>
        ))}
      </div>

      <div className="card">
        <div className="filters">
          <div>
            <label style={{fontSize:13,fontWeight:500,marginRight:6}}>Desde</label>
            <input type="date" className="form-control" style={{width:'auto',display:'inline'}}
              value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          </div>
          <div>
            <label style={{fontSize:13,fontWeight:500,marginRight:6}}>Hasta</label>
            <input type="date" className="form-control" style={{width:'auto',display:'inline'}}
              value={dateTo} onChange={e => setDateTo(e.target.value)} />
          </div>
          <button className="btn btn-primary" disabled={loading} onClick={fetch}>
            {loading ? 'Cargando...' : 'Consultar'}
          </button>
        </div>

        {tab === 'sales' && salesData && (
          <div style={{marginTop:16}}>
            <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:16}}>
              {[
                { label:'Ventas totales',    value:`Q${salesData.total_sales?.toFixed(2)}`, color:'#057a55' },
                { label:'Subtotal (sin IVA)',value:`Q${salesData.subtotal?.toFixed(2)}`,    color:'#1a56db' },
                { label:'IVA 12%',          value:`Q${salesData.total_tax?.toFixed(2)}`,   color:'#c27803' },
              ].map(s => (
                <div key={s.label} style={{background:'#f9fafb',borderRadius:8,padding:16,textAlign:'center'}}>
                  <div style={{fontSize:22,fontWeight:700,color:s.color}}>{s.value}</div>
                  <div style={{fontSize:12,color:'#6b7280',marginTop:4}}>{s.label}</div>
                </div>
              ))}
            </div>
            <p className="text-muted">Órdenes cerradas en el período: <strong>{salesData.count}</strong></p>
          </div>
        )}

        {tab === 'top' && topData.length > 0 && (
          <div style={{marginTop:16}}>
            <table>
              <thead><tr><th>#</th><th>Producto</th><th>Cant. vendida</th><th>Total (Q)</th></tr></thead>
              <tbody>
                {topData.map((p, i) => (
                  <tr key={p.name}>
                    <td>{i+1}</td><td>{p.name}</td><td>{p.qty}</td><td>Q{p.amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'audit' && auditData.length > 0 && (
          <div style={{marginTop:16}}>
            <table>
              <thead><tr><th>Fecha/Hora</th><th>Entidad</th><th>Acción</th><th>Detalles</th></tr></thead>
              <tbody>
                {auditData.map(a => (
                  <tr key={a.audit_id}>
                    <td style={{whiteSpace:'nowrap'}}>{a.created_at ? new Date(a.created_at).toLocaleString() : '-'}</td>
                    <td>{a.entity} #{a.entity_id}</td>
                    <td><code>{a.action}</code></td>
                    <td>{a.details || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !salesData && topData.length === 0 && auditData.length === 0 && (
          <p className="text-muted" style={{textAlign:'center',padding:32}}>
            Selecciona un rango de fechas y presiona Consultar
          </p>
        )}
      </div>
    </div>
  )
}
