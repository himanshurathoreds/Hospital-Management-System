<template>
    <div class="container-fluid">
        <h2 class="mb-4"><i class="bi bi-clock"></i> Manage Time Slots</h2>

        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Add New Slot</h5>
            </div>
            <div class="card-body">
                <form @submit.prevent="addSlot">
                    <div class="row g-3">
                        <label class="col-md-6">
                            <input type="date" v-model="slotDate" class="form-control" required />
                        </label>
                        <label class="col-md-6">
                            <input type="time" v-model="slotTime" class="form-control" required />
                        </label>
                    </div>
                    <button type="submit" class="btn btn-primary mt-3">Add Slot</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">My Slots</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="slot in slots" :key="slot.id">
                            <td>{{ slot.date }}</td>
                            <td>{{ slot.time }}</td>
                            <td>
                                <span :class="slot.available ? 'badge bg-success' : 'badge bg-secondary'">
                                    {{ slot.available ? 'Available' : 'Booked' }}
                                </span>
                            </td>
                            <td>
                                <button @click="deleteSlot(slot.id)" class="btn btn-sm btn-danger">
                                    <i class="bi bi-trash"></i> Delete
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <p v-if="slots.length === 0" class="text-center text-muted mb-0">No slots defined yet</p>
            </div>
        </div>
    </div>
</template>

<script>
import { getDoctorTime, addDoctorTime, deleteDoctorTime } from "@/api.js";

export default {
    data() {
        return {
            slots: [],
            slotDate: "",
            slotTime: ""
        };
    },
    async mounted() {
        const res = await getDoctorTime();
        this.slots = res.data;
    },
    methods: {
        async addSlot() {
            try {
                const res = await addDoctorTime({ date: this.slotDate, time: this.slotTime });
                this.$store.dispatch("addMessage", { message: { category: 'info', text: res.data.message }, delay: 3000 });
                this.slotDate = "";
                this.slotTime = "";
                const slotsRes = await getDoctorTime();
                this.slots = slotsRes.data;
            } catch (err) {
                this.$store.dispatch("addMessage", { message: { category: 'danger', text: err.response?.data?.message || "Error adding slot" }, delay: 3000 });
            }
        },
        async deleteSlot(id) {
            const res =  await deleteDoctorTime(id);
            this.$store.dispatch("addMessage", { message: { category: 'info', text: res.data.message }, delay: 3000 });
            const slotRes = await getDoctorTime();
            this.slots = slotRes.data;
        }
    }
}
</script>