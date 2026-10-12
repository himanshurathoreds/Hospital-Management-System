<template>
    <div class="container-fluid">
        <h2 class="mb-4">
            <i class="bi bi-calendar-check"></i> My Appointments
        </h2>

        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Doctor</th>
                                <th>Specialization</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-if="appointments.length === 0">
                                <td colspan="8" class="text-center text-muted">
                                    No appointments found.
                                    <router-link to="/patient/doctor">
                                        Book your first appointment
                                    </router-link>
                                </td>
                            </tr>

                            <tr v-for="apt in appointments" :key="apt.id">
                                <td>{{ apt.id }}</td>
                                <td>Dr. {{ apt.doctor.full_name }}</td>
                                <td>{{ apt.doctor.specialization || 'N/A' }}</td>
                                <td>{{ apt.date }}</td>
                                <td>{{ formatTime(apt.time) }}</td>
                                <td>
                                    {{ apt.reason?.length > 50
                                        ? apt.reason.slice(0, 50) + "..."
                                        : apt.reason }}
                                </td>

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
                                        <button class="btn btn-sm btn-warning me-2" @click="openRescheduleModal(apt)">
                                            <i class="bi bi-arrow-repeat"></i> Reschedule
                                        </button>

                                        <button class="btn btn-sm btn-danger" @click="openCancelModal(apt)">
                                            <i class="bi bi-x-circle"></i> Cancel
                                        </button>
                                    </template>

                                    <template v-else-if="apt.status === 'Completed'">
                                        <span class="badge bg-success">
                                            <i class="bi bi-check-circle"></i> Completed
                                        </span>
                                    </template>

                                    <span v-else class="text-muted">Cancelled</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div v-if="showModal && modalType === 'delete'" class="modal fade show d-block" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form @submit.prevent="cancelAppointment">
                        <div class="modal-header">
                            <h5 class="modal-title">Cancel Appointment</h5>
                            <button type="button" class="btn-close" @click="closeModal"></button>
                        </div>

                        <div class="modal-body" v-if="modalData">
                            <p>
                                Are you sure you want to cancel your appointment with
                                Dr. {{ modalData.doctor.full_name }}
                                on {{ modalData.date }}
                                at {{ formatTime(modalData.time) }}?
                            </p>
                        </div>

                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="closeModal">
                                No, Keep It
                            </button>
                            <button type="submit" class="btn btn-danger">
                                Yes, Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div v-if="showModal && modalType === 'delete'" class="modal-backdrop fade show" @click="closeModal"></div>
        <div v-if="showModal && modalType === 'reschedule'" class="modal fade show d-block">
            <div class="modal-dialog">
                <div class="modal-content">

                    <div class="modal-header">
                        <h5 class="modal-title">Reschedule Appointment</h5>
                        <button class="btn-close" @click="closeModal"></button>
                    </div>

                    <div class="modal-body">

                        <p v-if="modalData">
                            Reschedule appointment with
                            <strong>Dr. {{ modalData.doctor.full_name }}</strong>
                        </p>

                        <select class="form-select" v-model="selectedSlot">
                            <option disabled value="">Select new slot</option>
                            <option v-for="slot in slots" :key="slot.id" :value="slot.id">
                                {{ slot.date }} - {{ formatTime(slot.time) }}
                            </option>
                        </select>

                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-secondary" @click="closeModal">
                            Cancel
                        </button>

                        <button class="btn btn-primary" @click="rescheduleAppointment">
                            Confirm
                        </button>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
    name: "Appointments",

    data() {
        return {
            selectedSlot: ""
        };
    },

    computed: {
        ...mapGetters([
            "appointments",
            "showModal",
            "modalType",
            "modalData",
            "slots"
        ])
    },

    methods: {
        openCancelModal(appointment) {
            this.$store.dispatch("openDeleteModal", appointment);
        },
        async openRescheduleModal(appointment) {
            this.$store.dispatch("openRescheduleModal", appointment);
            this.selectedSlot = "";
            await this.$store.dispatch("fetchSlots", appointment.doctor.id);
        },
        closeModal() {
            this.$store.dispatch("closeModal");
        },

        async cancelAppointment() {
            if (!this.modalData) return;

            await this.$store.dispatch("cancelAppointment", {
                id: this.modalData.id
            });
            this.closeModal();
        },

        formatTime(time) {
            return time ? time.slice(0, 5) : "";
        },

        async rescheduleAppointment() {
            if (!this.selectedSlot || !this.modalData) return;

            await this.$store.dispatch("rescheduleAppointment", {
                id: this.modalData.id,
                slot_id: this.selectedSlot
            });

            this.selectedSlot = "";
            this.closeModal();
        }
    },

    mounted() {
        this.$store.dispatch("fetchAppointments");
    }
};
</script>