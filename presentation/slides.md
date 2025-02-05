---
theme: neversink
transition: fade
color: dark
addons:
  - slidev-component-progress
layout: cover
---

# **Detecção de Rosto, Expressões Faciais e Movimentos Corporais**

---
title: Problema
color: dark
layout: section
---

# **Problema**

---
layout: image-right
---

# Problema

É esperado que sejam realizados os seguintes processos, usando o vídeo como base:
- Reconhecimento facial: Identifique e marque os rostos presentes no vídeo.
- Análise de expressões emocionais: Analise as expressões emocionais dos rostos identificados.
- Detecção de atividades: Detecte e categorize as atividades sendo realizadas no vídeo.
- Geração de resumo: Crie um resumo automático das principais atividades e emoções detectadas no vídeo.

<template v-slot:right>
<video>
<source src="../input.mp4"/>
</video>
</template>

---
layout: section
color: dark
---

# **Instalação de Pacotes**

---

# **Instalação de Pacotes**

- É configurado um ambiente virtual, depois são instaladas as dependências do projeto.

---
layout: section
color: dark
---

# **Definições Iniciais**

---

# **Definições Iniciais**

- Para os resultados das detecções, estas serão salvas na seguinte estrutura:

---
layout: section
color: dark
---

# **Solução**

---

# **Solução**

1. Executa a detecção de rostos e gera a pasta `/hog`.

   Levou ~136.830 segundos para executar.

2. Executa a detecção de emoções e gera a pasta `/emotions`.

   Levou ~237.782 segundos para executar.

3. Executa a detecção de movimentos corporais e gera a pasta `/movements`.

   Levou ~41.261 segundos para executar.

4. Coleta os arquivos `.json` gerados nas execuções anteriores e gera um relatório, enquanto imprime no terminal.

---
layout: section
color: dark
---

# **Lógica**

---

# **Lógica**

- Para os arquivos `00_face_detection.py`, `01_emotion_detection.py`, e `02_movement_detection.py`, estes possuem código semelhante. O que os diferencia são os nomes dos arquivos e pastas geradas e as funções de detecção.
- Com isso, o fluxo de cada arquivo pode ser resumido nos seguintes passos:

---

# **Função Principal (1/4)**

- Esta função é a que chama o arquivo de vídeo, executa através de uma função que permite disponibilizar o vídeo como stream, que então processa cada frame do vídeo e depois salva os resultados coletados em um `.json`.

---

# **Leitor de Stream (2/4)**

- Além de ser uma função que disponibiliza os frames do vídeo passado como um gerador, ele também repassa as tarefas para múltiplos processos executarem em paralelo.

---

# **Função de Detecção (3/4)**

- Esta função varia ao longo dos arquivos mencionados anteriormente, mas consiste em obter o frame do vídeo, converter a cor do formato que o OpenCV2 usa (BGR) para (RGB).
- Então é passado para a biblioteca de detecção, que retorna algumas informações e as coordenadas da detecção caso esta tenha sido sucedida.
- Após tal passo, é salvo a imagem detectada na respectiva pasta definida em cada arquivo.
- Depois disso, retorna estes valores.

---

# **Salvar em .json (4/4)**

- Uma simples função utilitária para salvar o dicionário do Python em um arquivo `.json`.

---
layout: section
color: dark
---

# **Relatório**

---

# **Relatório**

- O ideal é que seja executado para comprovar que o relatório foi, de fato, gerado conforme o vídeo fornecido, mas estes foram os valores obtidos:
- Para que não fosse considerado uma anomalia, cada frame foi verificado se possuía a localização da face, uma emoção predominante, e se possuia os landmarks do rosto (olho esquerdo, olho direito, nariz, lábio esquerdo, lábio direito).
