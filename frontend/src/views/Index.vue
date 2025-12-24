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
        .map(d => parseInt(d.time) || 0)
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
      return this.chartLabelStats.find(s => s.text === this.activeChartLabel)?.color || '#7E4C64';
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
        this.$set(this.currentAnnotation, 'label', null);
        plottingApp.selectedLabel = '';
      } else {
        const labelObj = { id: label.id, text: label.text, color: labelColor, categoryId: catId, categoryName: this.localCategories[catId]?.name };
        this.$set(this.currentAnnotation, 'label', labelObj);
        plottingApp.selectedLabel = label.text;
        plottingApp.labelColor = labelColor;
        if (!plottingApp.labelList) plottingApp.labelList = [];
        const existing = plottingApp.labelList.find(l => l.name === label.text);
        if (!existing) plottingApp.labelList.push({ name: label.text, color: labelColor });
        else existing.color = labelColor;
      }
      this.annotationVersion++;
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
      const stats = this.chartLabelStats.filter(s => s.count > 0);
      const hasContent = (this.currentAnnotation.prompt || '').trim() || (this.currentAnnotation.expertOutput || '').trim();
      if (stats.length === 0 && !hasContent) return this.showToast('内容为空', 'error');
      
      stats.forEach(stat => {
        const labelObj = this.findLabelByText(stat.text) || { id: stat.text, text: stat.text, color: stat.color };
        const annotation = { id: Date.now(), label: labelObj, segments: this.activeSegments, prompt: this.currentAnnotation.prompt || '', expertOutput: this.currentAnnotation.expertOutput || '' };
        const idx = this.savedAnnotations.findIndex(a => a.label.text === labelObj.text);
        if (idx !== -1) {
          this.savedAnnotations[idx].prompt = annotation.prompt;
          this.savedAnnotations[idx].expertOutput = annotation.expertOutput;
        } else this.savedAnnotations.push(annotation);
      });
      
      if (stats.length === 0 && hasContent) {
        this.savedAnnotations.push({ id: Date.now(), label: { id: 'no_label', text: '无标签', color: '#999' }, segments: [], prompt: this.currentAnnotation.prompt, expertOutput: this.currentAnnotation.expertOutput });
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
    resetChartView() { if (plottingApp.resetView) plottingApp.resetView(); },
    clearAllLabels() {
      if (plottingApp.allData) plottingApp.allData.forEach(d => d.label = '');
      if (plottingApp.main) plottingApp.main.selectAll('.point').attr('style', 'fill: black; stroke: none; opacity: 1;');
      this.resetCurrentAnnotation();
      this.chartDataVersion++;
    },
    clearSeries() { if (plottingApp.allData) plottingApp.allData.filter(d => d.series === plottingApp.selectedSeries).forEach(d => d.label = ''); },
    fileCheck(e) { /* File upload logic */ },
    selectChartLabel(stat) {
      if (this.activeChartLabel === stat.text) this.activeChartLabel = null;
      else { this.activeChartLabel = stat.text; plottingApp.selectedLabel = stat.text; plottingApp.labelColor = stat.color; }
    },
    clearLabelFromChart(text) { plottingApp.allData.forEach(d => { if (d.label === text) d.label = ''; }); this.chartDataVersion++; },
    navigateToSegment(seg) { this.panChartToRange(seg.start, seg.end); },
    removeSegmentByRange(seg) {
      plottingApp.allData.forEach(d => { if (parseInt(d.id) >= seg.start && parseInt(d.id) <= seg.end && d.label === this.activeChartLabel) d.label = ''; });
      this.chartDataVersion++;
    },
    editAnnotation(idx) {
      const ann = this.savedAnnotations[idx];
      this.activeChartLabel = ann.label.text;
      this.currentAnnotation = { ...ann };
      this.editingAnnotationIndex = idx;
    },
    deleteAnnotation(idx) { this.savedAnnotations.splice(idx, 1); this.saveAnnotationsToServer(); },
    cycleAnnotationSegments(idx) { /* Cycle logic */ },
    navigateToAnnotationSegment(ann, sidx) { this.panChartToRange(ann.segments[sidx].start, ann.segments[sidx].end); },
    panChartToRange(start, end) {
      if (!plottingApp.plot?.context_brush) return;
      const padding = Math.max((end - start) * 0.5, 20);
      const extent = [start - padding, end + padding].map(d => plottingApp.context_xscale(d));
      plottingApp.plot.context_brush.call(plottingApp.context_brush.move, extent);
    },
    downloadAnnotations() { /* Export logic */ }
  }
};
</script>

<style>
@import "@/assets/css/style.css";
</style>
