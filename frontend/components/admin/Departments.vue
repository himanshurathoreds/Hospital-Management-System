<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-building"></i> Manage Departments</h2>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addDepartmentModal">
        <i class="bi bi-plus-circle"></i> Add Department
      </button>
    </div>

    <div class="row">
      <template v-if="departments.length">
        <div v-for="dept in departments" :key="dept.id" class="col-md-4 mb-3">
          <div class="card h-100">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-hospital"></i> {{ dept.name }}</h5>
            </div>
            <div class="card-body">
              <p class="card-text">{{ dept.description || 'No description available' }}</p>
              <hr>
              <p class="mb-0"><strong>Doctors:</strong> {{ dept.doctors?.length || 0 }}</p>
              <p class="text-muted mb-0">
                <small>Created: {{ formatDate(dept.created_at) }}</small>
              </p>
            </div>
            <div class="card-footer">
              <small class="text-muted">
                <template v-if="dept.doctors && dept.doctors.length">
                  <span v-for="(doctor, index) in dept.doctors.slice(0,3)" :key="doctor.id">
                    Dr. {{ doctor.full_name }}<span v-if="index < dept.doctors.slice(0,3).length - 1">, </span>
                  </span>
                  <span v-if="dept.doctors.length > 3">...</span>
                </template>
                <template v-else>
                  No doctors assigned
                </template>
              </small>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="col-12">
        <div class="alert alert-info text-center">
          <i class="bi bi-info-circle"></i> No departments found. Add one to get started.
        </div>
      </div>
    </div>

    <!-- Add Department Modal -->
    <div class="modal fade" id="addDepartmentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <form @submit.prevent="handleAddDepartment">
            <div class="modal-header">
              <h5 class="modal-title">Add New Department</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Department Name</label>
                <input type="text" class="form-control" v-model="newDepartment.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="newDepartment.description" rows="3"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Add Department</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { addAdminDepartments } from "@/api";

export default {
  data() {
    return {
      newDepartment: {
        name: "",
        description: ""
      }
    };
  },
  computed: {
    ...mapGetters(["departments"])
  },
  mounted() {
    this.fetchDepartments();
  },
  methods: {
    ...mapActions(["fetchDepartments"]),

    async handleAddDepartment() {
      await addAdminDepartments(this.newDepartment);
      await this.fetchDepartments();
      this.newDepartment = { name: "", description: "" };
      bootstrap.Modal.getInstance(document.getElementById("addDepartmentModal")).hide();
    },
    formatDate(dateStr) {
      if (!dateStr) return "";
      const d = new Date(dateStr);
      return d.toISOString().split("T")[0]; // YYYY-MM-DD
    }
  }
};
</script>