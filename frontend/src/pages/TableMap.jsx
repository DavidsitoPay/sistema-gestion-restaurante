import { useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const STATUS_LABELS = { LIBRE: 'Libre', OCUPADA: 'Ocupada', PENDIENTE: 'Pendiente', PAGANDO: 'Pagando' }

export default function TableMap() {
  const [tables, setTables] = useState([])
  const [filter, setFilter] = useState('ALL')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const { data } = await api.get('/tables/')
      setTables(data)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t) }, [load])

  const visible = filter === 'ALL' ? tables : tables.filter(t => t.status === filter)
  const counts = tables.reduce((a, t) => { a[t.status] = (a[t.status] || 0) + 1; return a }, {})

  if (loading) return <div className="spinner" />

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title" style={{marginBottom:0}}>Mapa de Mesas</h1>
        <button className="btn btn-outline btn-sm" onClick={load}>↻ Actualizar</button>
      </div>

      <div className="flex gap-2 mb-4" style={{flexWrap:'wrap'}}>
        {Object.entries(STATUS_LABELS).map(([k, v]) => (
          <span key={k} className={`badge badge-${k==='LIBRE'?'green':k==='OCUPADA'?'red':k==='PENDIENTE'?'yellow':'blue'}`}>
            {v}: {counts[k] || 0}
          </span>
        ))}
      </div>

      <div className="filters">
        {['ALL', ...Object.keys(STATUS_LABELS)].map(s => (
          <button key={s} className={`btn btn-sm ${filter===s?'btn-primary':'btn-outline'}`}
            onClick={() => setFilter(s)}>{s==='ALL'?'Todas':STATUS_LABELS[s]}</button>
        ))}
      </div>

      <div className="mesa-grid">
        {visible.map(t => (
          <div key={t.table_id} className={`mesa-card ${t.status}`}>
            <div className="mesa-num">{t.code}</div>
            <div className="mesa-cap">👥 {t.capacity} personas</div>
            <div className="mesa-cap" style={{fontSize:10,color:'#6b7280'}}>{t.area}</div>
            <div className="mesa-status">{STATUS_LABELS[t.status]}</div>
          </div>
        ))}
      </div>
      {visible.length === 0 && <p className="text-muted" style={{textAlign:'center',marginTop:40}}>No hay mesas con ese filtro.</p>}
    </div>
  )
}
