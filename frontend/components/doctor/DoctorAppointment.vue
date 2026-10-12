<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-calendar-check"></i> My Appointments</h2>

        <div class="card">
            <div class="card-header">
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-primary" @click="filterStatus = 'all'">All</button>
                    <button class="btn btn-sm btn-info" @click="filterStatus = 'Booked'">Booked</button>
                    <button class="btn btn-sm btn-success" @click="filterStatus = 'Completed'">Completed</button>
                    <button class="btn btn-sm btn-secondary" @click="filterStatus = 'Cancelled'">Cancelled</button>
                </div>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Patient</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="filteredAppointments.length === 0">
                                <td colspan="7" class="text-center text-muted">No appointments found</td>
                            </tr>
                            <tr v-for="apt in filteredAppointments" :key="apt.id" :data-status="apt.status">
                                <td>{{ apt.id }}</td>
                                <td>
                                    <div>{{ apt.patient.full_name }}</div>
                                    <small class="text-muted">{{ apt.patient.contact }}</small>
                                </td>
                                <td>{{ apt.date }}</td>
                                <td>{{ formatTime(apt.time) }}</td>
                                <td>{{ apt.reason.length > 80 ? apt.reason.slice(0, 80) + "..." : apt.reason }}</td>
                                <td>
                                    <span class="badge" :class="{
                                        'bg-primary': apt.status === 'Booked',
                                        'bg-success': apt.status === 'Completed',
                                        'bg-secondary': apt.status === 'Cancelled'
                                    }">
                                        {{ apt.status }}
                                    </span>
                                </td>
                                <td>
                                    <template v-if="apt.status === 'Booked'">
                                        <button class="btn btn-sm btn-success" @click="openCompleteModal(apt)">
                                            <i class="bi bi-check-circle"></i> Complete
                                        </button>
                                        <button class="btn btn-sm btn-danger" @click="openCancelModal(apt)">
                                            <i class="bi bi-x-circle"></i> Cancel
                                        </button>
                                    </template>
                                    <template v-else-if="apt.status === 'Completed'">
                                        <router-link :to="`/doctor/patient/${apt.patient.id}/history`"
                                            class="btn btn-sm btn-info">
                                            <i class="bi bi-file-medical"></i> History
                                        </router-link>
                                    </template>
                                    <span v-else class="text-muted">No actions</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="modal" :class="{ 'show d-block': showModal && modalType === 'edit' }" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <form @submit.prevent="completeAppointment">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    Complete Appointment - {{ selectedAppointment?.patient?.full_name || '' }}
                                </h5>
                                <button type="button" class="btn-close" @click="closeModals"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Diagnosis *</label>
                                    <textarea v-model="form.diagnosis" class="form-control" rows="3"
                                        required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Prescription</label>
                                    <textarea v-model="form.prescription" class="form-control" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Notes</label>
                                    <textarea v-model="form.notes" class="form-control" rows="2"></textarea>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" @click="closeModals">Cancel</button>
                                <button type="submit" class="btn btn-success">Complete & Save Treatment</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>


            <div class="modal" :class="{ 'show d-block': showModal && modalType === 'delete' }" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form @submit.prevent="cancelAppointment">
                            <div class="modal-header">
                                <h5 class="modal-title">Cancel Appointment</h5>
                                <button type="button" class="btn-close" @click="closeModals"></button>
                            </div>
                            <div class="modal-body">
                                <p>
                                    Are you sure you want to cancel this appointment with
                                    {{ selectedAppointment?.patient?.full_name || '' }}?
                                </p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" @click="closeModals">No</button>
                                <button type="submit" class="btn btn-danger">Yes, Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            filterStatus: "all",
            selectedAppointment: null,
            form: {
                diagnosis: "",
                prescription: "",
                notes: ""
            }
        };
    },
    computed: {
        appointments() {
            return this.$store.getters.appointments;
        },
        filteredAppointments() {
            if (this.filterStatus === "all") return this.appointments;
            return this.appointments.filter(
                (apt) => apt.status === this.filterStatus
            );
        },
        showModal() {
            return this.$store.getters.showModal;
        },
        modalType() {
            return this.$store.getters.modalType;
        },
        modalData() {
            return this.$store.getters.modalData;
        }
    },
    mounted() {
        this.$store.dispatch("fetchAppointments");
    },
    methods: {
        formatTime(time) {
            if (typeof time === "string") return time;
            const date = new Date(time);
            return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        },

        openCompleteModal(apt) {
            this.selectedAppointment = apt;
            this.$store.commit('openEditModal', apt);
        },
        openCancelModal(apt) {
            this.selectedAppointment = apt;
            this.$store.commit('openDeleteModal', apt);
        },
        closeModals() {
            this.selectedAppointment = null;
            this.$store.commit('closeModal');
        },

        async completeAppointment() {
            await this.$store.dispatch("completeAppointment", {
                id: this.selectedAppointment.id,
                data: this.form
            });
            this.closeModals();
            this.$store.dispatch("fetchAppointments");
        },

        async cancelAppointment() {
            if (!this.selectedAppointment) return;
            const id = this.selectedAppointment.id;

            await this.$store.dispatch("cancelAppointment", { id });
            this.closeModals();
            this.$store.dispatch("fetchAppointments");
        },
    }
};
</script>
