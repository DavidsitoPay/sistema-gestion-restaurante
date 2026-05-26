import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/',        label: '🗺️ Mapa de Mesas',    roles: ['ADMIN','HOST','MESERO','CAJERO'] },
  { to: '/orders',  label: '📋 Pedidos',           roles: ['ADMIN','MESERO','HOST'] },
  { to: '/kitchen', label: '👨‍🍳 Cocina (KDS)',     roles: ['ADMIN','COCINA'] },
  { to: '/billing', label: '💳 Caja / Cuenta',     roles: ['ADMIN','CAJERO'] },
  { to: '/menu',    label: '🍽️ Menú',              roles: ['ADMIN'] },
  { to: '/users',   label: '👥 Usuarios',          roles: ['ADMIN'] },
  { to: '/reports', label: '📊 Reportes',          roles: ['ADMIN'] },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }
  const visible = navItems.filter(n => n.roles.includes(user?.role))

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          🍴 RestaurantePRO
          <span>{user?.full_name} ({user?.role})</span>
        </div>
        <nav>
          {visible.map(n => (
            <NavLink key={n.to} to={n.to} end={n.to === '/'} className={({ isActive }) => isActive ? 'active' : ''}>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div>{user?.username}</div>
          <button onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
