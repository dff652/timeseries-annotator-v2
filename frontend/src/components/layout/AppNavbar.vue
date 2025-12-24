<template>
  <nav class="navbar">
    <h1 class="navbar-brand">📊 时序标注工具</h1>
    <span class="navbar-file" v-if="selectedFileName">{{ selectedFileName }}</span>
    <div class="navbar-user">
      <span class="user-name">👤 {{ currentUser }}</span>
      <button class="btn-logout" @click="logout">登出</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AppNavbar',
  props: {
    selectedFileName: {
      type: String,
      default: ''
    },
    currentUser: {
      type: String,
      default: 'User'
    }
  },
  methods: {
    logout() {
      this.$emit('logout');
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-brand { margin: 0; font-size: 1.125rem; font-weight: 600; color: #333; }
.navbar-file { color: #666; font-size: 0.875rem; margin-left: auto; margin-right: 16px; }
.navbar-user { display: flex; align-items: center; gap: 12px; }
.user-name { font-size: 0.875rem; color: #555; }
.btn-logout {
  padding: 6px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover { background: #e8e8e8; border-color: #ccc; }
</style>
