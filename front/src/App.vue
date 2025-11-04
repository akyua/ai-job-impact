<template>
  <div id="app">
    <Header @theme-changed="onThemeChanged" />
    <h1>Gráficos de Impacto de IA no Mercado de Trabalho</h1>
    <BarChart :is-dark-mode="isDarkMode" />
  </div>
</template>

<script>
import Header from './components/Header.vue'
import BarChart from './components/BarChart.vue'

export default {
  components: {
    Header,
    BarChart,
  },
  data() {
    return {
      isDarkMode: false,
    };
  },
  methods: {
    onThemeChanged(isDarkMode) {
      this.isDarkMode = isDarkMode;
    },
  },
};
</script>

<style scoped>
#app {
  text-align: center;
  min-height: 100vh;
}
h1 {
  color: var(--color-text);
}
</style>