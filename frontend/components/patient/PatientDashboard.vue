<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-speedometer2"></i> Patient Dashboard</h2>

        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-calendar-check"></i> Upcoming Appointments</h5>
                    </div>
                    <div class="card-body">
                        <template v-if="upcoming_appointments.length">
                            <div class="row">
                                <div class="col-md-6 mb-3" v-for="apt in upcoming_appointments" :key="apt.id">
                                    <div class="card border-primary">
                                        <div class="card-body">
                                            <h6 class="card-title">Dr. {{ apt.doctor.full_name }}</h6>
                                            <p class="mb-1"><i class="bi bi-calendar3"></i> <strong>Date:</strong> {{
                                                apt.date }}</p>
                                            <p class="mb-1"><i class="bi bi-clock"></i> <strong>Time:</strong> {{
                                                apt.time }}</p>
                                            <p class="mb-1"><i class="bi bi-hospital"></i>
                                                <strong>Specialization:</strong>
                                                {{ apt.doctor.specialization || 'N/A' }}
                                            </p>
                                            <p class="mb-1"><i class="bi bi-file-text"></i> <strong>Reason:</strong>
                                                {{ apt.reason?.length > 80 ? apt.reason.slice(0, 80) + "..." : apt.reason}}</p>
                                            <span class="badge bg-primary">{{ apt.status }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="text-center mt-3">
                                <router-link to="/patient/appointments" class="btn btn-primary">View All Appointments</router-link>
                            </div>
                        </template>
                        <template v-else>
                            <p class="text-center text-muted mb-0">No upcoming appointments. Book one now!</p>
                            <div class="text-center mt-3">
                                <router-link to="/patient/doctor" class="btn btn-primary">Book Appointment</router-link>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-building"></i> Available Departments</h5>
                    </div>
                    <div class="card-body">
                        <template v-if="departments.length">
                            <div class="row">
                                <div class="col-md-4 mb-3" v-for="dept in departments" :key="dept.id">
                                    <div class="card h-100 border-info">
                                        <div class="card-body">
                                            <h6 class="card-title"><i class="bi bi-hospital"></i> {{ dept.name }}</h6>
                                            <p class="card-text">{{ dept.description || 'No description available' }}</p>
                                            <p class="mb-0"><small class="text-muted">Doctors: {{ dept.doctors?.length || 0}}</small></p>
                                        </div>
                                        <div class="card-footer">
                                            <router-link to="/patient/doctor" class="btn btn-sm btn-info w-100">Find Doctors</router-link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <p class="text-center text-muted mb-0">No departments available at the moment.</p>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import { getPatientDashboard } from "../../src/api";
import { mapState } from "vuex";

export default {
  computed: {
    ...mapState(["appointments", "departments"]),

    upcoming_appointments() {
      return this.appointments || [];
    }
  },

  async mounted() {
    await this.fetchPatientDashboard();
  },

  methods: {
    async fetchPatientDashboard() {
      try {
        const { data } = await getPatientDashboard();

        this.$store.commit("setDepartments", data.departments || []);
        this.$store.commit("setAppointments", data.upcoming_appointments || []);

      } catch (error) {
        console.error("Failed to fetch dashboard", error);
      }
    }
  }
};
</script>



