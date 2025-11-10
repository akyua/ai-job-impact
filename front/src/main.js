import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { Chart, registerables } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(...registerables, ChartDataLabels);

const app = createApp(App)

app.use(router)

app.mount('#app')
