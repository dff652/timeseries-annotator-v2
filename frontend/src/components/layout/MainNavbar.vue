<template>
  <nav class="navbar">
    <h1 class="navbar-brand">📊 时序标注工具</h1>
    <span class="navbar-file" v-if="selectedFileName">{{ selectedFileName }}</span>
    <div class="navbar-user">
      <span class="user-name">👤 {{ currentUser }}</span>
      <button class="btn-logout" @click="$emit('logout')">登出</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'MainNavbar',
  props: {
    selectedFileName: String,
    currentUser: String
  }
};
</script>
