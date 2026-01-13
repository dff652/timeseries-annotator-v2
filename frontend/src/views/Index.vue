<template>
  <div class="app-container">
    <MainNavbar 
      :selectedFileName="selectedFileName" 
      :currentUser="currentUser" 
      @logout="logout" 
    />
    
    <div class="main-layout" :class="{ 'no-file': !isChartMode }">
      <LeftSidebar 
        :fileTab.sync="fileTab"
        :dataPath.sync="dataPath"
        :currentPath="currentPath"
        :csvFiles="csvFiles"
        :jsonFiles="jsonFiles"
        :selectedFileName="selectedFileName"
        :selectedResultFile="selectedResultFile"
        :loading="loading"
        :fileSortBy.sync="fileSortBy"
        :overallCategories="overallCategories"
        :localCategories="localCategories"
        :selectedOverallLabels.sync="selectedOverallLabels"
        :getCategoryColor="getCategoryColor"
        :getLabelColor="getLabelColor"
        :isLocalLabelSelected="isLocalLabelSelected"
        @refresh-files="loadFiles"
        @set-path="setDataPath"
        @open-dir-browser="showDirBrowser = true"
        @select-file="selectFile"
        @load-result-file="loadResultFile"
        @show-label-settings="showLabelSettings = true"
        @toggle-local-label="toggleLocalLabel"
      />

      <!-- Center Panel -->
      <chart-area
        :is-chart-mode="isChartMode"
        :chart-data="chartData"
        :filename="selectedFileName"
        :series-list="seriesList"
        :label-list="labelList"
        :selected-label="activeChartLabel"
        :label-color="activeLabelColor"
        :selection-stats="selectionStats"
        :format-number="formatNumber"
        @upload-click="$refs.fileInput.click()"
        @selection-update="onSelectionUpdate"
        @hover-update="updateHoverinfo"
        @data-version-inc="chartDataVersion++"
        @clear-labels="clearAllLabels"
        @clear-series="clearSeries"
      />

      <RightSidebar 
        v-if="isChartMode"
        :isChartMode="isChartMode"
        :chartLabelStats="chartLabelStats"
        :activeChartLabel="activeChartLabel"
        :activeSegments="activeSegments"
        :activeLabelColor="activeLabelColor"
        :currentAnnotation.sync="currentAnnotation"
        :canSaveCurrentAnnotation="canSaveCurrentAnnotation"
        :editingAnnotationIndex="editingAnnotationIndex"
        :savedAnnotations="savedAnnotations"
        @select-chart-label="selectChartLabel"
        @clear-label-from-chart="clearLabelFromChart"
        @navigate-to-segment="navigateToSegment"
        @remove-segment-by-range="removeSegmentByRange"
        @save-active-label="saveActiveLabel"
        @reset-current-annotation="resetCurrentAnnotation"
        @save-server="saveAnnotationsToServer"
        @download="downloadAnnotations"
        @cycle-segments="cycleAnnotationSegments"
        @edit-annotation="editAnnotation"
        @delete-annotation="deleteAnnotation"
        @navigate-ann-segment="navigateToAnnotationSegment"
      />
    </div>

    <!-- Hidden inputs/triggers -->
    <input type="file" ref="fileInput" @change="fileCheck" accept=".csv" style="display:none">


    <!-- Modals -->
    <DirBrowserModal 
      v-if="showDirBrowser"
      :browsePath.sync="browsePath"
      :directories="directories"
      @close="showDirBrowser = false"
      @go-to-parent="goToParentDir"
      @load-directory="loadDirectory"
      @select-current-dir="selectCurrentDir"
    />

    <LabelSettingsModal 
      v-if="showLabelSettings"
      :labelSettingsTab.sync="labelSettingsTab"
      :editableCategories="editableCategories"
      @close="showLabelSettings = false"
      @add-category="addCategory"
      @delete-category="deleteCategory"
      @add-label="addLabelToCategory"
      @delete-label="deleteLabelFromCategory"
      @save="saveLabelsToServer"
    />

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script>
import * as LabelerD3 from "@/assets/js/LabelerD3.js"
import { dataService } from '@/api/dataService'
import { transformForD3 } from '@/utils/dataTransform'
import * as labelUtils from '@/utils/labelUtils'
import MainNavbar from '@/components/layout/MainNavbar.vue'
import LeftSidebar from '@/components/layout/LeftSidebar.vue'
import RightSidebar from '@/components/layout/RightSidebar.vue'
import ChartArea from '@/components/layout/ChartArea.vue'
import DirBrowserModal from '@/components/layout/DirBrowserModal.vue'
import LabelSettingsModal from '@/components/layout/LabelSettingsModal.vue'

const { DateTime } = require("luxon");

var plottingApp = {};
window.plottingApp = plottingApp;

export default {
  name: 'Index',
  components: {
    MainNavbar,
    LeftSidebar,
    RightSidebar,
    ChartArea,
    DirBrowserModal,
    LabelSettingsModal
  },
  data() {
    return {
      currentUser: localStorage.getItem('name') || localStorage.getItem('username') || 'User',
      dataPath: '',
      currentPath: '',
      files: [],
      loading: false,
      selectedFileName: '',
      isChartMode: false,
      chartData: [],
      seriesList: [],
      labelList: [],
      labels: { overall_attribute: {}, local_change: {} },
      selectedOverallLabels: {},
      hoverinfo: { val: '', time: '', label: '' },
      currentAnnotation: { label: null, segments: [], prompt: '', expertOutput: '' },
      savedAnnotations: [],
      selectionStats: null,
      chartDataVersion: 0,
      annotationVersion: 0,
      toast: { show: false, message: '', type: 'info' },
      showDirBrowser: false,
      showLabelSettings: false,
      browsePath: '',
      parentPath: '',
      directories: [],
      fileTab: 'csv',
      fileSortBy: 'name',
      selectedResultFile: '',
      labelSettingsTab: 'overall',
      editingAnnotationIndex: null,
      annotationCyclePositions: {},
      activeChartLabel: null,
      categoryColors: {
        'outlier': '#ef4444', 'level_shift': '#3b82f6', 'concept_drift': '#22c55e',
        'seasonal': '#f59e0b', 'trend': '#8b5cf6', 'spike': '#ef4444',
        'step': '#22c55e', 'drift': '#3b82f6', 'anomaly': '#a855f7', 'default': '#6b7280'
      }
    }
  },
  computed: {
    overallCategories() { return this.labels.overall_attribute || {}; },
    localCategories() { return this.labels.local_change || {}; },
    canSaveCurrentAnnotation() {
      return (this.activeChartLabel && this.activeSegments.length > 0) || 
             (this.currentAnnotation.prompt || '').trim() || 
             (this.currentAnnotation.expertOutput || '').trim();
    },
    csvFiles() {
      const filtered = this.files.filter(f => f.name.toLowerCase().endsWith('.csv'));
      return this.sortFiles(filtered, this.fileSortBy);
    },
    jsonFiles() {
      return this.files.filter(f => f.name.toLowerCase().endsWith('.json') || f.has_annotations);
    },
    editableCategories() {
      return this.labelSettingsTab === 'overall' ? this.overallCategories : this.localCategories;
    },
    chartLabelStats() {
      const _v = this.chartDataVersion;
      if (!window.plottingApp || !window.plottingApp.allData) return [];
      const stats = {};
      window.plottingApp.allData.forEach(d => {
        if (d.label) {
          if (!stats[d.label]) stats[d.label] = { text: d.label, count: 0, color: null };
          stats[d.label].count++;
        }
      });
      return Object.values(stats).map(s => {
        const labelEntry = window.plottingApp.labelList?.find(l => l.name === s.text);
        s.color = labelEntry?.color || '#7E4C64';
        return s;
      });
    },
    activeSegments() {
      const _v = this.chartDataVersion;
      if (!this.activeChartLabel || !window.plottingApp?.allData) return [];
      const indices = window.plottingApp.allData
        .filter(d => d.label === this.activeChartLabel)
        .map(d => {
          // D3 的 type() 函数将索引存储在 actual_time 和 time 字段
          // 优先级：actual_time (D3设置) > time > idx
          const idx = d.actual_time !== undefined ? d.actual_time : (d.time !== undefined ? d.time : d.idx);
          return parseInt(idx) || 0;
        })
        .sort((a, b) => a - b);
      if (indices.length === 0) return [];
      const segments = [];
      let start = indices[0], end = indices[0];
      for (let i = 1; i < indices.length; i++) {
        if (indices[i] === end + 1) end = indices[i];
        else {
          segments.push({ start, end, count: end - start + 1 });
          start = indices[i]; end = indices[i];
        }
      }
      segments.push({ start, end, count: end - start + 1 });
      return segments;
    },
    activeLabelColor() {
      if (!this.activeChartLabel) return '#7E4C64';
      // Priority 1: Get color from currentAnnotation.label (for newly selected labels)
      if (this.currentAnnotation.label?.text === this.activeChartLabel && this.currentAnnotation.label?.color) {
        return this.currentAnnotation.label.color;
      }
      // Priority 2: Get color from chartLabelStats (for labels with existing points)
      const fromStats = this.chartLabelStats.find(s => s.text === this.activeChartLabel);
      if (fromStats?.color) return fromStats.color;
      // Fallback
      return '#7E4C64';
    }
  },
  mounted() {
    window.vueApp = this;
    this.init();
    // Add keyboard shortcuts
    window.addEventListener('keydown', this.handleGlobalKeydown);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.handleGlobalKeydown);
  },
  methods: {
    handleGlobalKeydown(e) {
      // Ctrl + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (this.canSaveCurrentAnnotation) {
          this.saveActiveLabel();
        } else if (this.savedAnnotations.length > 0) {
          this.saveAnnotationsToServer();
        }
      }
    },
    async init() {
      await this.loadLabels();
      await this.loadCurrentPath();
    },
    logout() {
      localStorage.clear();
      this.$router.push('/login');
    },
    async loadLabels() {
      try {
        const data = await dataService.getLabels();
        if (data.success) {
          this.labels = data.labels;
          Object.keys(this.labels.overall_attribute || {}).forEach(catId => {
            this.$set(this.selectedOverallLabels, catId, '');
          });
          this.updateCategoryColors();
        }
      } catch (e) { console.error('Load labels error:', e); }
    },
    async loadCurrentPath() {
      try {
        const data = await dataService.getCurrentPath();
        if (data.success && data.path) {
          this.currentPath = data.path;
          this.dataPath = data.path;
          await this.loadFiles();
        }
      } catch (e) { console.error('Load path error:', e); }
    },
    async setDataPath() {
      if (!this.dataPath) return this.showToast('请输入路径', 'error');
      try {
        const data = await dataService.setPath(this.dataPath);
        if (data.success) {
          this.currentPath = data.path;
          this.showToast('路径已设置', 'success');
          await this.loadFiles();
        }
      } catch (e) { this.showToast('路径设置失败', 'error'); }
    },
    async loadFiles() {
      if (!this.currentPath) return;
      try {
        const data = await dataService.getFiles(this.currentPath);
        if (data.success) {
          this.files = data.files || [];
          this.currentPath = data.path || this.currentPath;
        }
      } catch (e) { this.showToast('文件加载失败', 'error'); }
    },
    sortFiles(files, sortBy) {
      const sorted = [...files];
      const naturalSort = (a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
      if (sortBy === 'annotation') {
        sorted.sort((a, b) => (b.annotation_count || 0) - (a.annotation_count || 0) || naturalSort(a.name, b.name));
      } else {
        sorted.sort((a, b) => naturalSort(a.name, b.name));
      }
      return sorted;
    },
    async loadResultFile(file) {
      this.selectedResultFile = file.name;
      this.showToast('加载标注结果: ' + file.name, 'info');
      // Load the corresponding CSV file first if not already loaded
      const csvName = file.name.replace('.json', '.csv');
      const csvFile = this.csvFiles.find(f => f.name === csvName);
      if (csvFile && this.selectedFileName !== csvName) {
        await this.selectFile(csvFile);
      }
      // Then load annotations for this file
      const baseName = file.name.replace('.json', '');
      try {
        await this.loadAnnotationsForFile(baseName);
        this.showToast(`已加载 ${this.savedAnnotations.length} 条标注`, 'success');
      } catch (e) {
        this.showToast('加载标注失败', 'error');
      }
    },
    async selectFile(file) {
      this.resetStates();
      this.selectedFileName = file.name;
      this.loading = true;
      try {
        const data = await dataService.getData(file.name);
        if (data.success) {
          const transformedData = transformForD3(data.data);
          this.initChart(transformedData, file.name, data.seriesList, data.labelList || []);
          await this.loadAnnotationsForFile(file.name);
        }
      } catch (e) { this.showToast('加载失败', 'error'); }
      finally { this.loading = false; }
    },
    resetStates() {
      this.currentAnnotation = { label: null, segments: [], prompt: '', expertOutput: '' };
      this.savedAnnotations = [];
      this.activeChartLabel = '';
      this.editingAnnotationIndex = null;
    },
    initChart(csvData, filename, seriesList, labelList) {
      this.isChartMode = true;
      this.chartData = csvData;
      this.seriesList = seriesList;
      this.labelList = labelList.map(l => ({ 
        text: l, 
        color: this.generateUniqueColor() 
      }));
      this.chartDataVersion++;
    },
    setupSelectors(seriesList) {
      const sSelect = document.getElementById('seriesSelect');
      const rSelect = document.getElementById('referenceSelect');
      if (!sSelect || !rSelect) return;
      sSelect.innerHTML = rSelect.innerHTML = '';
      seriesList.forEach(s => {
        const opt = `<option value="${s}">${s}</option>`;
        sSelect.innerHTML += opt; rSelect.innerHTML += opt;
      });
    },
    toggleLocalLabel(label, catId) {
      const labelColor = this.getLabelColor(catId, label.id);
      if (this.currentAnnotation.label?.id === label.id) {
        // Deselect label
        this.$set(this.currentAnnotation, 'label', null);
        this.activeChartLabel = '';  // Fix: Also clear activeChartLabel
        window.plottingApp.selectedLabel = '';
        window.plottingApp.labelColor = '';
      } else {
        // Select new label
        const labelObj = { id: label.id, text: label.text, color: labelColor, categoryId: catId, categoryName: this.localCategories[catId]?.name };
        this.$set(this.currentAnnotation, 'label', labelObj);
        this.activeChartLabel = label.text;  // Fix: Update activeChartLabel for props
        window.plottingApp.selectedLabel = label.text;
        window.plottingApp.labelColor = labelColor;
        if (!plottingApp.labelList) window.plottingApp.labelList = [];
        const existing = window.plottingApp.labelList.find(l => l.name === label.text);
        if (!existing) window.plottingApp.labelList.push({ name: label.text, color: labelColor });
        else existing.color = labelColor;
      }
      this.annotationVersion++;
      this.chartDataVersion++;  // Fix: Trigger chart update
    },
    isLocalLabelSelected(id) { return this.currentAnnotation.label?.id === id; },
    getCategoryColor(catId) {
      return labelUtils.getCategoryColor(catId, this.labels, this.categoryColors);
    },
    getLabelColor(catId, labelId) {
      return labelUtils.getLabelColor(catId, labelId, this.labels, this.categoryColors);
    },
    updateHoverinfo() { this.hoverinfo = { ...plottingApp.hoverinfo }; },
    onSelectionUpdate(selection) {
      if (!selection) return;
      const { start, end, count, minVal, maxVal, mean, std, range } = selection;
      this.selectionStats = { start, end, count, minVal, maxVal, mean, std, range };
      let labelToUse = this.currentAnnotation.label || this.findLabelByText(plottingApp.selectedLabel);
      if (!labelToUse) return this.showToast('请先选择一个标签', 'warning');
      const segment = { start, end, count, minVal, maxVal, mean, label: { ...labelToUse } };
      this.currentAnnotation.segments.push(segment);
      this.activeChartLabel = labelToUse.text;
      this.chartDataVersion++;
      this.showToast(`已添加数据段: ${start}-${end}`, 'success');
    },
    findLabelByText(text) {
      return labelUtils.findLabelByText(text, this.localCategories, this.categoryColors);
    },
    saveActiveLabel() {
      // 获取当前激活标签的信息
      const hasContent = (this.currentAnnotation.prompt || '').trim() || (this.currentAnnotation.expertOutput || '').trim();
      
      // 如果没有激活标签且没有文本内容，返回错误
      if (!this.activeChartLabel && !hasContent) {
        return this.showToast('请先选择标签并框选区域', 'error');
      }
      
      // 只处理当前激活的标签（而非所有标签）
      if (this.activeChartLabel && this.activeSegments.length > 0) {
        const stat = this.chartLabelStats.find(s => s.text === this.activeChartLabel);
        if (!stat) {
          return this.showToast('未找到该标签的标注点', 'error');
        }
        
        const labelObj = this.findLabelByText(stat.text) || { id: stat.text, text: stat.text, color: stat.color };
        // 深拷贝 segments 避免引用问题
        const segmentsCopy = JSON.parse(JSON.stringify(this.activeSegments));
        const annotation = { 
          id: Date.now(), 
          label: labelObj, 
          segments: segmentsCopy, 
          prompt: this.currentAnnotation.prompt || '', 
          expertOutput: this.currentAnnotation.expertOutput || '' 
        };
        
        const idx = this.savedAnnotations.findIndex(a => a.label.text === labelObj.text);
        if (idx !== -1) {
          // 更新已存在标注：合并 segments
          const existingSegs = this.savedAnnotations[idx].segments;
          segmentsCopy.forEach(newSeg => {
            const exists = existingSegs.some(s => s.start === newSeg.start && s.end === newSeg.end);
            if (!exists) existingSegs.push(newSeg);
          });
          existingSegs.sort((a, b) => a.start - b.start);
          this.savedAnnotations[idx].prompt = annotation.prompt || this.savedAnnotations[idx].prompt;
          this.savedAnnotations[idx].expertOutput = annotation.expertOutput || this.savedAnnotations[idx].expertOutput;
        } else {
          this.savedAnnotations.push(annotation);
        }
      } else if (hasContent) {
        // 只有文本内容，没有选中区域
        this.savedAnnotations.push({ 
          id: Date.now(), 
          label: { id: 'no_label', text: '无标签', color: '#999' }, 
          segments: [], 
          prompt: this.currentAnnotation.prompt, 
          expertOutput: this.currentAnnotation.expertOutput 
        });
      }
      
      this.showToast('已添加标注', 'success');
      this.resetCurrentAnnotation();
      this.saveAnnotationsToServer();
    },
    resetCurrentAnnotation() {
      this.currentAnnotation = { label: null, segments: [], prompt: '', expertOutput: '' };
      this.selectionStats = null;
      this.editingAnnotationIndex = null;
    },
    async saveAnnotationsToServer() {
      if (!this.selectedFileName) return;
      try {
        const data = {
          filename: this.selectedFileName,
          overall_attribute: this.selectedOverallLabels,
          annotations: this.savedAnnotations.map(ann => ({
            label: ann.label, segments: ann.segments, prompt: ann.prompt, expert_output: ann.expertOutput
          })),
          export_time: new Date().toISOString()
        };
        const res = await dataService.saveAnnotations(this.selectedFileName, data);
        if (res.success) {
          this.showToast('已自动保存', 'success');
          await this.loadFiles();
        }
      } catch (e) { this.showToast('保存失败', 'error'); }
    },
    async loadAnnotationsForFile(filename) {
      try {
        const data = await dataService.getAnnotations(filename);
        if (data.success) {
          this.savedAnnotations = (data.annotations || []).map(ann => ({
            ...ann, expertOutput: ann.expert_output || ann.expertOutput || '', prompt: ann.prompt || ''
          }));
        }
      } catch (e) { this.savedAnnotations = []; }
    },
    async loadDirectory(path) {
      try {
        const data = await dataService.browseDir(path);
        if (data.success) {
          this.browsePath = data.current_path;
          this.parentPath = data.parent_path || '';
          this.directories = data.directories || [];
        }
      } catch (e) {}
    },
    goToParentDir() { if (this.parentPath) this.loadDirectory(this.parentPath); },
    async selectCurrentDir() {
      this.dataPath = this.browsePath;
      this.showDirBrowser = false;
      await this.setDataPath();
    },
    async saveLabelsToServer() {
      try {
        const res = await dataService.saveLabels(this.labels);
        if (res.success) {
          this.showToast('保存成功', 'success');
          this.showLabelSettings = false;
          this.updateCategoryColors();
        }
      } catch (e) { this.showToast('保存失败', 'error'); }
    },
    updateCategoryColors() {
      Object.entries(this.localCategories).forEach(([id, cat]) => {
        if (cat.color) this.$set(this.categoryColors, id, cat.color);
      });
    },
    addCategory() {
      const id = 'cat_' + Date.now();
      const target = this.labelSettingsTab === 'overall' ? this.labels.overall_attribute : this.labels.local_change;
      this.$set(target, id, { name: '新分类', labels: [], color: '#6b7280' });
    },
    deleteCategory(id) {
      if (confirm('确认删除？')) {
        const target = this.labelSettingsTab === 'overall' ? this.labels.overall_attribute : this.labels.local_change;
        this.$delete(target, id);
      }
    },
    addLabelToCategory(catId) {
      const target = this.labelSettingsTab === 'overall' ? this.overallCategories : this.localCategories;
      if (!target[catId]) return;
      if (!target[catId].labels) this.$set(target[catId], 'labels', []);
      target[catId].labels.push({ id: 'label_' + Date.now(), text: '新标签', color: this.generateUniqueColor() });
    },
    deleteLabelFromCategory(catId, idx) {
      const target = this.labelSettingsTab === 'overall' ? this.overallCategories : this.localCategories;
      target[catId].labels.splice(idx, 1);
    },
    generateUniqueColor() {
      return labelUtils.generateUniqueColor();
    },
    formatNumber(v) { return v?.toFixed(4) || '-'; },
    showToast(message, type = 'info') {
      this.toast = { show: true, message, type };
      setTimeout(() => this.toast.show = false, 3000);
    },
    resetChartView() { if (plottingApp.resetView) window.plottingApp.resetView(); },
    clearAllLabels() {
      if (!window.plottingApp || !window.plottingApp.allData) {
        this.showToast('图表未初始化', 'warning');
        return;
      }
      let count = 0;
      window.plottingApp.allData.forEach(d => {
        if (d.label) {
          d.label = '';
          count++;
        }
      });
      // 强制刷新所有点的样式
      if (window.plottingApp.main) {
        window.plottingApp.main.selectAll('.point')
          .attr('style', 'fill: black; stroke: none; opacity: 1;');
      }
      // 重置 D3 内部状态
      window.plottingApp.selectedLabel = '';
      window.plottingApp.labelColor = '';
      // 重置 Vue 状态
      this.activeChartLabel = '';
      this.resetCurrentAnnotation();
      this.chartDataVersion++;
      this.showToast(`已清除所有标注 (${count}点)`, 'success');
    },
    clearSeries() { if (plottingApp.allData) window.plottingApp.allData.filter(d => d.series === window.plottingApp.selectedSeries).forEach(d => d.label = ''); },
    fileCheck(e) { /* File upload logic */ },
    selectChartLabel(stat) {
      if (this.activeChartLabel === stat.text) this.activeChartLabel = null;
      else { this.activeChartLabel = stat.text; window.plottingApp.selectedLabel = stat.text; window.plottingApp.labelColor = stat.color; }
    },
    navigateToLabelPoints(labelText) {
      if (!window.plottingApp || !plottingApp.allData || !labelText) return;
      
      // Find all points with this label
      const labeledPoints = window.plottingApp.allData
        .map((d, idx) => ({ ...d, idx }))
        .filter(d => d.label === labelText);
      
      if (labeledPoints.length === 0) {
        this.showToast(`未找到 "${labelText}" 的标注点`, 'warning');
        return;
      }
      
      // Find the range of labeled points
      const indices = labeledPoints.map(d => d.idx);
      const minIdx = Math.min(...indices);
      const maxIdx = Math.max(...indices);
      
      this.panChartToRange(minIdx, maxIdx);
      this.showToast(`定位到 ${labelText}: ${minIdx}-${maxIdx} (${labeledPoints.length}点)`, 'info');
    },
    clearLabelFromChart(labelText) {
      if (!labelText || !window.plottingApp || !window.plottingApp.allData) {
        this.showToast('无效的标签', 'error');
        return;
      }
      
      let clearedCount = 0;
      window.plottingApp.allData.forEach(d => {
        if (d.label === labelText) {
          d.label = '';
          clearedCount++;
        }
      });
      
      if (clearedCount > 0) {
        // 刷新图表显示 - 主图和缩略图
        const updatePointStyle = function(d) {
          if (d.label) {
            const labelInfo = window.plottingApp.labelList?.find(l => l.name === d.label);
            const color = labelInfo?.color || '#7E4C64';
            return `fill: ${color}; stroke: ${color}; opacity: 0.75;`;
          }
          return 'fill: black; stroke: none; opacity: 1;';
        };
        
        if (window.plottingApp.main) {
          window.plottingApp.main.selectAll('.point').attr('style', updatePointStyle);
        }
        if (window.plottingApp.context) {
          window.plottingApp.context.selectAll('.point').attr('style', updatePointStyle);
        }
        
        // 如果清除的是当前激活标签，重置激活状态
        if (this.activeChartLabel === labelText) {
          this.activeChartLabel = '';
          window.plottingApp.selectedLabel = '';
          window.plottingApp.labelColor = '';
        }
        
        this.chartDataVersion++;
        this.showToast(`已清除 "${labelText}" 标签 (${clearedCount}点)`, 'success');
      } else {
        this.showToast(`未找到 "${labelText}" 的标注点`, 'warning');
      }
    },
    navigateToSegment(seg) {
      if (!seg || seg.start === undefined || seg.end === undefined) return;
      this.panChartToRange(seg.start, seg.end);
      this.showToast(`定位到: ${seg.start} - ${seg.end}`, 'info');
    },
    removeSegmentByRange(seg) {
      if (!seg || seg.start === undefined || seg.end === undefined) {
        this.showToast('无效的数据段', 'error');
        return;
      }
      if (!window.plottingApp || !window.plottingApp.allData) {
        this.showToast('图表未初始化', 'warning');
        return;
      }
      // 使用 activeChartLabel 优先，否则尝试清除范围内所有标签
      const labelToRemove = this.activeChartLabel;
      
      // 辅助函数：获取数据点的索引
      const getIdx = (d) => {
        const idx = d.actual_time !== undefined ? d.actual_time : (d.time !== undefined ? d.time : d.idx);
        return parseInt(idx) || 0;
      };
      
      let count = 0;
      window.plottingApp.allData.forEach(d => {
        const idx = getIdx(d);
        if (idx >= seg.start && idx <= seg.end) {
          // 如果指定了标签只删除该标签，否则删除所有
          if (!labelToRemove || d.label === labelToRemove) {
            if (d.label) {
              d.label = '';
              count++;
            }
          }
        }
      });
      
      // 强制刷新图表显示
      if (window.plottingApp.main) {
        window.plottingApp.main.selectAll('.point')
          .filter(d => {
            const idx = getIdx(d);
            return idx >= seg.start && idx <= seg.end;
          })
          .attr('style', 'fill: black; stroke: none; opacity: 1;');
      }
      
      this.chartDataVersion++;
      if (count > 0) {
        this.showToast(`已清除 ${count} 个点的标签`, 'success');
      } else {
        this.showToast('该范围内没有可清除的标签', 'info');
      }
    },
    editAnnotation(idx) {
      const ann = this.savedAnnotations[idx];
      this.activeChartLabel = ann.label.text;
      this.currentAnnotation = { ...ann };
      this.editingAnnotationIndex = idx;
    },
    deleteAnnotation(idx) { this.savedAnnotations.splice(idx, 1); this.saveAnnotationsToServer(); },
    cycleAnnotationSegments(idx) {
      const ann = this.savedAnnotations[idx];
      if (!ann || !ann.segments || ann.segments.length === 0) return;
      
      // Get current position for this annotation
      let currentPos = this.annotationCyclePositions[idx] || 0;
      
      // Navigate to current segment
      const seg = ann.segments[currentPos];
      this.panChartToRange(seg.start, seg.end);
      this.showToast(`${ann.label.text}: 段 ${currentPos + 1}/${ann.segments.length} (${seg.start}-${seg.end})`, 'info');
      
      // Increment position for next click (cycle back to 0)
      this.$set(this.annotationCyclePositions, idx, (currentPos + 1) % ann.segments.length);
    },
    navigateToAnnotationSegment(ann, sidx) {
      if (!ann || !ann.segments || !ann.segments[sidx]) return;
      const seg = ann.segments[sidx];
      this.panChartToRange(seg.start, seg.end);
      this.showToast(`定位到 ${ann.label.text}: ${seg.start} - ${seg.end}`, 'info');
    },
    panChartToRange(start, end) {
      // 检查图表是否就绪
      if (!window.plottingApp || !window.plottingApp.plot || !window.plottingApp.context_brush) {
        console.warn('Chart not ready for panning');
        this.showToast('图表未就绪', 'warning');
        return;
      }
      
      // 计算边距（显示段落周围的上下文）
      const segLen = end - start;
      const padding = Math.max(segLen * 0.5, 20);  // 至少 20 点边距
      const newStart = Math.max(0, start - padding);
      const newEnd = end + padding;
      
      // 通过缩略图 brush 更新主图视图
      try {
        if (window.plottingApp.context_xscale && window.plottingApp.plot.context_brush) {
          const newExtent = [newStart, newEnd].map(d => window.plottingApp.context_xscale(d));
          window.plottingApp.plot.context_brush.call(window.plottingApp.context_brush.move, newExtent);
        }
      } catch (e) {
        console.error('Error panning chart:', e);
        this.showToast('定位失败', 'error');
      }
    },
    downloadAnnotations() {
      if (!this.selectedFileName || this.savedAnnotations.length === 0) {
        this.showToast('没有可导出的标注', 'warning');
        return;
      }
      const exportData = {
        filename: this.selectedFileName,
        overall_attribute: this.selectedOverallLabels,
        annotations: this.savedAnnotations.map(ann => ({
          label: {
            id: ann.label.id,
            text: ann.label.text,
            categoryId: ann.label.categoryId,
            color: ann.label.color
          },
          segments: ann.segments,
          prompt: ann.prompt,
          expert_output: ann.expertOutput
        })),
        export_time: new Date().toISOString()
      };
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.selectedFileName}.json`;
      a.click();
      URL.revokeObjectURL(url);
      this.showToast('标注已导出', 'success');
    }
  }
};
</script>

<style>
@import "@/assets/css/style.css";
</style>
