<template>
  <aside class="sidebar right-sidebar" v-if="isChartMode">
    <!-- 📝 标注工作区 -->
    <div class="panel-section workspace-section">
      <h3 class="section-title">📝 标注工作区</h3>
      
      <!-- 标签 -->
      <div class="form-group">
        <label>标签</label>
        <div class="chart-labels-container" v-if="chartLabelStats.length > 0">
          <div v-for="stat in chartLabelStats" :key="stat.text" 
               class="chart-label-tag" 
               :class="{ 'active': activeChartLabel === stat.text }"
               :style="{ backgroundColor: stat.color }"
               @click="$emit('select-chart-label', stat)">
            <span class="label-text">{{ stat.text }}</span>
            <span class="label-count">({{ stat.count }})</span>
            <button class="label-remove" @click.stop="$emit('clear-label-from-chart', stat.text)" title="清除">×</button>
          </div>
        </div>
        <div v-else class="empty-message">← 左侧选择标签后在图中框选</div>
      </div>
      
      <!-- 数据段索引 -->
      <div class="form-group">
        <label v-if="activeChartLabel">数据段索引 ({{ activeSegments.length }})</label>
        <label v-else>数据段索引</label>
        <div class="segment-index-area">
          <div v-if="activeChartLabel && activeSegments.length > 0" class="segments-list">
            <div v-for="(seg, idx) in activeSegments" :key="idx" class="segment-item clickable" @click="$emit('navigate-to-segment', seg)" :style="{ borderLeft: '3px solid ' + activeLabelColor }">
              <span class="segment-range" :style="{ color: activeLabelColor }">{{ seg.start }} - {{ seg.end }}</span>
              <span class="segment-count">({{ seg.count }}点)</span>
              <button class="btn-icon-sm" @click.stop="$emit('remove-segment-by-range', seg)" title="删除">×</button>
            </div>
          </div>
          <div v-else-if="activeChartLabel" class="empty-placeholder">该标签暂无数据段</div>
          <div v-else-if="chartLabelStats.length > 0" class="empty-placeholder">↑ 点击标签查看数据段</div>
          <div v-else class="empty-placeholder">← 选择标签框选，或直接输入问题和分析</div>
        </div>
      </div>
      
      <!-- 问题和评价 -->
      <div class="form-group">
        <label>问题</label>
        <textarea :value="currentAnnotation.prompt" 
                  @input="updateAnnotation('prompt', $event.target.value)"
                  rows="2" 
                  placeholder="描述发现的问题..."></textarea>
      </div>
      <div class="form-group">
        <label>评价</label>
        <textarea :value="currentAnnotation.expertOutput" 
                  @input="updateAnnotation('expertOutput', $event.target.value)"
                  rows="2" 
                  placeholder="评价..."></textarea>
      </div>
      
      <!-- 操作按钮 -->
      <div class="form-actions">
        <button class="btn btn-primary" 
                @click="$emit('save-active-label')" 
                :disabled="!canSaveCurrentAnnotation">
          {{ editingAnnotationIndex !== null ? '更新标注' : '添加标注' }}
        </button>
        <button class="btn" 
                @click="$emit('reset-current-annotation')">重置</button>
      </div>
    </div>

    <!-- 📋 标注结果 -->
    <div class="panel-section">
      <div class="section-header">
        <h3 class="section-title">📋 标注结果 ({{ savedAnnotations.length }})</h3>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-sm btn-primary" @click="$emit('save-server')" :disabled="savedAnnotations.length === 0" title="保存到服务器">💾 保存</button>
          <button class="btn btn-sm" @click="$emit('download')" :disabled="savedAnnotations.length === 0" title="导出到本地">📥 导出</button>
        </div>
      </div>
      <div class="annotation-list">
        <div v-for="(ann, idx) in savedAnnotations" :key="ann.id" class="annotation-item" :class="{ 'editing': editingAnnotationIndex === idx }">
          <div class="annotation-header">
            <span class="label-tag clickable" :style="{ backgroundColor: ann.label.color }" @click="$emit('cycle-segments', idx)" :title="'点击定位数据段'">{{ ann.label.text }}</span>
            <span class="segment-summary">({{ ann.segments.length }}段)</span>
            <div class="annotation-actions">
              <button class="btn-icon-sm" @click="$emit('edit-annotation', idx)" title="编辑">✏️</button>
              <button class="btn-delete" @click="$emit('delete-annotation', idx)" title="删除">×</button>
            </div>
          </div>
          <div class="annotation-segments">
            <span v-for="(seg, sidx) in ann.segments" :key="sidx" class="segment-badge clickable" @click="$emit('navigate-ann-segment', ann, sidx)">
              {{ seg.start }}-{{ seg.end }}
            </span>
          </div>
          <div class="annotation-text" v-if="ann.prompt">
            <small>Q: {{ ann.prompt.substring(0, 50) }}{{ ann.prompt.length > 50 ? '...' : '' }}</small>
          </div>
        </div>
        <p v-if="savedAnnotations.length === 0" class="empty-message">暂无标注</p>
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'RightSidebar',
  props: {
    isChartMode: Boolean,
    chartLabelStats: Array,
    activeChartLabel: String,
    activeSegments: Array,
    activeLabelColor: String,
    currentAnnotation: Object,
    canSaveCurrentAnnotation: Boolean,
    editingAnnotationIndex: Number,
    savedAnnotations: Array
  },
  methods: {
    updateAnnotation(field, value) {
      const updated = { ...this.currentAnnotation, [field]: value };
      this.$emit('update:currentAnnotation', updated);
    }
  }
};
</script>
