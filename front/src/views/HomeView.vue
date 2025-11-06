<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Impacto da IA no Mercado de Trabalho</h1>
      <p class="subtitle">Analisando tendências de automação e crescimento de vagas.</p>
      <div class="filter-container">
        <label for="location-filter">Filtrar por Localização:</label>
        <select id="location-filter" v-model="selectedLocation" @change="fetchDashboardData">
          <option>All</option>
          <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
        </select>
      </div>
      <p class="data-source">Fonte dos dados: {{ dataSource }}</p>
    </header>

    <div v-if="isLoading" class="loading-message">
      <p>Carregando dados do dashboard...</p>
    </div>

    <div v-else class="charts-grid">
      <section class="chart-section">
        <h2>Top 15 Empregos com Maior Risco de Automação (%)</h2>
        <BarChart :chartData="highRiskJobsData" :chartOptions="horizontalChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section class="chart-section">
        <h2>Top 15 Empregos com Menor Risco de Automação (%)</h2>
        <BarChart :chartData="lowRiskJobsData" :chartOptions="lowRiskHorizontalChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section class="chart-section full-width">
        <h2>Projeção de Crescimento de Vagas por Indústria (2024-2030)</h2>
        <BarChart :chartData="jobGrowthData" :chartOptions="verticalChartOptions" :isDarkMode="isDarkMode" />
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BarChart from '../components/BarChart.vue';

const API_BASE_URL = 'http://localhost:5001/api';
const MAX_LABEL_LENGTH = 25; // Define max length for job titles

export default {
  components: {
    BarChart,
  },
  props: {
    isDarkMode: Boolean,
  },
  data() {
    return {
      isLoading: true,
      locations: [],
      selectedLocation: 'All',
      highRiskJobsData: { labels: [], datasets: [] },
      lowRiskJobsData: { labels: [], datasets: [] },
      jobGrowthData: { labels: [], datasets: [] },
    };
  },
  computed: {
    dataSource() {
      return this.selectedLocation === 'All' ? 'Global' : this.selectedLocation;
    },
    horizontalChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { left: 25 } }, // Add padding for long labels
        scales: {
          x: { min: 0, max: 100, ticks: { color: textColor } },
          y: { ticks: { color: textColor } }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Risco de Automação: ${context.parsed.x.toFixed(2)}%`
            }
          }
        }
      };
    },
    lowRiskHorizontalChartOptions() {
      const maxVal = this.lowRiskJobsData.datasets.length
        ? Math.max(...this.lowRiskJobsData.datasets[0].data)
        : 0;
      let suggestedMax = Math.ceil(maxVal) + 1;
      suggestedMax = suggestedMax < 10 ? 10 : suggestedMax;

      const options = JSON.parse(JSON.stringify(this.horizontalChartOptions));
      options.scales.x.max = suggestedMax;
      return options;
    },
    verticalChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { ticks: { color: textColor } }, y: { ticks: { color: textColor } } },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Crescimento Projetado: ${context.parsed.y.toFixed(2)}%`
            }
          }
        }
      };
    }
  },
  async created() {
    await this.fetchLocations();
    await this.fetchDashboardData();
  },
  methods: {
    async fetchLocations() {
      try {
        const response = await axios.get(`${API_BASE_URL}/locations`);
        this.locations = response.data;
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    },
    async fetchDashboardData() {
      this.isLoading = true;
      try {
        await Promise.all([
          this.fetchJobsByRisk('desc'),
          this.fetchJobsByRisk('asc'),
          this.fetchJobGrowth(),
        ]);
      } catch (error) {
        console.error("Failed to fetch all dashboard data:", error);
      }
      this.isLoading = false;
    },
    async fetchJobsByRisk(sortOrder) {
      const params = { sort: sortOrder, limit: 15, location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/jobs-by-risk`, { params });
      const data = response.data;

      const chartData = {
        labels: data.map(item => {
          const title = item['Job Title'];
          return title.length > MAX_LABEL_LENGTH
            ? title.substring(0, MAX_LABEL_LENGTH) + '...'
            : title;
        }),
        datasets: [{
          data: data.map(item => item['Automation Risk (%)']),
          backgroundColor: sortOrder === 'desc' ? '#c0392b' : '#27ae60',
          barPercentage: 0.9,
          categoryPercentage: 0.8,
        }]
      };

      if (sortOrder === 'desc') {
        this.highRiskJobsData = chartData;
      } else {
        this.lowRiskJobsData = chartData;
      }
    },
    async fetchJobGrowth() {
      const params = { location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/job-growth`, { params });
      // Sort by highest growth and take top 15 for clarity
      const data = response.data.sort((a, b) => b['Projected Growth (%)'] - a['Projected Growth (%)']).slice(0, 15);

      this.jobGrowthData = {
        labels: data.map(item => item['Industry']),
        datasets: [{
          data: data.map(item => item['Projected Growth (%)']),
          backgroundColor: '#3498db',
        }]
      };
    }
  }
};
</script>

<style scoped>
.dashboard {
  padding: 1rem;
  color: var(--color-text);
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--color-text-soft);
}

.filter-container {
  margin: 1.5rem 0;
}

.filter-container label {
  margin-right: 0.5rem;
}

.filter-container select {
  padding: 0.5rem;
  border-radius: 4px;
}

.data-source {
  font-style: italic;
  color: var(--color-text-soft);
}

.loading-message {
  text-align: center;
  font-size: 1.5rem;
  padding: 4rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.chart-section {
  background-color: var(--color-background-soft);
  padding: 1.5rem;
  border-radius: 8px;
  min-height: 500px; /* Ensure charts have space */
}

.chart-section.full-width {
  grid-column: 1 / -1;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}
</style>