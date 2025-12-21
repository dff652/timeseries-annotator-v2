<template>
  <div class="app-container">
    <!-- Navbar -->
    <nav class="navbar">
      <h1 class="navbar-brand">📊 时序标注工具</h1>
      <span class="navbar-file" v-if="selectedFileName">{{ selectedFileName }}</span>
    </nav>
    
    <!-- Main Layout -->
    <div class="main-layout" :class="{ 'no-file': !isChartMode }">
      <!-- Left Sidebar -->
      <aside class="sidebar left-sidebar">
        <!-- 数据管理 - 合并路径和文件 -->
        <div class="panel-card">
          <div class="panel-card-header">
            <span class="panel-card-title">📁 数据管理</span>
            <button class="btn-icon-sm" @click="refreshFiles" title="刷新">🔄</button>
          </div>
          <!-- 标签页切换 -->
          <div class="file-tabs">
            <button class="file-tab" :class="{ active: fileTab === 'csv' }" @click="fileTab = 'csv'">📄 原始数据</button>
            <button class="file-tab" :class="{ active: fileTab === 'json' }" @click="fileTab = 'json'">� 标注结果</button>
          </div>
          <!-- 路径输入 -->
          <div class="path-input-group">
            <input type="text" v-model="dataPath" placeholder="输入路径" class="input input-sm" @keyup.enter="setPath">
            <button class="btn btn-primary btn-xs" @click="openDirBrowser">📂</button>
          </div>
          <p class="current-path" v-if="currentPath">{{ currentPath }}</p>
          <!-- CSV 文件列表 -->
          <div class="file-list" v-show="fileTab === 'csv'">
            <div v-for="file in csvFiles" :key="file.name" class="file-item" :class="{ active: file.name === selectedFileName }" @click="selectFile(file)">
              <span class="file-name">{{ file.name }}</span>
            </div>
            <p v-if="csvFiles.length === 0 && !loading" class="empty-message">暂无 CSV 文件</p>
          </div>
          <!-- JSON 结果文件列表 -->
          <div class="file-list" v-show="fileTab === 'json'">
            <div v-for="file in jsonFiles" :key="file.name" class="file-item" :class="{ active: file.name === selectedResultFile }" @click="loadResultFile(file)">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-badge" v-if="file.annotation_count">✓</span>
            </div>
            <p v-if="jsonFiles.length === 0" class="empty-message">暂无标注结果</p>
          </div>
          <input type="file" ref="fileInput" @change="fileCheck" accept=".csv" style="display:none">
          <p v-if="loading" class="loading-message">加载中...</p>
        </div>

        <!-- 标签管理 -->
        <div class="panel-card">
          <div class="panel-card-header">
            <span class="panel-card-title">🏷️ 标签管理</span>
            <button class="btn-icon-sm" @click="showLabelSettings = true" title="设置">⚙️</button>
          </div>
          
          <!-- 整体属性 -->
          <details class="label-section" open>
            <summary>整体属性</summary>
            <div class="label-categories">
              <div v-for="(category, catId) in overallCategories" :key="catId" class="label-category">
                <span class="category-name">{{ category.name }}</span>
                <div class="label-options">
                  <label v-for="label in category.labels" :key="label.id" class="label-option">
                    <input type="radio" :name="'overall_' + catId" :value="label.id" v-model="selectedOverallLabels[catId]">
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
                       :style="isLocalLabelSelected(label.id) ? { backgroundColor: getCategoryColor(catId) + '22', borderColor: getCategoryColor(catId) } : {}"
                       @click="toggleLocalLabel(label, catId)">
                    <span>{{ label.text }}</span>
                  </div>
                </div>
              </div>
              <p v-if="Object.keys(localCategories).length === 0" class="empty-message">暂无标签</p>
            </div>
          </details>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Welcome Page -->
        <div class="welcome-section" v-if="!isChartMode">
          <h2 class="title">时序数据标注工具</h2>
          <p class="subtitle">Time Series Annotation Tool v2</p>
          <button class="btn btn-lg btn-primary" @click="$refs.fileInput.click()">📤 上传CSV文件</button>
          <input type="file" ref="fileInput" @change="fileCheck" accept=".csv" style="display:none">
          <p class="hint">或在左侧选择服务器上的文件</p>
        </div>
        
        <!-- Chart Area -->
        <div class="chart-area" v-show="isChartMode">
          <!-- Hover Info -->
          <div id="hoverbox">
            <div id="hoverinfo" class="hover-card" style="display: none;">
              <div>时间: {{ hoverinfo.time }}</div>
              <div>数值: {{ hoverinfo.val }}</div>
              <div>标签: {{ hoverinfo.label }}</div>
            </div>
          </div>
          
          <!-- D3 Chart Container -->
          <div id="maindiv"></div>

          <!-- Instructions & Toolbar -->
          <div class="toolbar" v-if="isChartMode" id="instrSelect">
            <div class="toolbar-section instr">
              <strong>标注操作</strong><br>
              <strong>点击</strong> 切换标签<br>
              <strong>拖拽</strong> 框选批量标注<br>
              <kbd>Shift</kbd> + 拖拽 取消标注
            </div>
            <div class="toolbar-section instr">
              <strong>导航</strong><br>
              <kbd>←</kbd><kbd>→</kbd> 平移<br>
              <kbd>↑</kbd><kbd>↓</kbd> 缩放
            </div>
            <div class="toolbar-section selectors" id="selectors">
              <div>主序列: <select id="seriesSelect"></select></div>
              <div>参考序列: <select id="referenceSelect"></select></div>
            </div>
            <div class="toolbar-section actions">
              <button class="btn btn-warning btn-sm" @click="clearAllLabels">清除标注</button>
              <button class="btn btn-success btn-sm" @click="exportAnnotations">导出</button>
            </div>
          </div>
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="sidebar right-sidebar" v-if="isChartMode">
        <!-- 标注列表 -->
        <div class="panel-section">
          <div class="section-header">
            <h3 class="section-title">📝 标注列表</h3>
            <button class="btn btn-sm btn-primary" @click="downloadAnnotations" :disabled="annotations.length === 0">下载</button>
          </div>
          <div class="annotation-list">
            <div v-for="(ann, idx) in annotations" :key="idx" class="annotation-item">
              <div class="annotation-header">
                <span class="annotation-range">{{ ann.startIndex }} - {{ ann.endIndex }}</span>
                <button class="btn-delete" @click="deleteAnnotation(idx)">×</button>
              </div>
              <div class="annotation-labels">
                <span v-for="label in ann.labels" :key="label.id" class="label-tag" :style="{ backgroundColor: label.color }">{{ label.text }}</span>
              </div>
            </div>
            <p v-if="annotations.length === 0" class="empty-message">暂无标注</p>
          </div>
        </div>

        <!-- 标注信息 -->
        <div class="panel-section annotation-form">
          <h3 class="section-title">标注信息</h3>
          <div class="form-group">
            <label>选区范围</label>
            <div class="selection-display">{{ selectionRange }}</div>
          </div>
          <div class="form-group">
            <label>已选标签</label>
            <div class="selected-labels">
              <span v-for="label in selectedLocalLabels" :key="label.id" class="label-tag" :style="{ backgroundColor: label.color }">{{ label.text }}</span>
              <span v-if="selectedLocalLabels.length === 0" class="no-label">未选择</span>
            </div>
          </div>
          <div class="form-group">
            <label>输入问题</label>
            <textarea v-model="inputPrompt" rows="2" placeholder="Supposing that..."></textarea>
          </div>
          <div class="form-group">
            <label>专家分析</label>
            <textarea v-model="expertOutput" rows="2" placeholder="Yes, the..."></textarea>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="saveAnnotation" :disabled="!canSave">保存</button>
            <button class="btn btn-success" @click="saveAndContinue" :disabled="!canSave">完成</button>
          </div>
        </div>
      </aside>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
    
    <!-- Directory Browser Modal -->
    <div v-if="showDirBrowser" class="modal-overlay" @click.self="showDirBrowser = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>📂 浏览目录</h3>
          <button class="close-btn" @click="showDirBrowser = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="browser-toolbar">
            <button class="btn btn-sm" @click="goToParentDir">⬆ 上级</button>
            <input type="text" v-model="browsePath" @keyup.enter="loadDirectory(browsePath)" class="input">
            <button class="btn btn-sm btn-primary" @click="loadDirectory(browsePath)">转到</button>
          </div>
          <div class="dir-list">
            <div v-for="dir in directories" :key="dir.path" class="dir-item" :class="{ 'has-data': dir.has_data_files }" @click="loadDirectory(dir.path)">
              <span>📁 {{ dir.name }}</span>
              <span v-if="dir.has_data_files" class="data-badge">含数据</span>
            </div>
            <p v-if="directories.length === 0" class="empty-message">无子目录</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showDirBrowser = false">取消</button>
          <button class="btn btn-primary" @click="selectCurrentDir">选择</button>
        </div>
      </div>
    </div>
    
    <!-- Add Label Modal -->
    <div v-if="showAddLabelModal" class="modal-overlay" @click.self="showAddLabelModal = false">
      <div class="modal-box modal-sm">
        <div class="modal-header">
          <h3>添加标签</h3>
          <button class="close-btn" @click="showAddLabelModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <input type="text" v-model="newLabelName" placeholder="输入标签名称" class="input" @keyup.enter="addLabel">
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showAddLabelModal = false">取消</button>
          <button class="btn btn-primary" @click="addLabel">添加</button>
        </div>
      </div>
    </div>
    
    <!-- Hidden triggers for D3 -->
    <button id="updateHover" style="display:none" @click="updateHoverinfo"></button>
    <button id="triggerReplot" style="display:none" @click="triggerReplot"></button>
    <button id="triggerRecolor" style="display:none" @click="triggerRecolor"></button>
    <button id="clearSeries" style="display:none" @click="clearSeries"></button>
  </div>
</template>

<script>
import * as LabelerD3 from "@/assets/js/LabelerD3.js"
const { DateTime } = require("luxon");

const API_BASE = 'http://192.168.199.126:5000/api';
var plottingApp = {};
// Expose to window for D3 access and debugging
window.plottingApp = plottingApp;

// Color palette for labels
const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#3b82f6', '#8b5cf6', '#ec4899'];
let colorIndex = 0;

export default {
  name: 'Index',
  data() {
    return {
      // Path & Files
      dataPath: '',
      currentPath: '',
      files: [],
      loading: false,
      selectedFileName: '',
      isChartMode: false,
      
      // Labels
      labels: { overall_attribute: {}, local_change: {} },
      selectedOverallLabels: {},
      selectedLocalLabels: [],
      
      // Chart labels
      selectedLabel: '',
      optionsList: [],
      newLabelName: '',
      
      // Hover info
      hoverinfo: { val: '', time: '', label: '' },
      
      // Annotations
      annotations: [],
      selectionRange: '未选择 (0 - 0)',
      currentSelection: { start: 0, end: 0 },
      inputPrompt: '',
      expertOutput: '',
      
      // UI state
      toast: { show: false, message: '', type: 'info' },
      showDirBrowser: false,
      showAddLabelModal: false,
      showLabelSettings: false,
      browsePath: '',
      parentPath: '',
      directories: [],
      fileTab: 'csv',  // 'csv' or 'json'
      selectedResultFile: '',
      
      // Category colors for local changes - each major category gets one color
      categoryColors: {
        'outlier': '#ef4444',
        'level_shift': '#3b82f6',
        'concept_drift': '#22c55e',
        'seasonal': '#f59e0b',
        'trend': '#8b5cf6',
        'default': '#6b7280'
      }
    }
  },
  computed: {
    overallCategories() {
      // API returns { categories: {...}, name: '...' }, access the categories sub-object
      const attr = this.labels.overall_attribute || {};
      return attr.categories || attr;  // Fallback to attr if no categories wrapper
    },
    localCategories() {
      // API returns { categories: {...}, name: '...' }, access the categories sub-object
      const attr = this.labels.local_change || {};
      return attr.categories || attr;  // Fallback to attr if no categories wrapper
    },
    canSave() {
      return this.currentSelection.start !== this.currentSelection.end || this.selectedLocalLabels.length > 0;
    },
    // Filter files for CSV tab
    csvFiles() {
      return this.files.filter(f => f.name.toLowerCase().endsWith('.csv'));
    },
    // Filter files for JSON results
    jsonFiles() {
      return this.files.filter(f => f.name.toLowerCase().endsWith('.json') || f.has_annotations);
    }
  },
  watch: {
    selectedLabel(val) {
      if (plottingApp) plottingApp.selectedLabel = val;
    }
  },
  mounted() {
    this.loadLabels();
    this.loadCurrentPath();
  },
  methods: {
    // API Methods
    async loadLabels() {
      try {
        console.log('Loading labels from:', `${API_BASE}/labels`);
        const res = await fetch(`${API_BASE}/labels`);
        const data = await res.json();
        console.log('Labels API response:', data);
        if (data.success) {
          this.labels = data.labels;
          console.log('Loaded labels - overall:', Object.keys(this.labels.overall_attribute || {}));
          console.log('Loaded labels - local:', Object.keys(this.labels.local_change || {}));
          // Initialize selected labels
          Object.keys(this.labels.overall_attribute || {}).forEach(catId => {
            this.$set(this.selectedOverallLabels, catId, '');
          });
        } else {
          console.error('Labels API error:', data.error);
        }
      } catch (e) {
        console.error('Failed to load labels:', e);
      }
    },
    
    async loadCurrentPath() {
      try {
        const res = await fetch(`${API_BASE}/current-path`);
        const data = await res.json();
        if (data.success && data.path) {
          this.currentPath = data.path;
          this.dataPath = data.path;
          this.refreshFiles();
        }
      } catch (e) {
        console.error('Failed to load path:', e);
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
          this.showToast(data.error || '设置失败', 'error');
        }
      } catch (e) {
        this.showToast('设置失败', 'error');
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
        console.error('Failed to load files:', e);
      }
      this.loading = false;
    },
    
    // Load JSON annotation result file for review/edit
    async loadResultFile(file) {
      this.selectedResultFile = file.name;
      this.showToast('加载标注结果: ' + file.name, 'info');
      // TODO: Implement actual JSON loading logic
      // This would load the annotations and overlay them on the chart
    },
    
    async selectFile(file) {
      console.log('selectFile called:', file.name);
      this.selectedFileName = file.name;
      this.loading = true;
      try {
        const url = `${API_BASE}/data/${file.name}`;
        console.log('Fetching:', url);
        const res = await fetch(url);
        console.log('Response status:', res.status);
        const data = await res.json();
        console.log('Response data success:', data.success, 'data length:', data.data?.length);
        if (data.success && data.data && data.data.length > 0) {
          const plotDict = data.data.map((d, idx) => ({
            id: idx.toString(),
            val: parseFloat(d.val),
            time: d.time,
            series: d.series || 'value',
            label: d.label || ''
          }));
          const seriesList = [...new Set(plotDict.map(d => d.series))];
          console.log('Calling initChart with', plotDict.length, 'points');
          this.initChart(plotDict, file.name, seriesList, []);
        } else {
          this.showToast('加载失败: ' + (data.error || '无数据'), 'error');
        }
      } catch (e) {
        console.error('selectFile error:', e);
        this.showToast('加载文件失败: ' + e.message, 'error');
      }
      this.loading = false;
    },
    
    // Chart Initialization
    initChart(csvData, filename, seriesList, labelList) {
      // Switch to chart mode first so DOM renders
      this.isChartMode = true;
      
      // Use nextTick to ensure DOM is rendered before D3 draws
      this.$nextTick(() => {
        // Clear previous chart
        const maindiv = document.getElementById('maindiv');
        if (maindiv) maindiv.innerHTML = '';
        
        // Setup plottingApp with data
        plottingApp.filename = filename;
        plottingApp.csvData = csvData;
        plottingApp.seriesList = seriesList;
        plottingApp.labelList = labelList.length > 0 ? labelList : ['label_1'];
        
        // CRITICAL: Pre-set selectedSeries before D3 initialization
        plottingApp.selectedSeries = seriesList[0] || 'value';
        plottingApp.refSeries = seriesList.length > 1 ? seriesList[1] : seriesList[0];
        
        // Setup selectors in DOM
        this.setupSelectors(seriesList);
        
        // Map labels to colors
        this.optionsList = plottingApp.labelList.map(l => ({ name: l, color: this.getNextColor() }));
        plottingApp.labelList = this.optionsList;
        this.selectedLabel = this.optionsList[0].name;
        
        // Draw chart with slight delay to ensure container has width
        setTimeout(() => {
          try {
            LabelerD3.drawLabeler(plottingApp);
          } catch (e) {
            console.error('Chart draw error:', e);
            this.showToast('图表绘制失败: ' + e.message, 'error');
          }
        }, 100);
      });
    },
    
    setupSelectors(seriesList) {
      const seriesSelect = document.getElementById('seriesSelect');
      const refSelect = document.getElementById('referenceSelect');
      if (!seriesSelect || !refSelect) return;
      
      seriesSelect.innerHTML = '';
      refSelect.innerHTML = '';
      
      seriesList.forEach(s => {
        seriesSelect.innerHTML += `<option value="${s}">${s}</option>`;
        refSelect.innerHTML += `<option value="${s}">${s}</option>`;
      });
      
      if (seriesList.length === 1) {
        document.getElementById('selectors').style.display = 'none';
      } else {
        document.getElementById('selectors').style.display = 'block';
      }
    },
    
    getNextColor() {
      const color = COLORS[colorIndex % COLORS.length];
      colorIndex++;
      return color;
    },
    
    // Label Methods - Single select for local labels
    toggleLocalLabel(label, categoryId) {
      // Single select: clicking same label removes it, clicking different replaces
      const idx = this.selectedLocalLabels.findIndex(l => l.id === label.id);
      if (idx > -1) {
        // Clicked same label - deselect
        this.selectedLocalLabels = [];
      } else {
        // Clicked different label - replace with single selection
        // Use category color, not label's individual color
        const categoryColor = this.getCategoryColor(categoryId);
        this.selectedLocalLabels = [{
          id: label.id,
          text: label.text,
          color: categoryColor,
          categoryId,
          categoryName: this.localCategories[categoryId]?.name
        }];
        
        // Update D3 chart with this color
        if (plottingApp && plottingApp.selectedLabel !== undefined) {
          plottingApp.selectedLabel = label.text;
          plottingApp.labelColor = categoryColor;
        }
      }
    },
    
    isLocalLabelSelected(labelId) {
      return this.selectedLocalLabels.some(l => l.id === labelId);
    },
    
    getCategoryColor(categoryId) {
      // Return color for category - each major category gets one color
      return this.categoryColors[categoryId] || this.categoryColors['default'];
    },
    
    addLabel() {
      if (!this.newLabelName || this.optionsList.some(l => l.name === this.newLabelName)) {
        this.showToast('标签名无效或已存在', 'error');
        return;
      }
      this.optionsList.push({ name: this.newLabelName, color: this.getNextColor() });
      plottingApp.labelList = this.optionsList;
      this.selectedLabel = this.newLabelName;
      this.newLabelName = '';
      this.showAddLabelModal = false;
    },
    
    removeLabel() {
      if (this.optionsList.length <= 1) return;
      const idx = this.optionsList.findIndex(l => l.name === this.selectedLabel);
      if (idx > -1) {
        this.optionsList.splice(idx, 1);
        plottingApp.labelList = this.optionsList;
        this.selectedLabel = this.optionsList[0].name;
      }
    },
    
    // Annotation Methods
    saveAnnotation() {
      if (!this.canSave) return;
      this.annotations.push({
        startIndex: this.currentSelection.start,
        endIndex: this.currentSelection.end,
        labels: [...this.selectedLocalLabels],
        input: this.inputPrompt,
        output: this.expertOutput,
        overallLabels: { ...this.selectedOverallLabels }
      });
      this.showToast('标注已保存', 'success');
    },
    
    saveAndContinue() {
      this.saveAnnotation();
      this.selectedLocalLabels = [];
      this.inputPrompt = '';
      this.expertOutput = '';
      this.currentSelection = { start: 0, end: 0 };
      this.selectionRange = '未选择 (0 - 0)';
    },
    
    deleteAnnotation(idx) {
      this.annotations.splice(idx, 1);
    },
    
    downloadAnnotations() {
      const exportData = {
        annotations: this.annotations,
        export_time: new Date().toISOString(),
        filename: this.selectedFileName
      };
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `annotations_${this.selectedFileName.replace('.csv', '')}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    exportAnnotations() {
      this.downloadAnnotations();
    },
    
    clearAllLabels() {
      if (confirm('确定清除所有标注吗？')) {
        if (plottingApp.allData) {
          plottingApp.allData.forEach(d => d.label = '');
        }
        this.triggerRecolor();
      }
    },
    
    // File Upload
    fileCheck(e) {
      const file = e.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const lines = reader.result.split('\n');
          const plotDict = [];
          const seriesSet = new Set();
          
          for (let i = 1; i < lines.length; i++) {
            const cols = lines[i].split(',');
            if (cols.length >= 3) {
              const val = parseFloat(cols[2]);
              if (!isNaN(val)) {
                const series = cols[0] || 'value';
                seriesSet.add(series);
                plotDict.push({
                  id: (i-1).toString(),
                  val,
                  time: DateTime.fromISO(cols[1], { setZone: true }),
                  series,
                  label: cols[3] || ''
                });
              }
            }
          }
          
          if (plotDict.length > 0) {
            this.selectedFileName = file.name;
            this.initChart(plotDict, file.name, Array.from(seriesSet), []);
          } else {
            this.showToast('文件解析失败', 'error');
          }
        } catch (err) {
          this.showToast('文件解析错误', 'error');
        }
      };
      reader.readAsText(file);
    },
    
    // Directory Browser
    openDirBrowser() {
      this.showDirBrowser = true;
      this.browsePath = this.currentPath || '/home';
      this.loadDirectory(this.browsePath);
    },
    
    async loadDirectory(path) {
      try {
        const res = await fetch(`${API_BASE}/browse-dir?path=${encodeURIComponent(path)}`);
        const data = await res.json();
        if (data.success) {
          this.browsePath = data.current_path;
          this.parentPath = data.parent_path || '';
          this.directories = data.directories || [];
        }
      } catch (e) {
        console.error('Failed to load directory:', e);
      }
    },
    
    goToParentDir() {
      if (this.parentPath) this.loadDirectory(this.parentPath);
    },
    
    async selectCurrentDir() {
      this.dataPath = this.browsePath;
      await this.setPath();
      this.showDirBrowser = false;
    },
    
    // D3 Triggers
    updateHoverinfo() {
      this.hoverinfo = { ...plottingApp.hoverinfo };
    },
    
    triggerReplot() {
      // Trigger chart replot
    },
    
    triggerRecolor() {
      // Trigger point recolor
    },
    
    clearSeries() {
      if (plottingApp.allData) {
        plottingApp.allData.filter(d => d.series === plottingApp.selectedSeries).forEach(d => d.label = '');
      }
    },
    
    // Utilities
    showToast(message, type = 'info') {
      this.toast = { show: true, message, type };
      setTimeout(() => { this.toast.show = false; }, 3000);
    }
  }
};
</script>

<style>
/* Global D3 Styles */
svg { font: 10px sans-serif; display: block; margin: auto; overflow: visible; }
#maindiv { width: 100%; text-align: left; }
.line { fill: none; stroke: black; stroke-width: 1.5px; clip-path: url(#clip); pointer-events: none; }
.point { fill: black; stroke: none; clip-path: url(#clip); }
.axis path, .axis line { fill: none; stroke: #000; shape-rendering: crispEdges; }
.loader { position: fixed; left: 50%; top: 30%; transform: translateX(-50%); border: 8px solid #f3f3f3; border-top: 8px solid #7E4C64; border-radius: 50%; width: 60px; height: 60px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: translateX(-50%) rotate(0deg); } 100% { transform: translateX(-50%) rotate(360deg); } }
kbd { display: inline-block; border: 1px solid #ccc; border-radius: 4px; padding: 0.1em 0.4em; background: #f7f7f7; font-size: 0.75em; }
</style>

<style scoped>
/* App Container */
.app-container { min-height: 100vh; background: #f5f5f5; }

/* Navbar */
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: #7E4C64; color: white; }
.navbar-brand { margin: 0; font-size: 1.1rem; font-weight: 600; }
.navbar-actions { display: flex; gap: 8px; }
.nav-btn { background: white; border: none; color: #7E4C64; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: 500; font-size: 0.875rem; }
.nav-btn:hover { background: #f0f0f0; }

/* Layout */
.main-layout { display: grid; grid-template-columns: 280px 1fr 300px; gap: 16px; padding: 16px; min-height: calc(100vh - 60px); }
.main-layout.no-file { grid-template-columns: 280px 1fr; }

/* Sidebar */
.sidebar { background: white; border-radius: 8px; padding: 10px; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

/* Panel Cards */
.panel-card { border: 1px solid #e0e0e0; border-radius: 6px; padding: 10px; margin-bottom: 10px; background: #fafafa; }
.panel-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.panel-card-title { font-size: 0.8125rem; font-weight: 600; color: #333; }
.btn-icon-sm { background: none; border: none; cursor: pointer; font-size: 0.875rem; padding: 2px; opacity: 0.7; }
.btn-icon-sm:hover { opacity: 1; }

/* Legacy section styles */
.panel-section { margin-bottom: 12px; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-title { margin: 0 0 8px; font-size: 0.8125rem; font-weight: 600; color: #333; }
.subsection-title { font-size: 0.8125rem; font-weight: 600; color: #666; margin: 12px 0 8px; }

/* Inputs */
.input, textarea, select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.875rem; }
.input:focus, textarea:focus { outline: none; border-color: #7E4C64; }
.path-input-group { display: flex; gap: 6px; }
.path-input-group .input { flex: 1; min-width: 0; }
.current-path { font-size: 0.75rem; color: #888; margin: 4px 0 0; word-break: break-all; }

/* Buttons */
.btn { padding: 8px 16px; border: none; border-radius: 6px; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #7E4C64; color: white; }
.btn-primary:hover { background: #6a3f54; }
.btn-success { background: #22c55e; color: white; }
.btn-sm { padding: 6px 12px; font-size: 0.8125rem; }
.btn-lg { padding: 12px 24px; font-size: 1rem; }
.btn-icon { background: none; border: none; font-size: 1rem; cursor: pointer; padding: 4px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-delete { background: none; border: none; color: #ef4444; font-size: 1.2rem; cursor: pointer; }
.add-btn, .delete-btn { background: #eee; border: 1px solid #ddd; width: 28px; height: 28px; border-radius: 4px; font-size: 1.2rem; cursor: pointer; }

/* File List */
.file-list { max-height: 180px; overflow-y: auto; }
.file-item { padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8125rem; }
.file-item:hover { background: #f0f0f0; }
.file-item.active { background: #d4edda; }

/* Labels */
.label-section { margin-bottom: 12px; }
.label-section summary { font-weight: 600; cursor: pointer; padding: 6px 0; }
.label-category { margin: 8px 0; padding-left: 8px; }
.category-name { display: block; font-size: 0.75rem; color: #888; margin-bottom: 4px; }
.label-options { display: flex; flex-wrap: wrap; gap: 6px; }
.label-option { display: flex; align-items: center; gap: 4px; font-size: 0.8125rem; cursor: pointer; }
.local-label-options { display: flex; flex-direction: column; gap: 4px; }
.local-label-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8125rem; }
.local-label-item:hover { background: #f0f0f0; }
.local-label-item.active { background: #f3e8ed; }
.label-color { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.label-select-group { display: flex; align-items: center; gap: 4px; }
.label-select { flex: 1; min-width: 0; }

/* Main Content */
.main-content { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-height: 400px; display: flex; flex-direction: column; }
.welcome-section { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.title { font-size: 2rem; color: #333; margin-bottom: 8px; }
.subtitle { color: #888; margin-bottom: 24px; }
.hint { color: #888; font-size: 0.875rem; margin-top: 16px; }
.chart-area { flex: 1; }

/* Toolbar (instructions + actions) */
.toolbar { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 16px; margin-top: 16px; font-size: 0.8125rem; align-items: start; }
.toolbar-section { padding: 12px; background: #f8f8f8; border-radius: 6px; }
.toolbar-section.instr { line-height: 1.6; }
.toolbar-section.selectors select { margin-left: 8px; }
.toolbar-section.actions { display: flex; gap: 8px; flex-direction: column; }

/* File Tabs */
.file-tabs { display: flex; gap: 0; margin-bottom: 8px; border-bottom: 1px solid #eee; }
.file-tab { flex: 1; padding: 8px 4px; background: transparent; border: none; border-bottom: 2px solid transparent; cursor: pointer; font-size: 0.8125rem; color: #666; transition: all 0.2s; }
.file-tab:hover { color: #7E4C64; background: #f8f4f6; }
.file-tab.active { color: #7E4C64; border-bottom-color: #7E4C64; font-weight: 600; }

/* File Badge */
.file-badge { color: #22c55e; font-weight: bold; margin-left: 4px; }

/* Navbar File Name */
.navbar-file { color: rgba(255,255,255,0.8); font-size: 0.875rem; margin-left: auto; }

/* Legacy compatibility */
.instructions { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px; font-size: 0.8125rem; }
.instr-col { padding: 12px; background: #f8f8f8; border-radius: 6px; }
.selectors select { margin-left: 8px; }

/* Hover Card */
#hoverbox { position: relative; float: right; z-index: 5; }
.hover-card { position: absolute; right: 20px; top: 10px; background: white; border: 1px solid #ddd; border-radius: 6px; padding: 10px; font-size: 0.8125rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

/* Annotations */
.annotation-list { max-height: 200px; overflow-y: auto; margin-bottom: 16px; }
.annotation-item { padding: 10px; border: 1px solid #eee; border-radius: 6px; margin-bottom: 8px; }
.annotation-header { display: flex; justify-content: space-between; align-items: center; }
.annotation-range { font-weight: 600; color: #7E4C64; padding-left: 8px; border-left: 3px solid #7E4C64; }
.annotation-labels { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.label-tag { font-size: 0.7rem; color: white; padding: 2px 6px; border-radius: 4px; }
.selected-labels { display: flex; flex-wrap: wrap; gap: 4px; min-height: 28px; padding: 6px 8px; border: 1px solid #eee; border-radius: 6px; }
.no-label { color: #aaa; font-size: 0.8125rem; }
.annotation-form { border-top: 1px solid #eee; padding-top: 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 0.75rem; font-weight: 600; color: #888; margin-bottom: 4px; }
.selection-display { padding: 8px; background: #f8f8f8; border-radius: 6px; font-family: monospace; font-size: 0.875rem; }
.form-actions { display: flex; gap: 8px; }
.form-actions .btn { flex: 1; }

/* Toast */
.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); padding: 12px 24px; background: #333; color: white; border-radius: 8px; z-index: 9999; }
.toast.success { background: #22c55e; }
.toast.error { background: #ef4444; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: white; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); max-width: 600px; width: 90%; max-height: 80vh; display: flex; flex-direction: column; }
.modal-sm { max-width: 360px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #eee; }
.modal-header h3 { margin: 0; font-size: 1.1rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #888; }
.modal-body { padding: 16px 20px; overflow-y: auto; flex: 1; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 20px; border-top: 1px solid #eee; }
.browser-toolbar { display: flex; gap: 8px; margin-bottom: 16px; }
.browser-toolbar .input { flex: 1; }
.dir-list { border: 1px solid #eee; border-radius: 6px; min-height: 200px; max-height: 300px; overflow-y: auto; }
.dir-item { display: flex; justify-content: space-between; padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #f0f0f0; }
.dir-item:hover { background: #f8f8f8; }
.dir-item.has-data { background: #f0fff4; }
.data-badge { background: #22c55e; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }
.empty-message { text-align: center; color: #888; padding: 12px; font-size: 0.875rem; }
</style>