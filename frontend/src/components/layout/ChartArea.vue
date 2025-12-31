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
            <button class="btn btn-secondary btn-sm" @click="resetView">🔄 重置视图</button>
            <button class="btn btn-warning btn-sm" @click="$emit('clear-labels')">清除标注</button>
          </div>
        </div>
        <div class="toolbar-row">
          <div class="toolbar-section selectors" id="selectors">
            <div class="selector-item">
              <label>主序列:</label>
              <select v-model="localSelectedSeries" @change="onSeriesChange">
                <option v-for="s in seriesList" :key="'main_'+s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="selector-item">
              <label>参考序列:</label>
              <select v-model="localRefSeries" @change="onSeriesChange">
                <option v-for="s in seriesList" :key="'ref_'+s" :value="s">{{ s }}</option>
              </select>
            </div>
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
      
      <!-- Integrated D3 Chart Component -->
      <time-series-chart
        ref="tsChart"
        :chart-data="chartData"
        :filename="filename"
        :series-list="seriesList"
        :label-list="labelList"
        :selected-label="selectedLabel"
        :label-color="labelColor"
        @selection-update="onSelectionUpdate"
        @hover-update="onHoverUpdate"
        @data-version-inc="$emit('data-version-inc')"
        @clear-series="$emit('clear-series')"
      />
    </div>
  </main>
</template>

<script>
import TimeSeriesChart from '../chart/TimeSeriesChart.vue';

export default {
  name: 'ChartArea',
  components: {
    TimeSeriesChart
  },
  props: {
    isChartMode: Boolean,
    chartData: {
      type: Array,
      default: () => []
    },
    filename: String,
    seriesList: Array,
    labelList: Array,
    selectedLabel: String,
    labelColor: String,
    selectionStats: Object,
    formatNumber: Function
  },
  data() {
    return {
      localSelectedSeries: '',
      localRefSeries: ''
    };
  },
  watch: {
    seriesList: {
      handler(newList) {
        if (newList && newList.length > 0) {
          this.localSelectedSeries = newList[0];
          this.localRefSeries = newList[1] || newList[0];
        }
      },
      immediate: true
    }
  },
  methods: {
    onSeriesChange() {
      if (this.$refs.tsChart) {
        this.$refs.tsChart.updateSeries(this.localSelectedSeries, this.localRefSeries);
      }
    },
    onSelectionUpdate(selection) {
      this.$emit('selection-update', selection);
    },
    onHoverUpdate(hoverinfo) {
      // Internal hover info is managed by TimeSeriesChart, 
      // but we can pass it up if parent needs it
      this.$emit('hover-update', hoverinfo);
    },
    resetView() {
      if (this.$refs.tsChart) {
        this.$refs.tsChart.resetView();
      }
    }
  }
};
</script>

<style scoped>
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  text-align: center;
}

.chart-area {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.toolbar {
  padding: 10px 15px;
  background: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.instr {
  font-size: 0.75rem;
  color: #666;
}

kbd {
  background-color: #eee;
  border-radius: 3px;
  border: 1px solid #b4b4b4;
  box-shadow: 0 1px 1px rgba(0,0,0,.2),0 2px 0 0 rgba(255,255,255,.7) inset;
  color: #333;
  display: inline-block;
  font-size: .85em;
  font-weight: 700;
  line-height: 1;
  padding: 2px 4px;
  white-space: nowrap;
}

.selection-stats-box {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 0.75rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: auto auto;
  gap: 2px 10px;
}

.stat-label { color: #888; }
.stat-value { font-weight: 600; color: #7E4C64; }

.selectors {
  display: flex;
  gap: 15px;
}

.selector-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
}

.selector-item select {
  padding: 2px 5px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
</style>