<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box modal-lg">
      <div class="modal-header">
        <h3>🏷️ 标签管理</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <!-- 标签页切换：整体属性 / 局部变化 -->
        <div class="label-settings-tabs">
          <button class="settings-tab" :class="{ active: labelSettingsTab === 'overall' }" @click="$emit('update:labelSettingsTab', 'overall')">
            整体属性
          </button>
          <button class="settings-tab" :class="{ active: labelSettingsTab === 'local' }" @click="$emit('update:labelSettingsTab', 'local')">
            局部变化
          </button>
        </div>
        
        <!-- 分类列表 -->
        <div class="category-editor-list">
          <div v-for="(cat, catId) in editableCategories" :key="catId" class="category-editor-card">
            <div class="category-editor-header">
              <input v-model="cat.name" class="input input-sm category-name-input" placeholder="分类名称">
              <div class="category-actions">
                <input v-if="labelSettingsTab === 'local'" type="color" v-model="cat.color" class="color-picker" title="分类颜色">
                <button class="btn-icon-danger" @click="$emit('delete-category', catId)" title="删除分类">🗑️</button>
              </div>
            </div>
            <div class="label-editor-list">
              <div v-for="(label, idx) in cat.labels" :key="label.id" class="label-editor-item">
                <input v-model="label.text" class="input input-xs label-name-input" placeholder="标签名">
                <input v-if="labelSettingsTab === 'local'" type="color" v-model="label.color" class="color-picker-sm" title="标签颜色">
                <button class="btn-icon-sm" @click="$emit('delete-label', catId, idx)" title="删除">×</button>
              </div>
              <button class="btn btn-xs btn-outline" @click="$emit('add-label', catId)">+ 添加标签</button>
            </div>
          </div>
          <button class="btn btn-primary btn-sm add-category-btn" @click="$emit('add-category')">+ 添加分类</button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn" @click="$emit('close')">取消</button>
        <button class="btn btn-primary" @click="$emit('save')">保存</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LabelSettingsModal',
  props: {
    labelSettingsTab: String,
    editableCategories: Object
  }
};
</script>
