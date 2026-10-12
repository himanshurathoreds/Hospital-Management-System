<template>
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-start">
            <h2 class="mb-4"><i class="bi bi-file-medical"></i> My Medical History</h2>
            <button class="btn btn-primary" @click="exportCSV" :disabled="exporting">
                <i class="fas fa-download me-2"></i>
                {{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
        </div>

        <div class="card">
            <div class="card-body">
                <div v-if="appointments.length === 0" class="text-center py-5">
                    <i class="bi bi-inbox" style="font-size: 3rem; color: #ccc;"></i>
                    <p class="text-muted mt-3">No medical history available yet.</p>
                    <router-link to="/patient/doctor" class="btn btn-primary">Book Your First
                        Appointment</router-link>
                </div>
                <div v-else class="accordion" id="historyAccordion">
                    <div v-for="(apt, index) in appointments" :key="apt.id" class="accordion-item">
                        <h2 class="accordion-header" id="heading{{ apt.id }}">
                            <button class="accordion-button" :class="{ collapsed: activeIndex !== index }" type="button"
                                @click="toggleAccordion(index)">
                                <div class="w-100 d-flex justify-content-between align-items-center pe-3">
                                    <span>
                                        <i class="bi bi-calendar3"></i> {{ apt.date }} - Dr. {{ apt.doctor.full_name }}
                                    </span>
                                    <span class="badge bg-success">Completed</span>
                                </div>
                            </button>
                        </h2>
                        <div id="collapse{{ apt.id }}" class="accordion-collapse collapse"
                            :class="{ show: activeIndex === index }">
                            <div class="accordion-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <p><strong><i class="bi bi-person-badge"></i> Doctor:</strong> Dr. {{
                                            apt.doctor.full_name }}</p>
                                        <p><strong><i class="bi bi-hospital"></i> Specialization:</strong> {{
                                            apt.doctor.specialization || 'N/A' }}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong><i class="bi bi-calendar3"></i> Date:</strong> {{ apt.date }}</p>
                                        <p><strong><i class="bi bi-clock"></i> Time:</strong> {{ formatTime(apt.time) }}
                                        </p>
                                    </div>
                                </div>

                                <hr>

                                <div class="mb-3">
                                    <h6><i class="bi bi-clipboard-pulse"></i> Reason for Visit</h6>
                                    <p>{{ apt.reason }}</p>
                                </div>

                                <template v-if="apt.treatment">
                                    <div class="mb-3">
                                        <h6><i class="bi bi-clipboard2-pulse"></i> Diagnosis</h6>
                                        <div class="alert alert-info">
                                            {{ apt.treatment.diagnosis }}
                                        </div>
                                    </div>
                                    <div v-if="apt.treatment.prescription" class="mb-3">
                                        <h6><i class="bi bi-prescription2"></i> Prescription</h6>
                                        <div class="alert alert-warning">
                                            {{ apt.treatment.prescription }}
                                        </div>
                                    </div>
                                    <div v-if="apt.treatment.notes" class="mb-3">
                                        <h6><i class="bi bi-sticky"></i> Additional Notes</h6>
                                        <p>{{ apt.treatment.notes }}</p>
                                    </div>
                                    <small class="text-muted">
                                        Treatment recorded on: {{ formatDateTime(apt.treatment.created_at) }}
                                    </small>
                                </template>
                                <template v-else>
                                    <div class="alert alert-secondary">
                                        No treatment details available for this appointment.
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getHistory, getHistoryExport } from '../../src/api';

export default {
    name: "MedicalHistory",

    data() {
        return {
            appointments: [],
            activeIndex: 0,
            exporting: false,
        };
    },

    async mounted() {
        await this.loadHistory()
    },

    methods: {
        async loadHistory() {
            try {
                const res = await getHistory();
                this.appointments = res.data;  // populate the appointments array
            } catch (err) {
                console.error(err);
                this.$store.dispatch('addMessage', {
                    message: { category: 'error', text: 'Failed to load medical history' },
                    delay: 3000
                });
            }
        },

        toggleAccordion(index) {
            this.activeIndex = this.activeIndex === index ? null : index;
        },

        formatTime(time) {
            return new Date(`1970-01-01T${time}`).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        },

        formatDateTime(datetime) {
            return new Date(datetime).toLocaleString();
        },

        async exportCSV() {
            try {
                this.exporting = true;
                const response = await getHistoryExport();
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'treatment_history.csv');
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);
                this.$store.dispatch('addMessage', {
                    message: { category: 'success', text: "CSV downloaded." },
                    delay: 3000
                });
            } catch (err) {
                console.error(err.response?.data || err);
                this.$store.dispatch('addMessage', {
                    message: { category: 'error', text: err.response?.data?.message || err.message },
                    delay: 3000
                });
            } finally {
                this.exporting = false;
            }
        }
    }
};
</script>