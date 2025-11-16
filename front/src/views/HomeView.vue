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
        <h2>Top 15 Empregos com Maior Pontuação de Segurança (%)</h2>
        <BarChart :chartData="lowRiskJobsData" :chartOptions="lowRiskHorizontalChartOptions" :isDarkMode="isDarkMode" />
      </section>

      <section class="analysis-section">
        <h3>Análise dos 3 Principais Empregos de Baixo Risco</h3>
        <ul>
          <li v-for="job in top3LowRiskJobs" :key="job['Job Title']">
            <strong>{{ translateTitle(job['Job Title']) }} (Pontuação de Segurança: {{ job['Safety Score (%)'].toFixed(2) }}%)</strong>
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
        <h2>Distribuição de Trabalhadores por Setor</h2>
        <BarChart :chartData="workersByIndustryData" :chartOptions="workersByIndustryChartOptions" :isDarkMode="isDarkMode" />
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
const MAX_LABEL_LENGTH = 25;

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
  'Designer, jewellery': 'Designer de Joias',
  'Clinical biochemist': 'Bioquímico(a) Clínico(a)',
  'Therapist': 'Terapeuta',
  'Nutritionist': 'Nutricionista',
  'Medical sales representative': 'Representante de Vendas Médicas',
  'Banker': 'Bancário(a)',
  'Electrical Engineer': 'Engenheiro(a) Eletricista',
  'Marine Scientist': 'Cientista Marinho(a)'
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
      workersByIndustryData: { labels: [], datasets: [] },
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
        layout: { padding: { left: 25, right: 50 } },
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
          },
          datalabels: {
            anchor: 'end',
            align: 'end',
            formatter: (value) => `${value.toFixed(2)}%`,
            color: textColor,
            font: {
              weight: 'bold'
            }
          }
        }
      };
    },
    lowRiskHorizontalChartOptions() {
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { left: 25, right: 50 } },
        scales: {
          x: { min: 0, max: 100, ticks: { color: textColor } },
          y: { ticks: { color: textColor } }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Pontuação de Segurança: ${context.parsed.x.toFixed(2)}%`
            }
          },
          datalabels: {
            anchor: 'end',
            align: 'end',
            formatter: (value) => `${value.toFixed(2)}%`,
            color: textColor,
            font: {
              weight: 'bold'
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
          },
          datalabels: {
            display: false
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
              label: (context) => `Trabalhadores: ${context.parsed.y.toLocaleString()}`
            }
          },
          datalabels: {
            display: false
          }
        }
      };
    },
    workersByIndustryChartOptions() {
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
                return (value / 1000000).toFixed(1) + 'M';
              }
            }
          } 
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Trabalhadores: ${context.parsed.y.toLocaleString()}`
            }
          },
          datalabels: {
            display: false
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
    translateIndustry(industry) {
      const industryTranslations = {
        'Health': 'Saúde',
        'IT': 'TI',
        'Healthcare': 'Cuidados de Saúde',
        'Entertainment': 'Entretenimento',
        'Retail': 'Varejo',
        'Finance': 'Finanças',
        'Manufacturing': 'Indústria',
        'Education': 'Educação',
        'Transportation': 'Transporte',
        'Services': 'Serviços',
        'Production': 'Produção',
        'Office and Administrative Support': 'Suporte de Escritório e Administrativo',
        'Administrative': 'Administrativo',
        'Sales and Related': 'Vendas e Relacionados',
        'Education, Legal, Community Service, Arts, and Media': 'Educação',
      };
      return industryTranslations[industry] || industry;
    },
    getRiskExplanation(job, riskType) {
      const title = job['Job Title'];
      
      const specificExplanations = {
        'Telemarketing Operator': 'Operadores de telemarketing realizam chamadas padronizadas seguindo roteiros pré-definidos. A IA pode automatizar completamente esse processo com chatbots de voz avançados, reconhecimento de fala e sistemas de resposta automática, eliminando a necessidade de intervenção humana para a maioria das interações.',
        'Car, Taxi and Van Drivers': 'Motoristas de táxi e carros particulares dirigem veículos em rotas urbanas. A condução é altamente automatizável com veículos autônomos que já demonstraram capacidade superior em testes, especialmente em ambientes urbanos estruturados, reduzindo significativamente a necessidade de motoristas humanos.',
        'Business Services Agents': 'Agentes de serviços empresariais realizam tarefas administrativas e de atendimento ao cliente. Muitas dessas funções envolvem processamento de dados rotineiro, consultas padronizadas e resolução de problemas comuns, que podem ser altamente automatizados por sistemas de IA e chatbots inteligentes.',

        'Music Therapist': 'Terapeutas musicais usam música como ferramenta terapêutica para tratamento emocional e psicológico. A combinação única de conhecimento musical, sensibilidade emocional e capacidade de conectar artisticamente com pacientes torna esta profissão profundamente humana e difícil de automatizar.',
        'Managing Directors and Chief Executives': 'Diretores executivos e gerentes tomam decisões estratégicas complexas, lidam com incertezas organizacionais e gerenciam relacionamentos interpessoais complexos. Essas habilidades executivas superiores exigem julgamento humano, intuição e inteligência emocional que a IA atual não consegue replicar.',
        'Creative Artists': 'Artistas criativos produzem obras originais que expressam ideias, emoções e perspectivas culturais únicas. A criatividade artística autêntica, a inovação cultural e a expressão pessoal individual são qualidades essencialmente humanas que transcendem as capacidades atuais da IA.',

        'Chief Executive': 'A liderança executiva exige visão estratégica, negociação complexa, inteligência emocional para gerir pessoas e tomar decisões ambíguas com informações incompletas. Essas são qualidades profundamente humanas, baseadas em valores e intuição, que estão muito além da capacidade atual da IA.',
        'Surgeon': 'Embora a IA possa auxiliar no diagnóstico por imagem e a robótica possa aumentar a precisão dos movimentos, a cirurgia em si requer um nível extremo de destreza manual, adaptabilidade a imprevistos anatômicos em tempo real e a capacidade de tomar decisões críticas sob pressão. A responsabilidade final e a complexidade do toque humano mantêm o risco baixo.',
        'Graphic Designer': 'A criatividade, a compreensão de nuances culturais e a empatia com o usuário são centrais para o design. Embora a IA possa gerar elementos visuais, a concepção original, a direção artística e a capacidade de traduzir emoções e conceitos complexos em soluções visuais permanecem como diferenciais humanos.',
        'Software Engineer': 'Escrever código é apenas uma parte do trabalho. A engenharia de software envolve entender as necessidades do cliente, arquitetar sistemas complexos, colaborar em equipe e resolver problemas abstratos de forma criativeis. A IA pode automatizar a escrita de código repetitivo, mas a concepção e a resolução de problemas de alto nível continuam sendo tarefas humanas.',
        'Teacher': 'O ensino eficaz vai muito além da transmissão de informações. Envolve inspirar, motivar, mentorar e adaptar-se às necessidades emocionais e intelectuais de cada aluno. A empatia, a paciência e a capacidade de criar um ambiente de aprendizado seguro e estimulante são habilidades interpessoais que a IA não pode replicar.',
        'Armed forces logistics/support/administrative officer': 'Embora a IA possa otimizar a logística e tarefas administrativas, a tomada de decisões estratégicas em ambientes complexos e de alta pressão, a gestão de pessoal e a adaptação a situações imprevisíveis em contextos militares exigem julgamento humano, liderança e inteligência emocional.',
        'Sports development officer': 'Este papel exige forte interação humana, construção de relacionamentos, criatividade na concepção de programas e a capacidade de motivar e inspirar comunidades. A IA pode auxiliar na análise de dados de desempenho, mas não pode substituir a dimensão interpessoal e estratégica do desenvolvimento esportivo.',
        'Jeweller': 'O trabalho de um joalheiro ou designer de joias é altamente artesanal e criativo, envolvendo habilidades manuais finas, um senso estético apurado e a capacidade de criar peças únicas e personalizadas. A IA pode auxiliar no design ou na prototipagem, mas a arte e a precisão do trabalho manual e a conexão emocional com o cliente são insubstituíveis.',
        'Clinical biochemist': 'Bioquímicos clínicos interpretam resultados de testes laboratoriais complexos para diagnosticar e monitorar doenças. Embora a IA possa auxiliar na análise de dados, a interpretação de casos atípicos, a correlação com o histórico clínico do paciente e a tomada de decisões diagnósticas exigem conhecimento médico aprofundado, julgamento crítico e experiência humana.',
        'Therapist': 'Terapeutas fornecem suporte emocional e psicológico, exigindo empatia, escuta ativa, construção de confiança e a capacidade de navegar em complexas interações humanas. A IA pode oferecer ferramentas de apoio, mas a profundidade da conexão humana e a compreensão das nuances emocionais são insubstituíveis para a eficácia da terapia.',
        'Nutritionist': 'Nutricionistas criam planos alimentares personalizados e fornecem aconselhamento de saúde. Isso requer uma compreensão profunda das necessidades individuais, empatia, motivação e a capacidade de adaptar estratégias com base no comportamento e das preferências do cliente. A IA pode gerar planos genéricos, mas a personalização e o suporte humano são cruciais.',
        'Medical sales representative': 'Representantes de vendas médicas constroem relacionamentos com profissionais de saúde, entendem suas necessidades e comunicam informações complexas sobre produtos. Isso exige habilidades interpessoais fortes, persuasão, conhecimento técnico e a capacidade de adaptar a abordagem a cada cliente, aspectos que a IA não consegue replicar eficazmente.'
      };

      if (specificExplanations[title]) {
        return specificExplanations[title];
      }

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
          this.fetchWorkersByIndustry(),
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
          data: data.map(item => sortOrder === 'asc' ? item['Safety Score (%)'] : item['Automation Risk (%)']),
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
        labels: data.map(item => this.translateIndustry(item['Industry'])),
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
    async fetchWorkersByIndustry() {
      const params = { location: this.selectedLocation };
      const response = await axios.get(`${API_BASE_URL}/workers-by-industry`, { params });
      const data = response.data;

      this.workersByIndustryData = {
        labels: data.map(item => this.translateIndustry(item['Industry'])),
        datasets: [{
          data: data.map(item => item['Workers']),
          backgroundColor: '#3498db',
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
      const textColor = this.isDarkMode ? 'white' : 'black';
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          datalabels: {
            color: '#000',
            formatter: (value, context) => {
              return value.toLocaleString();
            },
            font: {
              weight: 'bold',
              size: 14
            }
          },
          legend: {
            labels: {
              color: textColor
            }
          }
        }
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
  min-height: 500px;
}

.analysis-section {
  background-color: var(--color-background-soft);
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: -1rem;
  border-top: 1px solid var(--color-border);
}

.analysis-section h3 {
  text-align: center;
  margin-bottom: 1.5rem;
}

.analysis-section ul, .analysis-section div {
  text-align: left;
  padding: 0 1rem;
}

.analysis-section ul {
  list-style-type: none;
  padding: 0;
}

.analysis-section li {
  margin-bottom: 2rem;
}

.analysis-section li p {
  margin-top: 0.5rem;
  font-style: italic;
  color: var(--color-text-soft);
  text-align: left;
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