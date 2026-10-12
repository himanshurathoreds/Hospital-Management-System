<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-search"></i> Find Doctors</h2>

        <div class="card mb-4">
            <div class="card-header">
                <form @submit.prevent="searchDoctors" class="row g-3">
                    <div class="col-md-5">
                        <input type="text" class="form-control" placeholder="Search by doctor name..."
                            v-model="searchQuery">
                    </div>
                    <div class="col-md-5">
                        <select class="form-select" v-model="selectedSpecialization">
                            <option value="">All Specializations</option>
                            <option v-for="spec in specialization" :key="spec" :value="spec">{{ spec }}</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-primary w-100"><i class="bi bi-search"></i> Search</button>
                    </div>
                </form>
            </div>
        </div>

        <div class="row">
            <template v-if="doctors.length">
                <div class="col-md-4 mb-4" v-for="doctor in doctors" :key="doctor.id">
                    <div class="card h-100">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="bi bi-person-badge"></i> Dr. {{ doctor.full_name }}</h5>
                        </div>
                        <div class="card-body">
                            <p><strong><i class="bi bi-hospital"></i> Specialization:</strong> {{ doctor.specialization
                                || 'General' }}</p>
                            <p><strong><i class="bi bi-building"></i> Department:</strong> {{ doctor.department?.name ||
                                'N/A' }}</p>
                            <p><strong><i class="bi bi-envelope"></i> Email:</strong> {{ doctor.email }}</p>
                            <p class="mb-0"><strong><i class="bi bi-telephone"></i> Contact:</strong> {{ doctor.contact
                            }}</p>
                        </div>
                        <div class="card-footer">
                            <button @click="bookAppointment(doctor)" class="btn btn-success w-100">
                                <i class="bi bi-calendar-plus"></i> Book Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </template>
            <template v-else>
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="bi bi-info-circle"></i> No doctors found matching your criteria. Try adjusting your
                        search.
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
export default {
    data() {
        return {
            searchQuery: "",
            selectedSpecialization: "",
            specialization: [
                "Cardiology",
                "Neurology",
                "Pediatrics",
                "Orthopedics",
                "Dermatology",
                "General Medicine"
            ]
        }
    },
    computed: {
        ...mapGetters(['doctors'])
    },

    mounted() {
        this.loadDoctors()
    },
    methods: {
        ...mapActions(['fetchPatientDoctors']),

        async loadDoctors() {
            await this.fetchPatientDoctors({
                search: this.searchQuery,
                specialization: this.selectedSpecialization
            })
        },
        async searchDoctors() {
            await this.loadDoctors()
        },
        bookAppointment(doctor) {
            this.$router.push(`/patient/book/${doctor.id}`)
        }
    }
}
</script>