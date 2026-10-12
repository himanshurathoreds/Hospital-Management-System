<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-speedometer2"></i> Doctor Dashboard</h2>

        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-calendar-week"></i> Upcoming Appointments (Next 7 Days)</h5>
                    </div>
                    <div class="card-body">
                        <p v-if="upcomingAppointments.length === 0" class="text-center text-muted mb-0">No upcoming
                            appointments</p>
                        <div class="list-group" v-for="apt in upcomingAppointments" :key="apt.id">
                            <div class="list-group-item">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <h6 class="mb-1">{{ apt.patient.full_name }}</h6>
                                        <p class="mb-1"><i class="bi bi-calendar3"></i> {{ apt.date }} at {{
                                            formatTime(apt.time) }}</p>
                                        <small class="text-muted">{{ apt.reason ? (apt.reason.length > 80 ? apt.reason.slice(0, 80) +
                                            "..." : apt.reason) : "No reason provided" }}</small>
                                    </div>
                                    <span class="badge bg-primary">{{ apt.status }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer text-center">
                        <router-link to="/doctor/appointments" class="btn btn-sm btn-primary">View
                            All Appointments</router-link>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-people"></i> My Patients</h5>
                    </div>
                    <div class="card-body">
                        <template v-if="myPatients.length">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Contact</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody v-for="patient in myPatients" :key="patient.id">
                                        <tr>
                                            <td>{{ patient.full_name }}</td>
                                            <td>{{ patient.contact }}</td>
                                            <td>
                                                <router-link :to="`/doctor/patient/${patient.id}/history`"
                                                    class="btn btn-sm btn-info">
                                                    <i class="bi bi-file-medical"></i> History
                                                </router-link>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </template>
                        <template v-else>
                            <p class="text-center text-muted mb-0">No patients yet</p>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getDoctorDashboard } from '../../src/api'
export default {
  name: "DoctorDashboard",
  data() {
    return {
      upcomingAppointments: [],
      myPatients: []
    };
  },
  async mounted() {
    try {
      const res = await getDoctorDashboard();
      this.upcomingAppointments = res.data.upcoming_appointments || [];
      this.myPatients = res.data.myPatients || [];

    } catch (error) {
      console.error("Failed to load dashboard", error);
    }
  },
  methods: {
    formatTime(time) {
      if (typeof time === "string") return time;
      const d = new Date(time);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
  }
};
</script>
