<template>
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-person-badge"></i> Manage Doctors</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addDoctorModal">
                <i class="bi bi-plus-circle"></i> Add Doctor
            </button>
        </div>

        <div class="card">
            <div class="card-header">
                <form @submit.prevent="searchDoctors" class="row g-3">
                    <div class="col-md-10">
                        <input v-model="searchQuery" type="text" class="form-control" name="search"
                            placeholder="Search by name or specialization...">
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-primary w-100"><i class="bi bi-search"></i> Search</button>
                    </div>
                </form>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Contact</th>
                                <th>Specialization</th>
                                <th>Department</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody v-if="doctors.length">
                            <tr v-for="doctor in doctors" :key="doctor.id">
                                <td>{{ doctor.id }}</td>
                                <td>{{ doctor.full_name }}</td>
                                <td>{{ doctor.email }}</td>
                                <td>{{ doctor.contact }}</td>
                                <td>{{ doctor.specialization || 'N/A' }}</td>
                                <td>{{ doctor.department?.name || 'N/A' }}</td>
                                <td>
                                    <span class="badge" :class="doctor.is_active ? 'bg-success' : 'bg-secondary'">
                                        {{ doctor.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <button class=" btn btn-sm btn-warning" @click="openEditModal(doctor)">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="openDeleteModal(doctor)">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-else>
                            <tr>
                                <td>No doctors found</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="modal fade" id="addDoctorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form @submit.prevent="handleAddDoctor">
                        <div class="modal-header">
                            <h5 class="modal-title">Add New Doctor</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input v-model="newDoctor.username" type="text" class="form-control" name="username"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Full Name</label>
                                <input v-model="newDoctor.full_name" type="text" class="form-control" name="full_name"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input v-model="newDoctor.email" type="email" class="form-control" name="email"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input v-model="newDoctor.password" type="password" class="form-control" name="password"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Contact</label>
                                <input v-model="newDoctor.contact" type="text" class="form-control" name="contact"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Specialization</label>
                                <input v-model="newDoctor.specialization" type="text" class="form-control"
                                    name="specialization">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Department</label>
                                <select v-model="newDoctor.department_id" class="form-select" name="department_id">
                                    <option value="">Select Department</option>
                                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Add Doctor</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="modal fade" id="editDoctorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form @submit.prevent="handleUpdateDoctor">
                        <div class="modal-header">
                            <h5 class="modal-title">Edit Doctor</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" v-if="selectedDoctor">
                            <div class="mb-3">
                                <label class="form-label">Full Name</label>
                                <input v-model="selectedDoctor.full_name" type="text" class="form-control"
                                    name="full_name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input v-model="selectedDoctor.email" type="email" class="form-control" name="email"
                                    value="{{ doctor.email }}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Contact</label>
                                <input v-model="selectedDoctor.contact" type="text" class="form-control" name="contact"
                                    value="{{ doctor.contact }}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Specialization</label>
                                <input v-model="selectedDoctor.specialization" type="text" class="form-control"
                                    name="specialization" value="{{ doctor.specialization }}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Department</label>
                                <select v-model="selectedDoctor.department_id" class="form-select" name="department_id">
                                    <option value="">Select Department</option>
                                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                        {{ dept.name }}</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">New Password (leave blank to keep current)</label>
                                <input v-model="selectedDoctor.password" type="password" class="form-control"
                                    name="password">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Update Doctor</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="modal fade" id="deleteDoctorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form @submit.prevent="handleDeleteDoctor">
                        <div class="modal-header">
                            <h5 class="modal-title">Confirm Delete</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to deactivate <strong>Dr. {{ selectedDoctor?.full_name }}</strong>
                            </p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-danger">Deactivate</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { addAdminDoctor, updateAdminDoctor, deleteAdminDoctor } from "@/api";
import { mapActions, mapGetters } from 'vuex';
export default {
    data() {
        return {
            searchQuery: "",
            newDoctor: {
                username: "",
                full_name: "",
                email: "",
                password: "",
                contact: "",
                specialization: "",
                department_id: ""
            },
            selectedDoctor: null
        }
    },
    computed: {
        ...mapGetters(['doctors', 'departments'])
    },

    mounted() {
        this.fetchDoctors();
    },
    methods: {
        ...mapActions(['fetchDoctors']),

        async searchDoctors() {
            await this.fetchDoctors({
                search : this.searchQuery
            })
        },        
        async handleAddDoctor() {
            await addAdminDoctor(this.newDoctor)
            await this.fetchDoctors();
            this.resetNewDoctor()
            bootstrap.Modal.getInstance(document.getElementById("addDoctorModal")).hide()
        },
        resetNewDoctor() {
            this.newDoctor = {
                username: "",
                full_name: "",
                email: "",
                password: "",
                contact: "",
                specialization: "",
                department_id: ""
            }
        },

        async handleUpdateDoctor() {
            await updateAdminDoctor(this.selectedDoctor.id, this.selectedDoctor);
            await this.fetchDoctors();
            bootstrap.Modal.getInstance(document.getElementById("editDoctorModal")).hide();
        },

        async handleDeleteDoctor() {
            await deleteAdminDoctor(this.selectedDoctor.id);
            await this.fetchDoctors();
            bootstrap.Modal.getInstance(document.getElementById("deleteDoctorModal")).hide();
        },

        openEditModal(doctor) {
            this.selectedDoctor = { ...doctor };
            new bootstrap.Modal(document.getElementById("editDoctorModal")).show();
        },
        openDeleteModal(doctor) {
            this.selectedDoctor = doctor;
            new bootstrap.Modal(document.getElementById("deleteDoctorModal")).show();
        }
    }
}

</script>