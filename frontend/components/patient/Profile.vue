<template>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <h2 class="mb-4"><i class="bi bi-person-circle"></i> My Profile</h2>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Edit Profile Information</h5>
                    </div>
                    <div class="card-body">
                        <form @submit.prevent="updateProfile">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Full Name *</label>
                                    <input type="text" class="form-control" v-model="form.full_name" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Email *</label>
                                    <input type="email" class="form-control" v-model="form.email" required>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Contact Number *</label>
                                    <input type="text" class="form-control" v-model="form.contact" required>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Age</label>
                                    <input type="number" class="form-control" v-model="form.age">
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Gender</label>
                                    <select v-model="form.gender" class="form-select">
                                        <option value="">Select</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Address</label>
                                <textarea v-model="form.address" class="form-control" rows="3"></textarea>
                            </div>

                            <hr>

                            <h6 class="mb-3"><i class="bi bi-key"></i> Change Password (Optional)</h6>
                            <div class="mb-3">
                                <label class="form-label">New Password</label>
                                <input v-model="form.password" type="password" class="form-control"
                                    placeholder="Leave blank to keep current password">
                                <small class="form-text text-muted">Only fill this if you want to change your
                                    password</small>
                            </div>

                            <hr>

                            <div class="mb-3">
                                <h6>Account Information</h6>
                                <p class="mb-1"><strong>Username:</strong> {{ user.username }}</p>
                                <p class="mb-1"><strong>Account Created:</strong> {{ user.created_at || '' }}</p>
                                <p class="mb-0"><strong>Status:</strong>
                                    <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-secondary'">
                                        {{ user.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </p>
                            </div>

                            <button type="submit" class="btn btn-primary w-100">
                                <i class="bi bi-save"></i> Update Profile
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getPatientProfile, updatePatientProfile } from "../../src/api"

export default {
    name: "MyProfile",

    data() {
        return {
            user: {},
            form: {
                full_name: "",
                email: "",
                contact: "",
                age: "",
                gender: "",
                address: "",
                password: ""
            }
        };
    },

    methods: {
        async fetchProfile() {
            try {
                const response = await getPatientProfile();
                this.user = response.data;

                this.form = {
                    ...this.form,
                    ...response.data,
                    password: ""
                };
            } catch (error) {
                console.error(error);
            }
        },

        async updateProfile() {
            try {
                const res = await updatePatientProfile(this.form);
                this.form.password = "";
                this.$store.dispatch('addMessage',{message: {category: 'success', text: res.data.message}, delay: 3000})
                this.user = { ...this.user, ...this.form }
            } catch (error) {
                console.log(error.response?.data?.error)
                this.$store.dispatch('addMessage', {message: {category: 'danger', text: error.response?.data?.error || 'Profile update failed'}, delay: 3000})
            }
        }
    },

    mounted() {
        this.fetchProfile();
    }
};
</script>