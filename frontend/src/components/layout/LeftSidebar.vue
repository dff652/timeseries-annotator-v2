<template>
  <aside class="sidebar left-sidebar">
    <!-- 数据管理 - 合并路径和文件 -->
    <div class="panel-card">
      <div class="panel-card-header">
        <span class="panel-card-title">📁 数据管理</span>
        <button class="btn-icon-sm" @click="$emit('refresh-files')" title="刷新">🔄</button>
      </div>
      <!-- 标签页切换 -->
      <div class="file-tabs">
        <button class="file-tab" :class="{ active: fileTab === 'csv' }" @click="$emit('update:fileTab', 'csv')">📄 原始数据</button>
        <button class="file-tab" :class="{ active: fileTab === 'json' }" @click="$emit('update:fileTab', 'json')"> 标注结果</button>
      </div>
      <!-- 路径输入 -->
      <div class="path-control">
        <input type="text" :value="dataPath" @input="$emit('update:dataPath', $event.target.value)" placeholder="输入路径" class="input input-sm" @keyup.enter="$emit('set-path')">
        <button class="btn btn-primary btn-xs" @click="$emit('open-dir-browser')">📂</button>
      </div>
      <p class="current-path" v-if="currentPath">{{ currentPath }}</p>
      <div class="sort-control" v-if="fileTab === 'csv' && csvFiles.length > 0">
        <label>排序:</label>
        <select :value="fileSortBy" @change="$emit('update:fileSortBy', $event.target.value)" class="sort-select">
          <option value="name">名称</option>
          <option value="annotation">标注数</option>
        </select>
      </div>
      <!-- CSV 文件列表 -->
      <div class="file-list" v-show="fileTab === 'csv'">
        <div v-for="file in csvFiles" :key="file.name" class="file-item" :class="{ active: file.name === selectedFileName }" @click="$emit('select-file', file)">
          <span class="file-name">{{ file.name }}</span>
          <span v-if="file.has_annotations" class="file-badge" :title="`${file.annotation_count} 个标注`">✓ {{ file.annotation_count }}</span>
        </div>
        <p v-if="csvFiles.length === 0 && !loading" class="empty-message">暂无 CSV 文件</p>
      </div>
      <!-- JSON 结果文件列表 -->
      <div class="file-list" v-show="fileTab === 'json'">
        <div v-for="file in jsonFiles" :key="file.name" class="file-item" :class="{ active: file.name === selectedResultFile }" @click="$emit('load-result-file', file)">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-badge" v-if="file.annotation_count">✓</span>
        </div>
        <p v-if="jsonFiles.length === 0" class="empty-message">暂无标注结果</p>
      </div>
      <p v-if="loading" class="loading-message">加载中...</p>
    </div>

    <!-- 标签管理 -->
    <div class="panel-card">
      <div class="panel-card-header">
        <span class="panel-card-title">🏷️ 标签列表</span>
        <button class="btn btn-sm" @click="$emit('show-label-settings')">⚙️ 设置</button>
      </div>
      
      <!-- 整体属性 -->
      <details class="label-section" open>
        <summary>整体属性</summary>
        <div class="label-categories">
          <div v-for="(category, catId) in overallCategories" :key="catId" class="label-category">
            <span class="category-name">{{ category.name }}</span>
            <div class="label-options">
              <label v-for="label in category.labels" :key="label.id" class="label-option">
                <input type="radio" :name="'overall_' + catId" :value="label.id" :checked="selectedOverallLabels[catId] === label.id" @change="updateOverallLabel(catId, label.id)">
                <span>{{ label.text }}</span>
              </label>
            </div>
          </div>
          <p v-if="Object.keys(overallCategories).length === 0" class="empty-message">暂无标签</p>
        </div>
      </details>

      <!-- 局部变化 -->
      <details class="label-section" open>
        <summary>局部变化</summary>
        <div class="label-categories">
          <div v-for="(category, catId) in localCategories" :key="catId" class="label-category local-category">
            <span class="category-name" :style="{ color: getCategoryColor(catId) }">■ {{ category.name }}</span>
            <div class="local-label-options">
              <div v-for="label in category.labels" :key="label.id" 
                   class="local-label-item" 
                   :class="{ active: isLocalLabelSelected(label.id) }" 
                   :style="isLocalLabelSelected(label.id) ? { backgroundColor: getLabelColor(catId, label.id) + '22', borderColor: getLabelColor(catId, label.id) } : {}"
                   @click="$emit('toggle-local-label', label, catId)">
                <span class="label-color-dot" :style="{ backgroundColor: getLabelColor(catId, label.id) }"></span>
                <span>{{ label.text }}</span>
              </div>
            </div>
          </div>
          <p v-if="Object.keys(localCategories).length === 0" class="empty-message">暂无标签</p>
        </div>
      </details>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'LeftSidebar',
  props: {
    fileTab: String,
    dataPath: String,
    currentPath: String,
    csvFiles: Array,
    jsonFiles: Array,
    selectedFileName: String,
    selectedResultFile: String,
    loading: Boolean,
    fileSortBy: String,
    overallCategories: Object,
    localCategories: Object,
    selectedOverallLabels: Object,
    getCategoryColor: Function,
    getLabelColor: Function,
    isLocalLabelSelected: Function
  },
  methods: {
    updateOverallLabel(catId, labelId) {
      const updated = { ...this.selectedOverallLabels, [catId]: labelId };
      this.$emit('update:selectedOverallLabels', updated);
    }
  }
};
</script>
