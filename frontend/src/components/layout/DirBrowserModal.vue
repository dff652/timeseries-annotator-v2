<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <h3>📂 浏览目录</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <div class="browser-toolbar">
          <button class="btn btn-sm" @click="$emit('go-to-parent')">⬆ 上级</button>
          <input type="text" :value="browsePath" @input="$emit('update:browsePath', $event.target.value)" @keyup.enter="$emit('load-directory', browsePath)" class="input">
          <button class="btn btn-sm btn-primary" @click="$emit('load-directory', browsePath)">转到</button>
        </div>
        <div class="dir-list">
          <div v-for="dir in directories" :key="dir.path" class="dir-item" :class="{ 'has-data': dir.has_data_files }" @click="$emit('load-directory', dir.path)">
            <span>📁 {{ dir.name }}</span>
            <span v-if="dir.has_data_files" class="data-badge">含数据</span>
          </div>
          <p v-if="directories.length === 0" class="empty-message">无子目录</p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn" @click="$emit('close')">取消</button>
        <button class="btn btn-primary" @click="$emit('select-current-dir')">选择</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DirBrowserModal',
  props: {
    browsePath: String,
    directories: Array
  }
};
</script>
