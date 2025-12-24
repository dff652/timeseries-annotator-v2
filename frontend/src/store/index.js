import Vue from 'vue';

export const store = Vue.observable({
  currentUser: localStorage.getItem('name') || localStorage.getItem('username') || 'User',
  labels: { overall_attribute: {}, local_change: {} },
  currentPath: '',
  selectedFileName: '',
  isChartMode: false,
  toast: { show: false, message: '', type: 'info' },
  history: [],
  historyIndex: -1
});

export const mutations = {
  pushHistory(data) {
    // Basic undo/redo logic
    const stateSnapshot = JSON.parse(JSON.stringify(data));
    store.history = store.history.slice(0, store.historyIndex + 1);
    store.history.push(stateSnapshot);
    if (store.history.length > 20) store.history.shift();
    store.historyIndex = store.history.length - 1;
  },
  setCurrentUser(user) {
    store.currentUser = user;
  },
  setLabels(labels) {
    store.labels = labels;
  },
  setCurrentPath(path) {
    store.currentPath = path;
  },
  setSelectedFileName(name) {
    store.selectedFileName = name;
  },
  setIsChartMode(mode) {
    store.isChartMode = mode;
  },
  showToast(message, type = 'info') {
    store.toast = { show: true, message, type };
    setTimeout(() => {
      store.toast.show = false;
    }, 3000);
  }
};
