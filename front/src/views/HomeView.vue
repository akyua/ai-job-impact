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

      <section class="analysis-section">
        <h3>Análise dos 3 Principais Empregos em Risco</h3>
        <ul>
          <li v-for="job in top3HighRiskJobs" :key="job['Job Title']">
            <strong>{{ translateTitle(job['Job Title']) }} (Risco: {{ job['Automation Risk (%)'] }}%)</strong>
            <p>{{ getRiskExplanation(job, 'high') }}</p>
          </li>
        </ul>
      </section>

      <section class="chart-section">
        <h2>Top 15 Empregos com Menor Risco de Automação (%)</h2>
        <BarChart :chartData="lowRiskJobsData" :chartOptions="lowRiskHorizontalChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section class="analysis-section">
        <h3>Análise dos 3 Principais Empregos de Baixo Risco</h3>
        <ul>
          <li v-for="job in top3LowRiskJobs" :key="job['Job Title']">
            <strong>{{ translateTitle(job['Job Title']) }} (Risco: {{ job['Automation Risk (%)'] }}%)</strong>
            <p>{{ getRiskExplanation(job, 'low') }}</p>
          </li>
        </ul>
      </section>

      <section class="chart-section full-width">
        <h2>Projeção de Crescimento de Vagas por Indústria (2024-2030)</h2>
        <BarChart :chartData="jobGrowthData" :chartOptions="verticalChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section v-if="selectedLocation === 'Brazil'" class="chart-section">
        <h2>Distribuição de Trabalhadores por Nível de Risco</h2>
        <PieChart :chartData="workersByRiskData" :chartOptions="pieChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section v-if="selectedLocation === 'Brazil'" class="chart-section">
        <h2>Tipo de Impacto da IA no Emprego</h2>
        <PieChart :chartData="impactTypeData" :chartOptions="pieChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section v-if="selectedLocation === 'Brazil'" class="chart-section full-width">
        <h2>Top 10 Setores com Mais Trabalhadores em Alto Risco</h2>
        <BarChart :chartData="sectorsAtRiskData" :chartOptions="sectorsAtRiskChartOptions" :isDarkMode="isDarkMode" />
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BarChart from '../components/BarChart.vue';
import PieChart from '../components/PieChart.vue';

const API_BASE_URL = 'http://localhost:5001/api';
const MAX_LABEL_LENGTH = 25; // Define max length for job titles

const translations = {
  'Meteorologist': 'Meteorologista',
  'Data Entry Clerk': 'Digitador(a)',
  'Telemarketer': 'Operador(a) de Telemarketing',
  'Accountant': 'Contador(a)',
  'Truck Driver': 'Motorista de Caminhão',
  'Fast food restaurant manager': 'Gerente de Fast Food',
  'Water engineer': 'Engenheiro(a) Hídrico(a)',
  'Hydrologist': 'Hidrologista',
  'Media buyer': 'Comprador(a) de Mídia',
  'Investment analyst': 'Analista de Investimentos',
  'Chief Executive': 'Diretor(a) Executivo(a)',
  'Surgeon': 'Cirurgião(ã)',
  'Graphic Designer': 'Designer Gráfico(a)',
  'Software Engineer': 'Engenheiro(a) de Software',
  'Teacher': 'Professor(a)',
  'Armed forces logistics/support/administrative officer': 'Oficial de Logística/Suporte das Forças Armadas',
  'Sports development officer': 'Oficial de Desenvolvimento Esportivo',
  'Jeweller': 'Joalheiro(a)',
  'Designer, jewellery': 'Designer de Joias', // Corrected entry
  'Clinical biochemist': 'Bioquímico(a) Clínico(a)',
  'Therapist': 'Terapeuta',
  'Nutritionist': 'Nutricionista',
  'Medical sales representative': 'Representante de Vendas Médicas',
  'Banker': 'Bancário(a)', // New
  'Electrical Engineer': 'Engenheiro(a) Eletricista', // New
  'Marine Scientist': 'Cientista Marinho(a)' // New
};

export default {
  components: {
    BarChart,
    PieChart,
  },
  props: {
    isDarkMode: Boolean,
  },
  data() {
    return {
      isLoading: true,
      locations: [],
      selectedLocation: 'All',
      highRiskJobs: [],
      lowRiskJobs: [],
      jobGrowth: [],
      highRiskJobsData: { labels: [], datasets: [] },
      lowRiskJobsData: { labels: [], datasets: [] },
      jobGrowthData: { labels: [], datasets: [] },
      workersByRiskData: { labels: [], datasets: [] },
      impactTypeData: { labels: [], datasets: [] },
      sectorsAtRiskData: { labels: [], datasets: [] },
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
        layout: { padding: { left: 25 } },
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

      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { left: 25 } },
        scales: {
          x: { min: 0, max: suggestedMax, ticks: { color: textColor } },
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
    verticalChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
          x: { 
            ticks: { 
              color: textColor,
              maxRotation: 45,
              minRotation: 45,
              align: 'end'
            } 
          }, 
          y: { ticks: { color: textColor } } 
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Crescimento Projetado: ${context.parsed.y.toFixed(2)}%`
            }
          }
        }
      };
    },
    sectorsAtRiskChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
          x: { 
            ticks: { 
              color: textColor,
              maxRotation: 45,
              minRotation: 45,
              align: 'end'
            } 
          }, 
          y: { 
            ticks: { 
              color: textColor,
              callback: function(value) {
                return value.toLocaleString();
              }
            }
          } 
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Trabalhadores em Risco: ${context.parsed.y.toLocaleString()}`
            }
          }
        }
      };
    },
    top3HighRiskJobs() {
      return this.highRiskJobs.slice(0, 3);
    },
    top3LowRiskJobs() {
      return this.lowRiskJobs.slice(0, 3);
    },
  },
  async created() {
    await this.fetchLocations();
    await this.fetchDashboardData();
  },
  methods: {
    translateTitle(title) {
      return translations[title] || title;
    },
    getRiskExplanation(job, riskType) {
      const title = job['Job Title'];
      
      const specificExplanations = {
        // --- High Risk Examples ---
        'Meteorologist': 'A meteorologia moderna depende da análise de padrões em conjuntos de dados massivos (imagens de satélite, sensores, modelos climáticos). A IA é excepcionalmente eficiente nisso, prevendo o tempo com maior precisão e velocidade. Embora a interpretação final e a comunicação de alertas complexos ainda possam exigir um especialista, a maior parte da análise de dados, que é o cerne do trabalho, é altamente automatizável.',
        'Data Entry Clerk': 'Este trabalho consiste em transferir informações de um formato para outro, uma tarefa altamente estruturada e repetitiva. Algoritmos de OCR (Reconhecimento Óptico de Caracteres) e RPA (Automação de Processos Robóticos) podem executar essa função 24/7 com velocidade e precisão superiores, tornando a intervenção humana quase obsoleta.',
        'Telemarketer': 'Os avanços em modelos de linguagem de IA (como os que alimentam chatbots) permitem a criação de sistemas que podem conduzir conversas de vendas, responder a perguntas e registrar informações de forma autônoma. Eles podem realizar milhares de chamadas simultaneamente e otimizar roteiros em tempo real, superando a eficiência humana.',
        'Accountant': 'Muitas tarefas contábeis, como reconciliação de contas, categorização de despesas e geração de relatórios financeiros padrão, são baseadas em regras e dados. Softwares de contabilidade com IA podem automatizar grande parte desse trabalho, reduzindo erros e liberando os contadores para se concentrarem em análises estratégicas e consultoria, que são de menor risco.',
        'Truck Driver': 'A condução em rodovias, que compõe a maior parte do trabalho de um caminhoneiro, é um cenário ideal para a automação. Veículos autônomos podem operar por mais tempo, com maior eficiência de combustível e, teoricamente, com menos acidentes causados por fadiga. A logística de "primeira e última milha" é mais complexa, mas a automação do transporte de longa distância representa o maior risco.',
        'Fast food restaurant manager': 'A gestão de restaurantes de fast food envolve muitas tarefas rotineiras e baseadas em regras, como gestão de estoque, agendamento de funcionários e otimização de pedidos. A IA pode automatizar e otimizar essas operações, reduzindo a necessidade de supervisão humana direta para tarefas operacionais.',
        'Water engineer': 'Engenheiros de água lidam com o monitoramento e otimização de sistemas hídricos. A IA pode analisar grandes volumes de dados de sensores para prever falhas, otimizar a distribuição e detectar vazamentos, automatizando muitas das tarefas de análise e monitoramento que antes exigiam intervenção humana.',
        'Hydrologist': 'Hidrologistas analisam dados complexos sobre a distribuição e o movimento da água. A IA pode processar vastos conjuntos de dados de sensores, satélites e modelos climáticos para prever inundações, secas e otimizar a gestão de recursos hídricos com maior precisão e velocidade, automatizando muitas tarefas de análise e modelagem.',
        'Media buyer': 'Compradores de mídia otimizam a alocação de orçamentos de publicidade. A IA pode analisar o desempenho de campanhas em tempo real, identificar os canais mais eficazes e ajustar lances e segmentação automaticamente, superando a capacidade humana de processar e reagir a grandes volumes de dados de mercado.',
        'Investment analyst': 'Analistas de investimento pesquisam e avaliam ativos financeiros. A IA pode processar e interpretar notícias financeiras, relatórios de empresas e dados de mercado em uma escala e velocidade impossíveis para humanos, identificando padrões e prevendo tendências. Embora a tomada de decisão final possa permanecer humana, a maior parte da análise de dados pode ser automatizada.',

        // --- Low Risk Examples ---
        'Chief Executive': 'A liderança executiva exige visão estratégica, negociação complexa, inteligência emocional para gerir pessoas e tomar decisões ambíguas com informações incompletas. Essas são qualidades profundamente humanas, baseadas em valores e intuição, que estão muito além da capacidade atual da IA.',
        'Surgeon': 'Embora a IA possa auxiliar no diagnóstico por imagem e a robótica possa aumentar a precisão dos movimentos, a cirurgia em si requer um nível extremo de destreza manual, adaptabilidade a imprevistos anatômicos em tempo real e a capacidade de tomar decisões críticas sob pressão. A responsabilidade final e a complexidade do toque humano mantêm o risco baixo.',
        'Graphic Designer': 'A criatividade, a compreensão de nuances culturais e a empatia com o usuário são centrais para o design. Embora a IA possa gerar elementos visuais, a concepção original, a direção artística e a capacidade de traduzir emoções e conceitos complexos em soluções visuais permanecem como diferenciais humanos.',
        'Software Engineer': 'Escrever código é apenas uma parte do trabalho. A engenharia de software envolve entender as necessidades do cliente, arquitetar sistemas complexos, colaborar em equipe e resolver problemas abstratos de forma criativa. A IA pode automatizar a escrita de código repetitivo, mas a concepção e a resolução de problemas de alto nível continuam sendo tarefas humanas.',
        'Teacher': 'O ensino eficaz vai muito além da transmissão de informações. Envolve inspirar, motivar, mentorar e adaptar-se às necessidades emocionais e intelectuais de cada aluno. A empatia, a paciência e a capacidade de criar um ambiente de aprendizado seguro e estimulante são habilidades interpessoais que a IA não pode replicar.',
        'Armed forces logistics/support/administrative officer': 'Embora a IA possa otimizar a logística e tarefas administrativas, a tomada de decisões estratégicas em ambientes complexos e de alta pressão, a gestão de pessoal e a adaptação a situações imprevisíveis em contextos militares exigem julgamento humano, liderança e inteligência emocional.',
        'Sports development officer': 'Este papel exige forte interação humana, construção de relacionamentos, criatividade na concepção de programas e a capacidade de motivar e inspirar comunidades. A IA pode auxiliar na análise de dados de desempenho, mas não pode substituir a dimensão interpessoal e estratégica do desenvolvimento esportivo.',
        'Jeweller': 'O trabalho de um joalheiro ou designer de joias é altamente artesanal e criativo, envolvendo habilidades manuais finas, um senso estético apurado e a capacidade de criar peças únicas e personalizadas. A IA pode auxiliar no design ou na prototipagem, mas a arte e a precisão do trabalho manual e a conexão emocional com o cliente são insubstituíveis.',
        'Clinical biochemist': 'Bioquímicos clínicos interpretam resultados de testes laboratoriais complexos para diagnosticar e monitorar doenças. Embora a IA possa auxiliar na análise de dados, a interpretação de casos atípicos, a correlação com o histórico clínico do paciente e a tomada de decisões diagnósticas exigem conhecimento médico aprofundado, julgamento crítico e experiência humana.',
        'Therapist': 'Terapeutas fornecem suporte emocional e psicológico, exigindo empatia, escuta ativa, construção de confiança e a capacidade de navegar em complexas interações humanas. A IA pode oferecer ferramentas de apoio, mas a profundidade da conexão humana e a compreensão das nuances emocionais são insubstituíveis para a eficácia da terapia.',
        'Nutritionist': 'Nutricionistas criam planos alimentares personalizados e fornecem aconselhamento de saúde. Isso requer uma compreensão profunda das necessidades individuais, empatia, motivação e a capacidade de adaptar estratégias com base no comportamento e nas preferências do cliente. A IA pode gerar planos genéricos, mas a personalização e o suporte humano são cruciais.',
        'Medical sales representative': 'Representantes de vendas médicas constroem relacionamentos com profissionais de saúde, entendem suas necessidades e comunicam informações complexas sobre produtos. Isso exige habilidades interpessoais fortes, persuasão, conhecimento técnico e a capacidade de adaptar a abordagem a cada cliente, aspectos que a IA não consegue replicar eficazmente.'
      };

      // Return the specific explanation if available
      if (specificExplanations[title]) {
        return specificExplanations[title];
      }

      // Fallback to generic explanations if no specific one is found
      return riskType === 'high'
        ? 'Este tipo de trabalho geralmente envolve tarefas repetitivas e padronizadas, que são facilmente automatizadas por algoritmos e robôs.'
        : 'Esta profissão exige pensamento crítico, criatividade e habilidades interpessoais complexas, características que a IA atualmente não consegue replicar.';
    },
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
          this.fetchWorkersByRisk(),
          this.fetchImpactType(),
          this.fetchSectorsAtRisk(),
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

      if (sortOrder === 'desc') {
        this.highRiskJobs = data;
      } else {
        this.lowRiskJobs = data;
      }

      const chartData = {
        labels: data.map(item => {
          const title = item['Job Title'];
          const translatedTitle = this.translateTitle(title);
          return translatedTitle.length > MAX_LABEL_LENGTH
            ? translatedTitle.substring(0, MAX_LABEL_LENGTH) + '...'
            : translatedTitle;
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
      const data = response.data.sort((a, b) => b['Projected Growth (%)'] - a['Projected Growth (%)']).slice(0, 15);

      this.jobGrowth = data;

      this.jobGrowthData = {
        labels: data.map(item => item['Industry']),
        datasets: [{
          data: data.map(item => item['Projected Growth (%)']),
          backgroundColor: '#3498db',
        }]
      };
    },
    async fetchWorkersByRisk() {
      const params = { location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/workers-by-risk`, { params });
      const data = response.data;

      const riskColors = {
        'High': '#e74c3c',
        'Medium': '#f39c12',
        'Low': '#27ae60'
      };

      this.workersByRiskData = {
        labels: data.map(item => item['Risk Level']),
        datasets: [{
          data: data.map(item => item['Workers']),
          backgroundColor: data.map(item => riskColors[item['Risk Level']] || '#95a5a6'),
        }]
      };
    },
    async fetchImpactType() {
      const params = { location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/impact-type`, { params });
      const data = response.data;

      const impactColors = {
        'Increase': '#27ae60',
        'Decrease': '#e74c3c',
        'Mixed': '#f39c12'
      };

      this.impactTypeData = {
        labels: data.map(item => item['Impact Type']),
        datasets: [{
          data: data.map(item => item['Count']),
          backgroundColor: data.map(item => impactColors[item['Impact Type']] || '#95a5a6'),
        }]
      };
    },
    async fetchSectorsAtRisk() {
      const params = { location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/sectors-at-risk`, { params });
      const data = response.data;

      this.sectorsAtRiskData = {
        labels: data.map(item => item['Sector']),
        datasets: [{
          data: data.map(item => item['Workers at Risk']),
          backgroundColor: '#e74c3c',
        }]
      };
    },
    pieChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
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
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-section {
  background-color: var(--color-background-soft);
  padding: 1.5rem;
  border-radius: 8px;
  min-height: 500px; /* Ensure charts have space */
}

.analysis-section {
  background-color: var(--color-background-soft);
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: -1rem; /* Pulls it closer to the chart above */
  border-top: 1px solid var(--color-border);
}

.analysis-section h3 {
  text-align: center;
  margin-bottom: 1.5rem;
}

.analysis-section ul, .analysis-section div {
  text-align: left;
  padding: 0 1rem; /* Add some padding for better readability */
}

.analysis-section ul {
  list-style-type: none;
  padding: 0;
}

.analysis-section li {
  margin-bottom: 2rem; /* Increased spacing */
}

.analysis-section li p {
  margin-top: 0.5rem;
  font-style: italic;
  color: var(--color-text-soft);
  text-align: left; /* Ensure paragraph is left-aligned */
}

.analysis-section.full-width {
  grid-column: 1 / -1;
}

.chart-section.full-width {
  grid-column: 1 / -1;
  min-height: 650px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}
</style>