<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-8">

        <!-- Back Button -->
        <div class="mb-3">
          <router-link to="/patient/doctor" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Back to Doctors
          </router-link>
        </div>

        <!-- Doctor Info -->
        <div v-if="doctor" class="mb-4 p-3 bg-light rounded">
          <h5>Doctor Information</h5>
          <p class="mb-1"><strong>Name:</strong> Dr. {{ doctor.full_name }}</p>
          <p class="mb-1"><strong>Specialization:</strong> {{ doctor.specialization }}</p>
          <p class="mb-0"><strong>Email:</strong> {{ doctor.email }}</p>
        </div>

        <!-- Available Slots -->
        <div v-if="Object.keys(groupedSlots).length">
          <h5 class="mb-3">Available Slots (Next 7 Days)</h5>

          <div v-for="(slots, date) in groupedSlots" :key="date" class="mb-3">
            <h6 class="text-primary">{{ date }}</h6>
            <div class="d-flex flex-wrap gap-2">
              <button v-for="slot in slots" :key="slot.id" class="btn"
                      :class="selectedSlot === slot.id ? 'btn-success' : 'btn-outline-primary'"
                      @click="selectSlot(slot.id)">
                {{ slot.time }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="alert alert-warning">
          No available slots for the next 7 days.
        </div>

        <!-- Reason for Visit -->
        <div class="mt-3">
          <label class="form-label"><strong>Reason for Visit</strong></label>
          <textarea
            v-model="reason"
            class="form-control"
            rows="3"
            placeholder="Describe your symptoms or reason for appointment">
          </textarea>
        </div>

        <!-- Confirm Booking -->
        <button class="btn btn-success w-100 mt-3" :disabled="!selectedSlot || loading" @click="bookSlot">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Confirm Booking
        </button>

      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { getPatientDoctors, bookAppointment } from '../../src/api'

export default {
  name: 'BookAppointment',

  data() {
    return {
      doctor: null,
      selectedSlot: null,
      loading: false,
      reason: ""
    }
  },

  computed: {
    ...mapGetters(['currentUser', 'doctors', 'slots']),

    groupedSlots() {
      const grouped = {}
      this.slots.forEach(slot => {
        if (!grouped[slot.date]) grouped[slot.date] = []
        grouped[slot.date].push(slot)
      })
      return grouped
    }
  },

  methods: {
    ...mapActions(['addMessage', 'fetchSlots']),

    async fetchDoctor() {
      const doctorId = parseInt(this.$route.params.id)
      this.doctor = this.doctors.find(d => d.id === doctorId)

      if (!this.doctor) {
        try {
          const res = await getPatientDoctors({})
          this.doctor = res.data.find(d => d.id === doctorId)
          if (!this.doctor) this.addMessage({ message: 'Doctor not found', delay: 3000 })
        } catch (err) {
          console.error(err)
          this.addMessage({ message: 'Failed to fetch doctor', delay: 3000 })
        }
      }
    },

    async loadSlots() {
      const doctorId = parseInt(this.$route.params.id)
      await this.fetchSlots(doctorId)
    },

    selectSlot(slotId) {
      this.selectedSlot = slotId
    },

    async bookSlot() {
      if (!this.selectedSlot) return
      try {
        this.loading = true
        await bookAppointment(this.selectedSlot, { reason: this.reason })
        this.addMessage({ message: { category: 'success', text: 'Appointment booked successfully' }, delay: 3000 })

      } catch (err) {
        console.error(err)
        this.addMessage({ message: err.response?.data?.error || 'Failed to book slot', delay: 3000 })
      } finally {
        this.loading = false
      }
    }
  },

  async mounted() {
    await this.fetchDoctor()
    await this.loadSlots()
  }
}
</script>