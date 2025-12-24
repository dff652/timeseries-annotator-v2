<template>
  <div class="chart-container-inner">
    <!-- Hover Info -->
    <div id="hoverbox">
      <div id="hoverinfo" class="hover-card" v-show="hoverVisible">
        <div>时间: {{ hoverinfo.time }}</div>
        <div>数值: {{ hoverinfo.val }}</div>
        <div>标签: {{ hoverinfo.label }}</div>
      </div>
    </div>
    
    <!-- Chart DOM -->
    <div id="maindiv" ref="maindiv"></div>
    
    <!-- Hidden sync buttons for Legacy LabelerD3 compatibility -->
    <div style="display:none">
      <button id="updateHover" @click="handleHoverUpdate"></button>
      <button id="updateSelection" @click="handleSelectionUpdate"></button>
      <button id="triggerReplot" @click="replot"></button>
      <button id="triggerRecolor" @click="recolor"></button>
      <button id="clearSeries" @click="$emit('clear-series')"></button>
    </div>
  </div>
</template>

<script>
import * as LabelerD3 from "@/assets/js/LabelerD3.js";
import $ from "jquery";

export default {
  name: 'TimeSeriesChart',
  props: {
    chartData: {
      type: Array,
      required: true
    },
    filename: {
      type: String,
      default: ''
    },
    seriesList: {
      type: Array,
      default: () => []
    },
    labelList: {
      type: Array,
      default: () => []
    },
    selectedLabel: {
      type: String,
      default: ''
    },
    labelColor: {
      type: String,
      default: '#7E4C64'
    }
  },
  data() {
    return {
      plottingApp: {},
      hoverinfo: { val: '', time: '', label: '' },
      hoverVisible: false
    };
  },
  watch: {
    // Re-draw when data changes significantly (new file)
    chartData: {
      handler(newData) {
        if (newData && newData.length > 0) {
          this.initChart();
        }
      },
      immediate: false
    },
    selectedLabel(newVal) {
      if (this.plottingApp) {
        this.plottingApp.selectedLabel = newVal;
        this.plottingApp.labelColor = this.labelColor;
      }
    },
    labelColor(newVal) {
      if (this.plottingApp) {
        this.plottingApp.labelColor = newVal;
      }
    }
  },
  mounted() {
    // Expose this component to window for D3 legacy access
    // This allows LabelerD3.js to find our handlers
    window.plottingApp = this.plottingApp;
    if (this.chartData && this.chartData.length > 0) {
      this.initChart();
    }
  },
  methods: {
    initChart() {
      const container = this.$refs.maindiv;
      if (!container) return;
      
      $(container).empty();
      
      // Initialize plottingApp object for LabelerD3
      this.plottingApp.filename = this.filename;
      this.plottingApp.csvData = this.chartData;
      this.plottingApp.seriesList = this.seriesList;
      this.plottingApp.selectedSeries = this.seriesList[0] || 'value';
      this.plottingApp.refSeries = this.seriesList[1] || this.seriesList[0];
      this.plottingApp.labelList = this.labelList.map(l => ({ name: l.text, color: l.color }));
      this.plottingApp.selectedLabel = this.selectedLabel;
      this.plottingApp.labelColor = this.labelColor;
      
      // Wait for DOM
      this.$nextTick(() => {
        setTimeout(() => {
          LabelerD3.drawLabeler(this.plottingApp);
        }, 100);
      });
    },
    handleHoverUpdate() {
      if (this.plottingApp.hoverinfo) {
        this.hoverinfo = { ...this.plottingApp.hoverinfo };
        this.hoverVisible = true;
        this.$emit('hover-update', this.hoverinfo);
      }
    },
    handleSelectionUpdate() {
      if (this.plottingApp.selection) {
        this.$emit('selection-update', { ...this.plottingApp.selection });
      }
    },
    replot() {
      if (this.plottingApp.resetView) {
        this.plottingApp.resetView();
      }
    },
    recolor() {
      // Logic for force-refreshing colors if needed
      this.$emit('data-version-inc');
    },
    resetView() {
      this.replot();
    }
  }
};
</script>

<style scoped>
.chart-container-inner {
  position: relative;
  width: 100%;
  height: 100%;
}

#maindiv {
  width: 100%;
  min-height: 500px;
}

#hoverbox {
  position: absolute;
  pointer-events: none;
  z-index: 10;
}

.hover-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 120px;
}
</style>
