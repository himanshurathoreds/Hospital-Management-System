<template>
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-people"></i> Manage Patients</h2>
        </div>

        <div class="card">
            <div class="card-header">
                <form @submit.prevent="searchPatients" class="row g-3">
                    <div class="col-md-10">
                        <input v-model="searchQuery" type="text" class="form-control" name="search"
                            placeholder="Search by name, email or contact...">
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
                                <th>Age</th>
                                <th>Gender</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody v-if="patients.length">
                            <tr v-for="patient in patients" :key="patient.id">
                                <td>{{ patient.id }}</td>
                                <td>{{ patient.full_name }}</td>
                                <td>{{ patient.email }}</td>
                                <td>{{ patient.contact }}</td>
                                <td>{{ patient.age || 'N/A' }}</td>
                                <td>{{ patient.gender || 'N/A' }}</td>
                                <td>
                                    <span class="badge" :class="patient.is_active ? 'bg-success' : 'bg-secondary'">
                                        {{ patient.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-warning" @click="handleEdit(patient)">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="handleDelete(patient)">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-else>
                            <tr>
                                <td colspan="8" class="text-center text-muted">No patients found</td>
                            </tr>
                        </tbody>
                    </table>
                    <div v-if="showModal && modalType === 'edit'" class="modal d-block" style="background: rgba(0,0,0,0.5)" id="editPatientModal"
                        tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <form @submit.prevent="adminEditPatient">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Edit Patient</h5>
                                        <button @click="closeModal" type="button" class="btn-close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">Full Name</label>
                                            <input v-model="selectedPatient.full_name" type="text" class="form-control"
                                                name="full_name" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input v-model="selectedPatient.email" type="email" class="form-control"
                                                name="email" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Contact</label>
                                            <input v-model="selectedPatient.contact" type="text" class="form-control"
                                                name="contact" required>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Age</label>
                                                <input v-model="selectedPatient.age" type="number" class="form-control"
                                                    name="age">
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Gender</label>
                                                <select v-model="selectedPatient.gender" class="form-select"
                                                    name="gender">
                                                    <option value="">Select</option>
                                                    <option value="Male">Male</option>
                                                    <option value="Female">Female</option>
                                                    <option value="Other">Other</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Address</label>
                                            <textarea v-model="selectedPatient.address" class="form-control"
                                                name="address" rows="2"></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary"
                                            @click="closeModal">Cancel</button>
                                        <button type="submit" class="btn btn-primary">Update Patient</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div v-if="showModal && modalType === 'delete'" class="modal d-block" style="background: rgba(0,0,0,0.5)" id="deletePatientModal"
                        tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <form @submit.prevent="adminDeletePatient">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Confirm Delete</h5>
                                        <button type="button" class="btn-close" @click="closeModal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <p>Are you sure you want to deactivate {{ selectedPatient.full_name }}?
                                        </p>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary"
                                            @click="closeModal">Cancel</button>
                                        <button type="submit" class="btn btn-danger">Deactivate</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
    data() {
        return {
            searchQuery: "",
            selectedPatient: {
                full_name: "",
                email: "",
                contact: "",
                age: null,
                gender: "",
                address: ""
            }
        }
    },
    computed: {
        ...mapGetters(['patients', 'showModal', 'modalType', 'modalData'])
    },

    mounted() {
        this.fetchPatients();
    },
    methods: {
        ...mapActions(['fetchPatients', 'updatePatient', 'deletePatient', "openEditModal", "openDeleteModal", "closeModal"]),

        async searchPatients() {
            await this.fetchPatients({
                search: this.searchQuery
            })
        },
        handleClose() {
            this.closeModal();
        },
        handleEdit(patient) {
            this.selectedPatient = { ...patient };
            this.openEditModal(patient);
        },
        handleDelete(patient) {
            this.selectedPatient = { ...patient };
            this.openDeleteModal(patient);
        },
        async adminEditPatient() {
            await this.updatePatient(this.selectedPatient);
            await this.fetchPatients();
            this.closeModal();
        },
        async adminDeletePatient() {
            await this.deletePatient(this.selectedPatient);
            await this.fetchPatients();
            this.closeModal();
        },
    }
}
</script>