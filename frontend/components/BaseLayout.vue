<template>
  <div class="app">
    <!-- Navbar -->
    <nav v-if="currentUser.is_authenticated" class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="">
          <i class="bi bi-hospital"></i> Hospital MS
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <!-- Admin view -->
            <template v-if="currentUser.role === 'admin'">
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/dashboard"><i class="bi bi-speedometer2"></i>
                  Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/doctor"><i class="bi bi-person-badge"></i>
                  Doctors</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/patient"><i class="bi bi-people"></i> Patients</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/appointments"><i class="bi bi-calendar-check"></i>
                  Appointments</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/departments"><i class="bi bi-building"></i>
                  Departments</router-link>
              </li>
            </template>

            <!-- Doctor View -->
            <template v-else-if="currentUser.role === 'doctor'">
              <li class="nav-item">
                <router-link class="nav-link" to="/doctor/dashboard"><i class="bi bi-speedometer2"></i>
                  Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/doctor/appointments"><i class="bi bi-calendar-check"></i>
                  Appointments</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/doctor/timeslots"><i class="bi bi-clock"></i>
                  Time Slot</router-link>
              </li>
            </template>

            <!-- Patient View -->
            <template v-else-if="currentUser.role === 'patient'">
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/dashboard"><i class="bi bi-speedometer2"></i>
                  Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/doctor"><i class="bi bi-search"></i> Find
                  Doctors</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/appointments"><i class="bi bi-calendar-check"></i> My
                  Appointments</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/history"><i class="bi bi-file-medical"></i> Medical
                  History</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/profile"><i class="bi bi-person-circle"></i>
                  Profile</router-link>
              </li>
            </template>
          </ul>

          <ul class="navbar-nav">
            <li class="nav-item dropdown">
              <router-link class="nav-link dropdown-toggle" to="#" id="navbarDropdown" role="button"
                data-bs-toggle="dropdown">
                <i class="bi bi-person-circle"></i> {{ currentUser.full_name }}
              </router-link>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <span class="dropdown-item-text">
                    <small>Role: {{ currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1) }}</small>
                  </span>
                </li>
                <li>
                  <hr class="dropdown-divider">
                </li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right"></i> Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Alerts -->
    <div class="container-fluid" style="margin: 15px 0 0 0">
      <div v-for="(msg, index) in messages" :key="index" class="alert alert-dismissible fade show"
        :class="`alert-${msg.category}`" role="alert">
        {{ msg.text }}
        <button type="button" class="btn-close" @click="removeMessage(index)"></button>
      </div>
    </div>

    <!-- Page content -->
    <div class="main-content">
      <div class="container-fluid">
        <router-view />
      </div>
    </div>

    <!-- Footer -->
    <footer class="text-center mt-5">
      <div class="container">
        <p class="mb-0">&copy; 2025 Hospital Management System. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapGetters({
      currentUser: 'currentUser',
      messages: 'messages'
    })
  },

  methods: {
    ...mapActions(['addMessage', 'removeMessage']),
    logout() {
      this.$store.dispatch('logout')
      this.addMessage({ message: {category: 'info', text: 'You have been logged out.' },delay: 3000 })
      this.$router.push('/login')
    }
  }
}
</script>
