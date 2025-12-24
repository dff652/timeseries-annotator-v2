/**
 * Time Series Data Transformation Utilities
 * Standardizes data formats between Backend API, Vue State, and D3 Chart.
 */

/**
 * Transforms raw backend API data into a format suitable for D3.js
 * Ensures consistent field names and numeric types.
 * @param {Array} apiData - The raw 'data' array from /api/data/{filename}
 * @returns {Array} - Array of objects with idx, val, series, label, time, x, y
 */
export function transformForD3(apiData) {
  if (!apiData || !Array.isArray(apiData)) return [];
  
  return apiData.map((d, i) => {
    const val = parseFloat(d.val);
    const idx = d.idx !== undefined ? d.idx : i;
    
    return {
      ...d,
      idx: idx,
      val: isNaN(val) ? 0 : val,
      x: idx, // D3 plotting usually uses x for the index/time axis
      y: isNaN(val) ? 0 : val,
      series: d.series || 'value',
      label: d.label || ''
    };
  });
}

/**
 * Normalizes annotation data from the backend to ensure backward compatibility
 * and consistent field naming (e.g., expertOutput vs expert_output).
 * @param {Object} annData - Raw annotation object from /api/annotations/{filename}
 * @returns {Object} - Normalized annotation object
 */
export function normalizeAnnotations(annData) {
  if (!annData) return { annotations: [], overall_attribute: {} };
  
  const annotations = (annData.annotations || []).map(ann => ({
    ...ann,
    id: ann.id || `ann_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    segments: (ann.segments || []).filter(seg => !isNaN(parseInt(seg.start)) && !isNaN(parseInt(seg.end))),
    // Map both snake_case and camelCase output fields
    expertOutput: ann.expertOutput || ann.expert_output || '',
    prompt: ann.prompt || ann.input || ''
  }));
  
  return {
    filename: annData.filename || '',
    overall_attribute: annData.overall_attribute || annData.overall_attributes || {},
    annotations: annotations
  };
}

/**
 * Prepares annotation data for saving to the backend.
 * Ensures the structure matches the 08-data-schema-spec.md requirement.
 */
export function prepareForSave(filename, annotations, overallAttribute) {
  return {
    filename,
    export_time: new Date().toISOString(),
    annotations: annotations.map(ann => ({
      id: ann.id,
      label: ann.label,
      segments: ann.segments,
      overall_attributes: ann.overall_attributes || {},
      prompt: ann.prompt,
      expertOutput: ann.expertOutput
    })),
    overall_attribute: overallAttribute
  };
}