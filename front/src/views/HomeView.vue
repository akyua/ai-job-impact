<template>
  <div>
    <h1>Gráficos de Impacto de IA no Mercado de Trabalho</h1>
    <BarChart :is-dark-mode="isDarkMode" />
  </div>
</template>

<script>
import BarChart from '../components/BarChart.vue'

export default {
  components: {
    BarChart,
  },
  props: {
    isDarkMode: Boolean,
  },
};
</script>

<style scoped>
h1 {
  color: var(--color-text);
}
</style>
