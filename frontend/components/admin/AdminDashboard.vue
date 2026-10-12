<template>
    <div class="container-fluid">
        <div class="row justice-content-center">
            <h2 class="mb-4"><i class="bi bi-speedometer2"></i> Admin Dashboard</h2>
        </div>

        <div class="row">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <h6 class="text-muted">Total Doctors</h6>
                        <h2 class="mb-0">{{ dashboard.total_doctors }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <h6 class="text-muted">Total Patients</h6>
                        <h2 class="mb-0">{{ dashboard.total_patients }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <h6 class="text-muted">Total Appointments</h6>
                        <h2 class="mb-0">{{ dashboard.total_appointments }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <h6 class="text-muted">Pending Appointments</h6>
                        <h2 class="mb-0">{{ dashboard.pending_appointments }}</h2>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0">Recent Appointments</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Patient</th>
                                <th>Doctor</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="apt in dashboard.recent_appointments" :key="apt.id">
                                <td>{{ apt.id }}</td>
                                <td>{{ apt.patient.full_name }}</td>
                                <td>{{ apt.doctor.full_name }}</td>
                                <td>{{ apt.date }}</td>
                                <td>{{ apt.time }}</td>
                                <td>
                                    <span :class="statusClass(apt.status)">
                                        {{ apt.status }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import { getAdminDashboard } from '../../src/api'

export default {
  data() {
    return {
      dashboard: {
        total_doctors: 0,
        total_patients: 0,
        total_appointments: 0,
        pending_appointments: 0,
        recent_appointments: []
      }
    }
  },
  async mounted() {
    try {
      const { data } = await getAdminDashboard()
      this.dashboard = data
    } catch (err) {
      console.error("Failed to load dashboard:", err)
    }
  },
  methods: {
    statusClass(status) {
      if (status === 'Booked') return 'badge bg-primary'
      if (status === 'Completed') return 'badge bg-success'
      return 'badge bg-secondary'
    }
  }
}
</script>