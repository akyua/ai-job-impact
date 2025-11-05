<template>
  <div id="app">
    <Header @theme-changed="onThemeChanged" />
    <router-view :is-dark-mode="isDarkMode" />
  </div>
</template>

<script>
import Header from './components/Header.vue'


export default {
  components: {
    Header,
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