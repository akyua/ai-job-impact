<template>
  <div class="chart-container">
    <Doughnut :data="chartData" :options="finalChartOptions" />
  </div>
</template>

<script>
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

export default {
  components: { Doughnut },
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
        maintainAspectRatio: false,
        plugins: {
          legend: { 
            display: true,
            position: 'bottom',
            labels: {
              color: textColor,
              padding: 15,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            enabled: true
          }
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
