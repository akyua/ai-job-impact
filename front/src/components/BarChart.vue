<template>
  <div class="chart-container">
    <Bar :data="chartData" :options="finalChartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  components: { Bar },
  props: {
    chartData: {
      type: Object,
      required: true,
    },
    chartOptions: {
      type: Object,
      default: () => ({}),
    },
    isDarkMode: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    finalChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      const defaultOptions = {
        responsive: true,
        scales: {
          x: { ticks: { color: textColor }, grid: { color: this.isDarkMode ? '#444444' : '#e5e5e5' } },
          y: { ticks: { color: textColor }, grid: { color: this.isDarkMode ? '#444444' : '#e5e5e5' } },
        },
        plugins: {
          legend: { display: false },
        },
      };

      return { ...defaultOptions, ...this.chartOptions };
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  min-height: 400px;
  background-color: var(--color-background);
  padding: 1rem;
}
</style>
