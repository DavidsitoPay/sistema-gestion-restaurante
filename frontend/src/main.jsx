import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import './index.css'

import Login from './pages/Login'
import Layout from './components/Layout'
import TableMap from './pages/TableMap'
import Orders from './pages/Orders'
import KitchenDisplay from './pages/KitchenDisplay'
import Billing from './pages/Billing'
import MenuManagement from './pages/MenuManagement'
import Users from './pages/Users'
import Reports from './pages/Reports'

function PrivateRoute({ children, roles }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<TableMap />} />
            <Route path="orders" element={<Orders />} />
            <Route path="kitchen" element={<PrivateRoute roles={['COCINA','ADMIN']}><KitchenDisplay /></PrivateRoute>} />
            <Route path="billing" element={<PrivateRoute roles={['CAJERO','ADMIN']}><Billing /></PrivateRoute>} />
            <Route path="menu" element={<PrivateRoute roles={['ADMIN']}><MenuManagement /></PrivateRoute>} />
            <Route path="users" element={<PrivateRoute roles={['ADMIN']}><Users /></PrivateRoute>} />
            <Route path="reports" element={<PrivateRoute roles={['ADMIN']}><Reports /></PrivateRoute>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
