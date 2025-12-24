<template>
  <main class="main-content">
    <!-- Welcome Page -->
    <div class="welcome-section" v-if="!isChartMode">
      <h2 class="title">时序数据标注工具</h2>
      <p class="subtitle">Time Series Annotation Tool v2</p>
      <button class="btn btn-lg btn-primary" @click="$emit('upload-click')">📤 上传CSV文件</button>
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
      
      <!-- Instructions & Toolbar (above chart) -->
      <div class="toolbar" v-if="isChartMode" id="instrSelect">
        <div class="toolbar-row">
          <div class="toolbar-section instr compact">
            <span><strong>标注:</strong> 点击切换 | 拖拽框选 | <kbd>Shift</kbd>+拖拽取消</span>
          </div>
          <div class="toolbar-section instr compact">
            <span><strong>导航:</strong> <kbd>←</kbd><kbd>→</kbd>平移 | <kbd>↑</kbd><kbd>↓</kbd>或滚轮缩放</span>
          </div>
          <div class="toolbar-section actions-inline">
            <button class="btn btn-secondary btn-sm" @click="$emit('reset-view')">🔄 重置视图</button>
            <button class="btn btn-warning btn-sm" @click="$emit('clear-labels')">清除标注</button>
          </div>
        </div>
        <div class="toolbar-row">
          <div class="toolbar-section selectors" id="selectors">
            <div class="selector-item"><label>主序列:</label><select id="seriesSelect"></select></div>
            <div class="selector-item"><label>参考序列:</label><select id="referenceSelect"></select></div>
          </div>
          <!-- Selection Stats -->
          <div class="toolbar-section selection-stats-box" v-if="selectionStats">
            <div class="stats-header">📊 框选统计</div>
            <div class="stats-grid">
              <span class="stat-label">索引</span><span class="stat-value">{{ selectionStats.start }} - {{ selectionStats.end }}</span>
              <span class="stat-label">点数</span><span class="stat-value">{{ selectionStats.count }}</span>
              <span class="stat-label">范围</span><span class="stat-value">{{ formatNumber(selectionStats.minVal) }} ~ {{ formatNumber(selectionStats.maxVal) }}</span>
              <span class="stat-label">均值</span><span class="stat-value">{{ formatNumber(selectionStats.mean) }}</span>
            </div>
            <div class="stats-grid">
              <span class="stat-label">标准差</span><span class="stat-value">{{ formatNumber(selectionStats.std) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- D3 Chart Container -->
      <div id="maindiv"></div>
    </div>
  </main>
</template>

<script>
export default {
  name: 'ChartArea',
  props: {
    isChartMode: Boolean,
    hoverinfo: Object,
    selectionStats: Object,
    formatNumber: Function
  }
};
</script>
