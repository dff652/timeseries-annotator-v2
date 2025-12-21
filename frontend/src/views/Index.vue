<template>
  <BaseView class="container">
    <template v-slot:main-content>
      <div class="main-layout">
        <!-- Left Sidebar: File Browser -->
        <aside class="sidebar">
          <!-- 数据路径 -->
          <div class="panel-section">
            <h3 class="section-title">📁 数据路径</h3>
            <div class="path-input-group">
              <input 
                type="text" 
                v-model="dataPath" 
                placeholder="输入数据文件夹路径"
                class="input"
                @keyup.enter="setPath"
              >
              <button class="btn btn-primary btn-sm" @click="setPath">设置</button>
            </div>
            <p class="current-path" v-if="currentPath">当前: {{ currentPath }}</p>
          </div>

          <!-- 数据文件 -->
          <div class="panel-section">
            <div class="section-header">
              <h3 class="section-title">📄 数据文件</h3>
              <button class="btn-icon" @click="refreshFiles" title="刷新">🔄</button>
            </div>
            <div class="file-list">
              <div 
                v-for="file in files" 
                :key="file.name"
                class="file-item"
                @click="selectFile(file)"
              >
                <span class="file-name">{{ file.name }}</span>
                <span v-if="file.has_annotations" class="annotation-badge">{{ file.annotation_count }}</span>
              </div>
              <p v-if="files.length === 0 && !loading" class="empty-message">暂无数据文件</p>
              <p v-if="loading" class="loading-message">加载中...</p>
            </div>
          </div>

          <!-- 标签管理 -->
          <div class="panel-section">
            <h3 class="section-title">🏷️ 标签管理</h3>
            
            <!-- 整体属性 -->
            <details class="label-section" open>
              <summary>整体属性</summary>
              <div class="label-categories">
                <div v-for="(category, catId) in labels.overall_attribute" :key="catId" class="label-category">
                  <span class="category-name">{{ category.name }}</span>
                  <div class="label-options">
                    <label v-for="label in category.labels" :key="label.id" class="label-option">
                      <input type="radio" :name="'overall_' + catId" :value="label.id" v-model="selectedOverallLabels[catId]">
                      <span>{{ label.text }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </details>

            <!-- 局部变化 -->
            <details class="label-section" open>
              <summary>局部变化</summary>
              <div class="label-categories">
                <div v-for="(category, catId) in labels.local_change" :key="catId" class="label-category">
                  <span class="category-name">{{ category.name }}</span>
                  <div class="local-label-options">
                    <div 
                      v-for="label in category.labels" 
                      :key="label.id" 
                      class="local-label-item"
                      :class="{ active: selectedLocalLabel === label.id }"
                      @click="selectLocalLabel(label)"
                    >
                      <span class="label-color" :style="{ backgroundColor: label.color }"></span>
                      <span>{{ label.text }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </details>
          </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
          <div class="welcome-section" v-if="!selectedFileData">
            <h3 class="title">时序数据标注工具</h3>
            <p class="subtitle">Time Series Annotation Tool v2</p>
            <div class="upload-section">
              <button type="button" class="btn btn-lg btn-outline-primary upload" @click="upload">
                📤 上传CSV文件
              </button>
              <input type="file" id="upload-file" ref="fileInput" class="fileCheck" @change="fileCheck" accept=".csv">
              <p class="hint">或在左侧选择服务器上的文件</p>
            </div>
          </div>

          <!-- File Preview (when file selected from server) -->
          <div class="file-preview" v-if="selectedFileData && !navigateToLabeler">
            <h4>文件预览: {{ selectedFileName }}</h4>
            <p>数据点数: {{ selectedFileData.length }}</p>
            <button class="btn btn-primary btn-lg" @click="startLabeling">开始标注 →</button>
          </div>
        </main>

        <!-- Right Sidebar: Annotation Info -->
        <aside class="sidebar right-sidebar">
          <!-- 标注列表 -->
          <div class="panel-section">
            <div class="section-header">
              <h3 class="section-title">📝 标注列表</h3>
              <button class="btn btn-sm btn-primary" @click="downloadAnnotations" :disabled="annotations.length === 0">下载</button>
            </div>
            <div class="annotation-list">
              <div v-for="ann in annotations" :key="ann.id" class="annotation-item">
                <div class="annotation-header">
                  <span class="annotation-range" :style="{ borderLeftColor: ann.color }">{{ ann.startIndex }} - {{ ann.endIndex }}</span>
                </div>
                <div class="annotation-label">{{ ann.labelText }}</div>
              </div>
              <p v-if="annotations.length === 0" class="empty-message">暂无标注</p>
            </div>
          </div>

          <!-- 标注信息输入 -->
          <div class="panel-section annotation-form">
            <h3 class="section-title">标注信息</h3>
            
            <div class="form-group">
              <label>选区范围</label>
              <div class="selection-display">{{ selectionRange }}</div>
            </div>
            
            <div class="form-group">
              <label>输入问题 (Input Prompt)</label>
              <textarea v-model="inputPrompt" rows="3" placeholder="例如: Supposing that..."></textarea>
            </div>
            
            <div class="form-group">
              <label>专家分析 (Expert Output)</label>
              <textarea v-model="expertOutput" rows="3" placeholder="例如: Yes, the observed series..."></textarea>
            </div>
            
            <div class="form-actions">
              <button class="btn btn-primary" @click="saveAnnotation">保存标注</button>
              <button class="btn btn-success" @click="saveAndContinue">完成并继续</button>
            </div>
          </div>
        </aside>
      </div>

      <!-- Toast -->
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
    </template>
  </BaseView>
</template>

<script>
const { DateTime } = require("luxon");

const API_BASE = 'http://localhost:5000/api';

export default {
  name: 'index',
  data() {
    return {
      // Path & Files
      dataPath: '',
      currentPath: '',
      files: [],
      loading: false,
      
      // Selected file data
      selectedFileName: '',
      selectedFileData: null,
      navigateToLabeler: false,
      
      // Labels
      labels: {
        overall_attribute: {},
        local_change: {},
        custom_labels: []
      },
      selectedOverallLabels: {},
      selectedLocalLabel: '',
      selectedLocalLabelColor: '#3b82f6',
      
      // Annotations
      annotations: [],
      selectionRange: '未选择 (0 - 0)',
      inputPrompt: '',
      expertOutput: '',
      
      // Toast
      toast: { show: false, message: '', type: 'info' },
      
      // Upload error
      errorUpload: false
    }
  },
  props: {
    nextUp: Boolean
  },
  mounted() {
    this.loadLabels();
    this.loadCurrentPath();
    this.shouldUpload();
  },
  methods: {
    // API Calls
    async loadLabels() {
      try {
        const res = await fetch(`${API_BASE}/labels`);
        const data = await res.json();
        if (data.success) {
          this.labels = data.labels;
          Object.keys(this.labels.overall_attribute || {}).forEach(catId => {
            this.$set(this.selectedOverallLabels, catId, '');
          });
        }
      } catch (e) {
        console.error('Failed to load labels:', e);
      }
    },
    
    async loadCurrentPath() {
      try {
        const res = await fetch(`${API_BASE}/current-path`);
        const data = await res.json();
        if (data.success) {
          this.currentPath = data.path;
          this.dataPath = data.path;
          this.refreshFiles();
        }
      } catch (e) {
        console.error('Failed to load current path:', e);
      }
    },
    
    async setPath() {
      if (!this.dataPath) return;
      try {
        const res = await fetch(`${API_BASE}/set-path`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: this.dataPath })
        });
        const data = await res.json();
        if (data.success) {
          this.currentPath = data.path;
          this.refreshFiles();
          this.showToast('路径设置成功', 'success');
        } else {
          this.showToast(data.error || '路径设置失败', 'error');
        }
      } catch (e) {
        this.showToast('路径设置失败', 'error');
      }
    },
    
    async refreshFiles() {
      this.loading = true;
      try {
        const res = await fetch(`${API_BASE}/files`);
        const data = await res.json();
        if (data.success) {
          this.files = data.files;
        }
      } catch (e) {
        console.error('Failed to refresh files:', e);
      }
      this.loading = false;
    },
    
    async selectFile(file) {
      this.selectedFileName = file.name;
      this.loading = true;
      try {
        const res = await fetch(`${API_BASE}/data/${file.name}`);
        const data = await res.json();
        if (data.success) {
          // Convert to trainset format and navigate
          const plotDict = data.data.map((d, idx) => ({
            id: idx.toString(),
            val: d.val,
            time: DateTime.fromISO(d.time, {setZone: true}),
            series: d.series || 'value',
            label: d.label || ''
          }));
          
          const seriesList = [...new Set(plotDict.map(d => d.series))];
          
          // Navigate to labeler
          this.$router.push({
            name: 'labeler',
            params: {
              csvData: plotDict,
              filename: file.name,
              headerStr: 'series,time,val,label',
              seriesList: seriesList,
              labelList: [],
              isValid: true
            }
          });
        }
      } catch (e) {
        this.showToast('加载文件失败', 'error');
      }
      this.loading = false;
    },
    
    async loadAnnotations() {
      if (!this.selectedFileName) return;
      try {
        const res = await fetch(`${API_BASE}/annotations/${this.selectedFileName}`);
        const data = await res.json();
        if (data.success) {
          this.annotations = data.annotations.map((ann, idx) => ({
            id: ann.id || `ann_${idx}`,
            startIndex: 0,
            endIndex: 0,
            labelText: '标注',
            color: '#3b82f6',
            raw: ann
          }));
        }
      } catch (e) {
        console.error('Failed to load annotations:', e);
      }
    },
    
    async saveAnnotation() {
      // Build annotation and save
      this.showToast('请在标注界面进行操作', 'info');
    },
    
    async saveAndContinue() {
      await this.saveAnnotation();
    },
    
    async downloadAnnotations() {
      if (!this.selectedFileName) return;
      try {
        const res = await fetch(`${API_BASE}/download-annotations/${this.selectedFileName}`);
        const data = await res.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.selectedFileName}_annotations.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showToast('导出成功', 'success');
      } catch (e) {
        this.showToast('导出失败', 'error');
      }
    },
    
    selectLocalLabel(label) {
      this.selectedLocalLabel = label.id;
      this.selectedLocalLabelColor = label.color;
    },
    
    startLabeling() {
      if (this.selectedFileData) {
        const seriesList = [...new Set(this.selectedFileData.map(d => d.series))];
        this.$router.push({
          name: 'labeler',
          params: {
            csvData: this.selectedFileData,
            filename: this.selectedFileName,
            headerStr: 'series,time,val,label',
            seriesList: seriesList,
            labelList: [],
            isValid: true
          }
        });
      }
    },
    
    // Original trainset upload methods
    error() {
      this.errorUpload = true;
      this.$router.push({
        name: 'labeler',
        params: {
          csvData: [],
          minMax: [],
          filename: "",
          headerStr: "",
          isValid: false
        }
      });
    },
    
    shouldUpload() {
      if (this.nextUp === true) {
        setTimeout(() => this.upload(), 100);
      }
    },
    
    upload() {
      this.$refs.fileInput.click();
    },
    
    fileCheck() {
      window.onerror = (errorMsg, url, lineNumber) => {
        this.error();
      }
      var fileInput = document.getElementById("upload-file").files.item(0), fileText;
      var filename = fileInput.name.split('.csv')[0];
      var id = 0;
      var reader = new FileReader();
      var seriesList = new Set(), labelList = new Set(), plotDict = [], headerStr;
      reader.readAsBinaryString(fileInput);
      reader.onloadend = () => {
        fileText = $.csv.toArrays(reader.result);
        headerStr = fileText[0].toString();
        for (var i = 1; i < fileText.length; i++) {
          var dateMatches = fileText[i][1].match(/^((\d{4})-(\d{2})-(\d{2})T(\d{2})\:(\d{2})\:(\d{2})(.(\d{3}))?(([+-](\d{2})\:?(\d{2}))|Z))$/);
          var labelMatches = fileText[i][3] ? fileText[i][3].match(/^[a-zA-Z0-9_-]{0,16}$/) : [''];
          var parsedValue = Number(fileText[i][2]).toString();
          if (fileText[i].length >= 3 && (dateMatches || !isNaN(Date.parse(fileText[i][1]))) && parsedValue !== 'NaN') {
            var date = DateTime.fromISO(fileText[i][1], {setZone: true});
            if (!date.isValid) {
              date = DateTime.fromSQL(fileText[i][1]);
            }
            var series = fileText[i][0] || 'value';
            seriesList.add(series);
            if (fileText[i][3]) {
              labelList.add(fileText[i][3]);
            }
            plotDict.push({
              'id': id.toString(),
              'val': Number(parsedValue),
              'time': date,
              'series': series,
              'label': fileText[i][3] || ''
            });
            id++;
          } else {
            console.log('Parse error in line ' + (i + 1));
            // Continue with flexible parsing
          }
        }
        
        if (plotDict.length > 0) {
          seriesList = Array.from(seriesList);
          labelList = Array.from(labelList);
          
          this.$router.push({
            name: 'labeler',
            params: {
              csvData: plotDict,
              filename: filename,
              headerStr: headerStr,
              seriesList: seriesList,
              labelList: labelList,
              isValid: true
            }
          });
        } else {
          this.error();
        }
      }
    },
    
    showToast(message, type = 'info') {
      this.toast = { show: true, message, type };
      setTimeout(() => { this.toast.show = false; }, 3000);
    }
  }
};
</script>

<style scoped>
/* Layout */
.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 20px;
  min-height: calc(100vh - 100px);
  padding: 20px;
}

/* Sidebar */
.sidebar {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
  max-height: calc(100vh - 140px);
}

.right-sidebar {
  background: #f8f9fa;
}

/* Section styling */
.panel-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
}

/* Inputs */
.input, textarea, select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.input:focus, textarea:focus {
  outline: none;
  border-color: #7E4C64;
  box-shadow: 0 0 0 2px rgba(126, 76, 100, 0.1);
}

.path-input-group {
  display: flex;
  gap: 8px;
}

.path-input-group .input {
  flex: 1;
}

.current-path {
  font-size: 0.75rem;
  color: #6c757d;
  margin: 4px 0 0 0;
  word-break: break-all;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #7E4C64;
  color: white;
}

.btn-primary:hover {
  background: #6a3f54;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8125rem;
}

.btn-lg {
  padding: 12px 24px;
  font-size: 1rem;
}

.btn-outline-primary {
  background: transparent;
  border: 2px solid #7E4C64;
  color: #7E4C64;
}

.btn-outline-primary:hover {
  background: #7E4C64;
  color: white;
}

.btn-icon {
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 4px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* File List */
.file-list {
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.file-item:hover {
  background: #e9ecef;
}

.file-name {
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.annotation-badge {
  background: #7E4C64;
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
}

/* Label Sections */
.label-section {
  margin-bottom: 12px;
}

.label-section summary {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  padding: 6px 0;
}

.label-category {
  margin-bottom: 12px;
}

.category-name {
  display: block;
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 6px;
}

.label-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.label-option {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8125rem;
  cursor: pointer;
}

.local-label-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.local-label-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8125rem;
}

.local-label-item:hover {
  background: #e9ecef;
}

.local-label-item.active {
  background: #f3e8ed;
}

.label-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

/* Main Content */
.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.welcome-section {
  text-align: center;
}

.title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #6c757d;
  margin-bottom: 32px;
}

.upload-section {
  margin-top: 20px;
}

.upload {
  margin-bottom: 12px;
}

#upload-file {
  display: none;
}

.hint {
  color: #6c757d;
  font-size: 0.875rem;
}

.file-preview {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Annotations */
.annotation-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.annotation-item {
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 8px;
  background: white;
}

.annotation-header {
  display: flex;
  justify-content: space-between;
}

.annotation-range {
  font-size: 0.875rem;
  font-weight: 600;
  color: #7E4C64;
  padding-left: 8px;
  border-left: 3px solid #7E4C64;
}

.annotation-label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 4px;
}

/* Form */
.annotation-form {
  border-top: 1px solid #dee2e6;
  padding-top: 16px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 6px;
}

.selection-display {
  padding: 8px 12px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.form-actions .btn {
  flex: 1;
}

.empty-message, .loading-message {
  text-align: center;
  color: #6c757d;
  font-size: 0.875rem;
  padding: 12px;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: #343a40;
  color: white;
  border-radius: 8px;
  font-size: 0.875rem;
  z-index: 1000;
}

.toast.success {
  background: #28a745;
}

.toast.error {
  background: #dc3545;
}
</style>