<template>
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-8 col-lg-6">
                <div class="card">
                    <div class="card-header text-center">
                        <h4 class="mb-0"><i class="bi bi-person-plus"></i> Patient Registration</h4>
                    </div>
                    <div class="card-body">
                        <form @submit.prevent="handleRegister">
                            <div class="row">
                                <div class="col-md-6 mb-3"><i class="bi bi-person-fill"></i><label class="form-label">Username</label><input
                                        v-model="username" type="text" class="form-control" required /></div>
                                <div class="col-md-6 mb-3"><label class="form-label"><i class="bi bi-envelope-fill"></i>Email</label><input v-model="email"
                                        type="email" class="form-control" required /></div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><i class="bi bi-lock-fill"></i><label class="form-label">Password</label><input
                                        v-model="password" type="password" class="form-control" required /></div>
                                <div class="col-md-6 mb-3"><i class="bi bi-person-vcard"></i><label class="form-label">Full Name</label><input
                                        v-model="full_name" type="text" class="form-control" /></div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3"><i class="bi bi-telephone-fill"></i><label class="form-label">Contact</label><input
                                        v-model="contact" type="text" class="form-control" /></div>
                                <div class="col-md-3 mb-3"><label class="form-label">Age</label><input v-model="age"
                                        type="number" class="form-control" /></div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Gender</label>
                                    <select v-model="gender" class="form-select">
                                        <option>Male</option>
                                        <option>Female</option>
                                        <option>Other</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3"><label class="form-label">Address</label><textarea v-model="address"
                                    class="form-control"></textarea></div>

                            <button type="submit" class="btn btn-primary w-100">Register</button>
                            <p v-if="error" class="error">{{ error }}</p>
                        </form>
                    </div>
                    <div class="card-footer text-center">
                        Already have an account?
                        <router-link to="/login">Login here</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { register } from '../../src/api'

export default {
    data() {
        return {
            username: '', email: '', password: '',
            full_name: '', contact: '', age: '', gender: '', address: '',
            error: ''
        }
    },
    methods: {
        async handleRegister() {
            try {
                await register({
                    username: this.username,
                    email: this.email,
                    password: this.password,
                    full_name: this.full_name,
                    contact: this.contact,
                    age: this.age,
                    gender: this.gender,
                    address: this.address
                })
                alert('Registration successful! Please login.')
                this.$router.push('/login')
            } catch (err) {
                this.error = err.response?.data?.message || 'Registration failed'
            }
        }
    }
}
</script>

<style scoped>
.auth-container {
    max-width: 500px;
    margin: auto;
    padding: 2rem;
}

.error {
    color: red;
    margin-top: 1rem;
}
</style>