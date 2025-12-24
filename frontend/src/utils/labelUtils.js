/**
 * Label and Category Utility Functions
 */

/**
 * Gets the color for a specific category
 */
export function getCategoryColor(catId, labels, categoryColors) {
  return labels.local_change?.[catId]?.color || 
         categoryColors[catId] || 
         categoryColors.default || '#6b7280';
}

/**
 * Gets the color for a specific label within a category
 */
export function getLabelColor(catId, labelId, labels, categoryColors) {
  const category = labels.local_change?.[catId];
  const label = category?.labels?.find(l => l.id === labelId);
  return label?.color || getCategoryColor(catId, labels, categoryColors);
}

/**
 * Finds a label object by its display text
 */
export function findLabelByText(text, localCategories, categoryColors) {
  for (const [catId, cat] of Object.entries(localCategories)) {
    const label = cat.labels?.find(l => l.text === text);
    if (label) {
      return {
        id: label.id,
        text: label.text,
        color: label.color || getCategoryColor(catId, { local_change: localCategories }, categoryColors),
        categoryId: catId,
        categoryName: cat.name
      };
    }
  }
  return null;
}

/**
 * Generates a unique color from a predefined palette
 */
export function generateUniqueColor() {
  const palette = [
    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', 
    '#22c55e', '#10b981', '#14b8a6', '#3b82f6', '#8b5cf6',
    '#d946ef', '#f43f5e', '#6366f1', '#06b6d4', '#2dd4bf'
  ];
  return palette[Math.floor(Math.random() * palette.length)];
}
