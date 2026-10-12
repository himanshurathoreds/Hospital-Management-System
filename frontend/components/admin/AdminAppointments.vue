<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-calendar-check"></i> All Appointments</h2>

        <div class="card">
            <div class="card-header">
                <div class="row">
                    <div class="col-md-12">
                        <button class="btn btn-sm btn-primary" @click="filterStatus = 'all'">All</button>
                        <button class="btn btn-sm btn-info" @click="filterStatus = 'Booked'">Booked</button>
                        <button class="btn btn-sm btn-success" @click="filterStatus = 'Completed'">Completed</button>
                        <button class="btn btn-sm btn-secondary" @click="filterStatus = 'Cancelled'">Cancelled</button>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover" id="appointmentsTable">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Patient</th>
                                <th>Doctor</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Reason</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="filteredAppointments.length === 0">
                                <td colspan="7" class="text-center text-muted">No appointments found</td>
                            </tr>
                            <tr v-for="apt in filteredAppointments" :key="apt.id" :data-status="apt.status">
                                <td>{{ apt.id }}</td>
                                <td>{{ apt.patient.full_name }}</td>
                                <td>Dr. {{ apt.doctor.full_name }}</td>
                                <td>{{ apt.date }}</td>
                                <td>{{ formatTime(apt.time) }}</td>
                                <td>{{ apt.reason.length > 50 ? apt.reason.slice(0, 50) + "..." : apt.reason }}</td>
                                <td>
                                    <span class="badge" :class="{
                                        'bg-primary': apt.status === 'Booked', 'bg-success': apt.status === 'Completed',
                                        'bg-secondary': apt.status === 'Cancelled'}">
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
export default {
    data() {
        return {
            filterStatus: "all",
        };
    },
    computed: {
        appointments() {
            return this.$store.getters.appointments
        },
        filteredAppointments() {
            if (this.filterStatus === 'all') return this.appointments
            return this.appointments.filter(
                apt => apt.status === this.filterStatus
            )
        }
    },
    mounted() {
        this.$store.dispatch('fetchAppointments')
    },
    methods: {
        formatTime(time) {
            if (typeof time === "string") return time;
            const date = new Date(time);
            return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        },
    },
};

</script>
