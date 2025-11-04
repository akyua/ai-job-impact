<template>
  <div class="chart-container">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  components: { Bar },
  props: {
    isDarkMode: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    chartData() {
      const chartColor = this.isDarkMode ? '#ffffff' : '#213547';
      return {
        labels: ['January', 'February', 'March'],
        datasets: [
          {
            data: [40, 20, 12],
            backgroundColor: chartColor,
          },
        ],
      };
    },
    chartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        responsive: true,
        scales: {
          x: {
            ticks: {
              color: textColor,
            },
            grid: {
              color: this.isDarkMode ? '#444444' : '#e5e5e5',
            },
          },
          y: {
            ticks: {
              color: textColor,
            },
            grid: {
              color: this.isDarkMode ? '#444444' : '#e5e5e5',
            },
          },
        },
        plugins: {
          legend: {
            labels: {
              color: textColor,
            },
          },
        },
      };
    },
  },
};
</script>

<style scoped>
.chart-container {
  background-color: var(--color-background);
  padding: 1rem;
}
</style>
