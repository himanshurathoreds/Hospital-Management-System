<template>
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-6 col-lg-4">
                <div class="card">
                    <div class="card-header text-center">
                        <h4 class="mb-0"><i class="bi bi-hospital"></i> Hospital Login</h4>
                    </div>
                    <div class="card-body">
                        <form @submit.prevent="handleLogin">
                            <div class="mb-3">
                                <label class="form-label"><i class="bi bi-person-fill"></i>Username</label>
                                <input v-model="username" type="text" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><i class="bi bi-lock-fill"></i>Password</label>
                                <input v-model="password" type="password" class="form-control" required />
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                            <p v-if="error" class="error">{{ error }}</p>
                        </form>
                    </div>
                    <div class="card-footer text-center" style="margin: 15px">
                        Don’t have an account? <router-link to="/register">Register here</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { login } from '../../src/api'
import { mapActions } from 'vuex'

export default {
    data() {
        return {
            username: '',
            password: '',
            error: ''
        }
    },
    methods: {
        ...mapActions(['login', 'addMessage']), // Use the Vuex login action
        async handleLogin() {
            try {
                const res = await login(this.username, this.password)

                // Update Vuex state using single login action
                this.login({
                    token: res.data.access_token,
                    full_name: res.data.user,
                    role: res.data.role
                })
                this.addMessage({ message: {category: 'success', text: res.data.message}, delay: 3000 })

                // Redirect based on role
                if (res.data.role === 'admin') this.$router.push('/admin/dashboard')
                else if (res.data.role === 'doctor') this.$router.push('/doctor/dashboard')
                else this.$router.push('/patient/dashboard')
            } catch (err) {
                this.addMessage({ message: {category: 'danger', text: err.response?.data?.message || 'Login failed'}, delay: 3000 })
            }
        }
    }
}
</script>
