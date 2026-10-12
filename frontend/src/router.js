import { createRouter, createWebHistory } from 'vue-router'
import BaseLayout from '../components/BaseLayout.vue'
import Login from '../components/auth/login.vue'
import Register from '../components/auth/register.vue'
import AdminDashboard from '../components/admin/AdminDashboard.vue'
import AdminDoctor from '../components/admin/AdminDoctor.vue'
import AdminPatient from '../components/admin/AdminPatient.vue'
import Departments from '../components/admin/Departments.vue'
import AdminAppointments from '../components/admin/AdminAppointments.vue'
import DoctorDashboard from '../components/doctor/DoctorDashboard.vue'
import DoctorAppointment from '../components/doctor/DoctorAppointment.vue'
import DoctorTime from '../components/doctor/DoctorTime.vue'
import DoctorPatientHistory from '../components/doctor/DoctorPatientHistory.vue'
import PatientDashboard from '../components/patient/PatientDashboard.vue'
import PatientDoctor from '../components/patient/PatientDoctors.vue'
import BookAppointment from '../components/patient/BookAppointment.vue'
import PatientAppointment from '../components/patient/PatientAppointment.vue'
import PatientHistory from '../components/patient/PatientHistory.vue'
import PatientProfile from '../components/patient/Profile.vue'

const routes = [
  {
    path: '/',
    component: BaseLayout,
    children: [
      { path: 'login', component: Login },
      { path: 'register', component: Register },
      { path: 'admin/dashboard', component: AdminDashboard },
      { path: 'admin/doctor', component: AdminDoctor },
      { path: 'admin/patient', component: AdminPatient },
      { path: 'admin/departments', component: Departments },
      { path: 'admin/appointments', component: AdminAppointments },
      { path: 'doctor/dashboard', component: DoctorDashboard },
      { path: 'doctor/patient/:id/history', component: DoctorPatientHistory },
      { path: 'doctor/appointments', component: DoctorAppointment },
      { path: 'doctor/timeslots', component: DoctorTime },
      { path: 'doctor/treatment', component: DoctorPatientHistory },
      { path: 'patient/dashboard', component: PatientDashboard },
      { path: 'patient/doctor', component: PatientDoctor },
      { path: 'patient/appointments', component: PatientAppointment },
      { path: 'patient/book/:id', component: BookAppointment },
      { path: 'patient/history', component: PatientHistory },
      { path: 'patient/profile', component: PatientProfile },

      ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (!token && to.path !== '/login' && to.path !== '/register') {
    next('/login')
  } else if (token) {
    if (to.path === '/admin/dashboard' && role !== 'admin') {
      next('/login')
    } else if (to.path === '/doctor/dashboard' && role !== 'doctor') {
      next('/login')
    } else if (to.path === '/patient/dashboard' && role !== 'patient') {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router