import apiClient from './client';

export const dataService = {
  getLabels() {
    return apiClient.get('/labels');
  },
  
  saveLabels(labels) {
    return apiClient.post('/labels', { labels });
  },
  
  getCurrentPath() {
    return apiClient.get('/current-path');
  },
  
  setPath(path) {
    return apiClient.post('/set-path', { path });
  },
  
  getFiles(path) {
    return apiClient.get(`/files?path=${encodeURIComponent(path)}`);
  },
  
  browseDir(path) {
    return apiClient.get(`/browse-dir?path=${encodeURIComponent(path)}`);
  },
  
  getData(filename) {
    return apiClient.get(`/data/${encodeURIComponent(filename)}`);
  },
  
  getAnnotations(filename) {
    return apiClient.get(`/annotations/${encodeURIComponent(filename)}`);
  },
  
  saveAnnotations(filename, data) {
    return apiClient.post(`/annotations/${encodeURIComponent(filename)}`, data);
  }
};
