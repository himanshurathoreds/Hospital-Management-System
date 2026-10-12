import axios from 'axios'

const API = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000' })

API.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = (username, password) => API.post('/login', { username, password })
export const register = (data) => API.post('/register', data)
export const getDashboard = () => API.get('/')
// admin api
export const getAdminDashboard = () => API.get('/admin/dashboard')
export const getAdminDepartments = () => API.get('/admin/departments')
export const addAdminDepartments = (department) => API.post('/admin/department/add', department)
export const getAdminDoctors = (params) => API.get('/admin/doctor', { params })
export const addAdminDoctor = (doctor) => API.post('/admin/doctor/add', doctor)
export const updateAdminDoctor = (id, doctor) => API.put(`/admin/doctor/edit/${id}`, doctor)
export const deleteAdminDoctor = (id) => API.delete(`/admin/doctor/delete/${id}`)
export const getAdminPatients = (params) => API.get('/admin/patient', { params })
export const updateAdminPatient = (id, patient) => API.put(`/admin/patient/edit/${id}`, patient)
export const deleteAdminPatient = (id) => API.delete(`/admin/patient/delete/${id}`)
export const getAdminAppointments = (params) => API.get('/admin/appointments', { params })
// doctor api
export const getDoctorDashboard = () => API.get('/doctor/dashboard')
export const getDoctorAppointment = (params) => API.get('/doctor/appointments', { params })
export const completeDoctorAppointment = (id, payload) => API.post(`/doctor/appointments/${id}/complete`, payload)
export const cancelDoctorAppointment = (id) => API.post(`/doctor/appointments/${id}/cancel`)
export const getDoctorTime = () => API.get('/doctor/timeslots')
export const getPatientHistory = (id) => API.get(`/doctor/patient/${id}/history`)
export const addDoctorTime = (slot) => API.post('/doctor/timeslots', slot)
export const updateDoctorTime = (id, slot) => API.put(`/doctor/timeslots/${id}`, slot)
export const deleteDoctorTime = (id) => API.delete(`/doctor/timeslots/${id}`)
export const createDoctorTreatment = (payload) => API.post(`/doctor/treatment/`, payload);
export const getDoctorTreatment = (appointmentId) => API.get(`/doctor/treatment/${appointmentId}`)
export const updateDoctorTreatment = (treatmentId, payload) => API.put(`/doctor/treatment/${treatmentId}`, payload)
export const deleteDoctorTreatment = (treatmentId) => API.delete(`/doctor/treatment/${treatmentId}`)
// patient api
export const getPatientDashboard = () => API.get('/patient/dashboard')
export const getPatientDoctors = (params) => API.get('/patient/doctor', { params })
export const bookAppointment = (slotId, data) => API.post(`/patient/book/${slotId}`, data)
export const getDoctorSlots = (doctorId) => API.get(`/patient/doctor/${doctorId}/slots`)
export const getPatientAppointments = (params) => API.get('/patient/appointments', { params })
export const cancelPatientAppointment = (id) => API.post(`/patient/appointments/${id}/cancel`)
export const reschedulePatientAppointment = (id, payload) => API.put(`/patient/appointments/${id}/reschedule`, payload)
export const getHistory = () => API.get('/patient/history')
export const getHistoryExport = () => API.post('/patient/history/export_csv', {}, { responseType: 'blob' })
export const getPatientProfile = () => API.get('/patient/profile')
export const updatePatientProfile = (data) => API.put('/patient/profile', data)
