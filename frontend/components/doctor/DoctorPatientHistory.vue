<template>
    <div class="container-fluid">
        <div class="mb-4">
            <router-link to="/doctor/dashboard" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Back to Dashboard
            </router-link>
        </div>

        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card" v-if="patient">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-person"></i> Patient Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <p><strong>Name:</strong> {{ patient.full_name }}</p>
                            </div>
                            <div class="col-md-3">
                                <p><strong>Email:</strong> {{ patient.email }}</p>
                            </div>
                            <div class="col-md-2">
                                <p><strong>Contact:</strong> {{ patient.contact }}</p>
                            </div>
                            <div class="col-md-2">
                                <p><strong>Age:</strong> {{ patient.age || 'N/A' }}</p>
                            </div>
                            <div class="col-md-2">
                                <p><strong>Gender:</strong> {{ patient.gender || 'N/A' }}</p>
                            </div>
                        </div>
                        <p v-if="patient.address" class="mb-0"><strong>Address:</strong> {{ patient.address }}</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-file-medical"></i> Treatment History</h5>
            </div>
            <div class="card-body">
                <template v-if="filteredAppointments.length">
                    <div class="accordion" id="treatmentAccordion">
                        <div class="accordion-item" v-for="(apt, index) in filteredAppointments" :key="apt.id">
                            <h2 class="accordion-header">
                                <button class="accordion-button" :class="{ collapsed: index !== 0 }" type="button"
                                    data-bs-toggle="collapse" :data-bs-target="'#collapse' + apt.id">
                                    <div class="w-100 d-flex justify-content-between align-items-center pe-3">
                                        <span>
                                            <i class="bi bi-calendar3"></i> {{ formatDate(apt.date) }} at {{
                                                formatTime(apt.time) }}
                                        </span>
                                        <span class="badge bg-success">Completed</span>
                                    </div>
                                </button>
                            </h2>
                            <div :id="'collapse' + apt.id" class="accordion-collapse collapse"
                                :class="{ show: index === 0 }" data-bs-parent="#treatmentAccordion">
                                <div class="accordion-body">
                                    <div class="row">
                                        <div class="col-md-12 mb-3">
                                            <h6><i class="bi bi-clipboard-pulse"></i> Reason for Visit</h6>
                                            <p>{{ apt.reason }}</p>
                                        </div>
                                    </div>

                                    <template v-if="apt.treatment">
                                        <div class="row">
                                            <div class="col-md-12 mb-3">
                                                <h6><i class="bi bi-clipboard2-pulse"></i> Diagnosis</h6>
                                                <p>{{ apt.treatment.diagnosis }}</p>
                                            </div>
                                        </div>

                                        <div class="row" v-if="apt.treatment.prescription">
                                            <div class="col-md-12 mb-3">
                                                <h6><i class="bi bi-prescription2"></i> Prescription</h6>
                                                <p>{{ apt.treatment.prescription }}</p>
                                            </div>
                                        </div>

                                        <div class="row" v-if="apt.treatment.notes">
                                            <div class="col-md-12 mb-3">
                                                <h6><i class="bi bi-sticky"></i> Notes</h6>
                                                <p>{{ apt.treatment.notes }}</p>
                                            </div>
                                        </div>

                                        <small class="text-muted">
                                            Recorded on: {{ formatDateTime(apt.treatment.created_at) }}
                                        </small>
                                    </template>
                                    <template v-else>
                                        <p class="text-muted">No treatment details recorded.</p>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
                <template v-else>
                    <p class="text-center text-muted mb-0">No treatment history available for this patient.</p>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import { getPatientHistory } from '../../src/api'

export default {
    data() {
        return {
        patient: null,
        filteredAppointments: [],
        loading: true,
        error: null
        }
    },
    async mounted() {
        const patientId = this.$route.params.id
        try {
        const res = await getPatientHistory(patientId)
        this.patient = res.data.patient
        this.filteredAppointments = res.data.appointments.map(apt => ({
            ...apt,
            treatment: apt.treatment || null
        }))
        } catch (err) {
        console.error(err)
        this.error = 'Failed to load patient history'
        } finally {
        this.loading = false
        }
    },
    methods: {
        formatDate(dateStr) {
            return dateStr
        },
        formatTime(time) {
            return time;
        },
        formatDateTime(dateTimeStr) {
            if (!dateTimeStr) return 'N/A'
            return new Date(dateTimeStr).toLocaleString()
        }
    }
}
</script>