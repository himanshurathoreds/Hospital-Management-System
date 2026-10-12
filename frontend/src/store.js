import { createStore } from 'vuex'
import {
  getAdminDoctors, getAdminPatients, deleteAdminPatient, updateAdminPatient, getAdminAppointments, getAdminDepartments,
  getDoctorAppointment, getDoctorTreatment, updateDoctorTreatment, deleteDoctorTreatment, getDoctorSlots, getPatientDoctors,
  cancelDoctorAppointment, completeDoctorAppointment, getPatientAppointments, cancelPatientAppointment, reschedulePatientAppointment, getHistory
} from './api'

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    current_user: {
      is_authenticated: !!localStorage.getItem('token'),
      full_name: localStorage.getItem('user') || '',
      role: localStorage.getItem('role') || ''
    },
    messages: [],
    doctors: [],
    departments: [],
    patients: [],
    appointments: [],
    showModal: false,
    modalType: null,
    modalData: null,
    slots: []
  },
  mutations: {
    setUser(state, { token, full_name, role }) {
      state.token = token
      state.current_user = {
        is_authenticated: true,
        full_name,
        role
      }
      localStorage.setItem('token', token)
      localStorage.setItem('user', full_name)
      localStorage.setItem('role', role)
    },
    logout(state) {
      state.token = null
      state.current_user = {
        is_authenticated: false,
        full_name: '',
        role: ''
      }
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
    },
    addMessage(state, message) {
      state.messages.push(message)
    },
    removeMessage(state, index) {
      state.messages.splice(index, 1)
    },
    setDoctors(state, doctors) {
      state.doctors = doctors
    },
    setPatients(state, patients) {
      state.patients = patients
    },
    setDepartments(state, departments) {
      state.departments = departments
    },
    openEditModal(state, payload) {
      state.showModal = true;
      state.modalType = "edit";
      state.modalData = payload;
    },
    openDeleteModal(state, payload) {
      state.showModal = true;
      state.modalType = "delete";
      state.modalData = payload;
    },
    closeModal(state) {
      state.showModal = false;
      state.modalType = null;
      state.modalData = null;
    },
    openRescheduleModal(state, payload) {
      state.showModal = true;
      state.modalType = "reschedule";
      state.modalData = payload;
    },
    setSlots(state, slots) {
      state.slots = slots
    },
    updatePatient(state, updatedPatient) {
      const index = state.patients.findIndex(p => p.id === updatedPatient.id)
      if (index !== -1) {
        state.patients.splice(index, 1, updatedPatient)
      }
    },
    deletePatient(state, patientId) {
      state.patients = state.patients.filter(p => p.id !== patientId)
    },
    setAppointments(state, appointments) {
      state.appointments = appointments
    },
    updateAppointmentStatus(state, { id, status, treatment = null }) {
      const index = state.appointments.findIndex(a => a.id === id);
      if (index !== -1) {
        state.appointments[index].status = status;
        if (treatment) state.appointments[index].treatment = treatment;
      }
    }

  },
  actions: {
    login({ commit }, payload) {
      commit('setUser', payload)
    },
    logout({ commit }) {
      commit('logout')
    },
    addMessage({ commit, state }, { message, delay }) {
      commit('addMessage', message);
      const index = state.messages.length - 1;
      setTimeout(() => {
        commit('removeMessage', index);
      }, delay);
    },
    removeMessage({ commit }, index) {
      commit('removeMessage', index)
    },
    openEditModal({ commit }, data) {
      commit("openEditModal", data);
    },
    openDeleteModal({ commit }, data) {
      commit("openDeleteModal", data);
    },
    closeModal({ commit }) {
      commit("closeModal");
    },
    openRescheduleModal({ commit }, data) {
      commit("openRescheduleModal", data);
    },
    async fetchDoctors({ commit }, params) {
      const { data } = await getAdminDoctors(params);
      commit('setDoctors', data.doctors || []);
      commit('setDepartments', data.departments || []);
    },
    async fetchDepartments({ commit }) {
      const { data } = await getAdminDepartments();
      commit('setDepartments', data.departments || []);
    },
    async fetchPatientDoctors({ commit }, params) {
      const { data } = await getPatientDoctors(params);
      commit('setDoctors', Array.isArray(data) ? data : data.doctors || []);
    },
    async fetchPatients({ commit }, params) {
      const { data } = await getAdminPatients(params)
      commit('setPatients', data.patients || [])
    },
    async updatePatient({ commit }, patient) {
      const { data } = await updateAdminPatient(patient.id, patient)
      commit('updatePatient', data)
    },
    async deletePatient({ commit }, patient) {
      await deleteAdminPatient(patient.id)
      commit('deletePatient', patient.id)
    },
    async fetchAppointments({ commit, rootState }, params = {}) {
      try {
        let data = []
        const role = rootState.current_user?.role

        if (role === 'admin') {
          const res = await getAdminAppointments(params)
          data = res.data.appointments || []
        } else if (role === 'doctor') {
          const res = await getDoctorAppointment(params)
          data = res.data.appointments || []
        } else if (role === 'patient') {
          const res = await getPatientAppointments(params)
          data = res.data || []
        }

        commit('setAppointments', data)
      } catch (error) {
        console.error('Failed to fetch appointments', error)
        throw error
      }
    },
    async rescheduleAppointment({ dispatch }, { id, slot_id }) {
      try {
        await reschedulePatientAppointment(id, { slot_id })
        dispatch("fetchAppointments")
      } catch (error) {
        console.error("Failed to reschedule appointment", error)
      }
    },
    async fetchSlots({ commit }, doctorId) {
      try {
        const res = await getDoctorSlots(doctorId)  // axios call with token automatically
        commit('setSlots', res.data)               // save slots in Vuex state
      } catch (error) {
        console.error('Failed to fetch slots', error)
      }
    },
    async fetchDoctorTreatment(_, appointmentId) {
      try {
        const { data } = await getDoctorTreatment(appointmentId)
        return data
      } catch (error) {
        console.error('Failed to fetch treatment', error)
        throw error
      }
    },
    async updateDoctorTreatment(_, { treatmentId, payload }) {
      try {
        const { data } = await updateDoctorTreatment(treatmentId, payload)
        return data.message
      } catch (error) {
        console.error('Failed to update treatment', error)
        throw error
      }
    },
    async deleteDoctorTreatment(_, treatmentId) {
      try {
        const { data } = await deleteDoctorTreatment(treatmentId)
        return data.message
      } catch (error) {
        console.error('Failed to delete treatment', error)
        throw error
      }
    },
    async completeAppointment({ commit }, { id, data }) {
      try {
        const res = await completeDoctorAppointment(id, data);
        commit('updateAppointmentStatus', { id, status: 'Completed', treatment: res });
        commit('closeModal');
      } catch (error) {
        console.error('Failed to complete appointment', error);
      }
    },
    async cancelAppointment({ commit, rootState }, { id }) {
      try {
        const role = rootState.current_user?.role

        if (role === "doctor") {
          await cancelDoctorAppointment(id)
        } else if (role === "patient") {
          await cancelPatientAppointment(id)
        }

        commit("updateAppointmentStatus", { id, status: "Cancelled" })
        commit("closeModal")

      } catch (error) {
        console.error("Failed to cancel appointment", error)
      }
    },
    async fetchPatientHistory({ commit }) {
      try {
        const { data } = await getHistory()
        commit('setAppointments', data)
      } catch (error) {
        console.error('Failed to fetch patient history', error)
      }
    }
  },
  getters: {
    currentUser: state => state.current_user,
    isAuthenticated: state => state.current_user.is_authenticated,
    messages: state => state.messages,
    doctors: state => state.doctors,
    departments: state => state.departments,
    patients: state => state.patients,
    appointments: state => state.appointments,
    showModal: state => state.showModal,
    modalType: state => state.modalType,
    modalData: state => state.modalData,
    slots: state => state.slots
  }
})
