<template>
  <div class="about">
    <h1>Sobre o Projeto</h1>
    <p>Este é um trabalho de faculdade da matéria de Tópicos de Big Data em Python.</p>
    <p>Como projeto, resolvemos fazer um site com front-end em Vue.js e back-end em Python com PySpark, para fazermos uma análise dos dados do tema escolhido pela equipe, que é sobre o Impacto de IA no mercado de trabalho.</p>
    
    <h2>Data Sets encontrados e usados no projeto:</h2>
    <p><a href="https://www.kaggle.com/datasets/sahilislam007/ai-impact-on-job-market-20242030" target="_blank">Ai Impact on Job Market</a></p>
    <p><a href="https://www.weforum.org/publications/the-future-of-jobs-report-2025/" target="_blank">The future of Jobs report 2025</a></p>
    
    <div class="alunos">
      <h3>Alunos:</h3>
      <p>Gabriel Henrique</p>
      <p>Thiago Barbieri</p>
      <h3>Professor:</h3>
      <p>Vagner Cordeiro</p>
    </div>
  </div>
</template>

<style>
.about {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;   
  text-align: left;
  color: var(--color-text);
}

.about h1, .about h2, .about h3 {
  color: var(--color-text);
}

.alunos {
  margin-top: 20px;
}

[data-theme='dark'] .about a {
  color: #64b5f6;
}
</style>
