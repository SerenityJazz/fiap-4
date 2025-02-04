# Entregável 4 - Detecção de rosto, expressões faciais e movimentos corporais

# 1. Problema

Link do vídeo: https://drive.usercontent.google.com/download?id=1B5PbZdUDi-r7Ac7BK3a3WdNppfQqM_Ne&export=download

Você deverá criar uma aplicação a partir do vídeo disponibilizado e que execute as seguintes tarefas:
1. Reconhecimento facial: Identifique e marque os rostos presentes no vídeo.
2. Análise de expressões emocionais: Analise as expressões emocionais dos rostos identificados.
3. Detecção de atividades: Detecte e categorize as atividades sendo realizadas no vídeo.
4. Geração de resumo: Crie um resumo automático das principais atividades e emoções detectadas no vídeo.

# 2. Instalação de pacotes

```sh
python -m venv venv   # Caso queira instalar em um ambiente virtual
./venv/bin/activate   # Caso estiver em um Windows, usar .\venv\Scripts\activate

pip install deepface mediapipe face-recognition

# Tive problemas com a biblioteca 'dlib', então tive que baixar binário por fora
# Usei executável para Python 3.10 desse repositório
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x

# Depois de baixado, instalei apontando para o arquivo baixado localmente
# pip install ./<nome do arquivo dlib-versao.whl>
# pip install tf-keras
```

# 3. Definições iniciais

O vídeo fornecido contém 3326 frames, onde será referenciado como `input.mp4`

Para os resultados das detecções, estas serão salvas na seguinte estrutura:

```
----/
  |
  |
  |-/emotions
  |   |
  |   |-/detected_emotions
  |   |   |
  |   |   |- *.jpg  # Imagens com os rostos, e o nome do arquivo
  |   |               contendo coordenada e emoção predominante
  |   |
  |   |-tracked_emotions.json   # Arquivo contendo cada frame
  |                             detectado como chave, e as
  |                             coordenadas como valores
  |
  |-/hog
  |   |
  |   |-/detected_faces
  |   |   |
  |   |   |- *.jpg  # Imagens com os rostos, e o nome do arquivo
  |   |               contendo coordenada
  |   |
  |   |-tracked_faces.json   # Arquivo contendo cada frame
  |                            detectado como chave, e as
  |                            coordenadas dos rostos como
  |                            valores
  |
  |-/movements
  |   |
  |   |-/detected_movements
  |   |   |
  |   |   |- *.jpg  # Imagens com os rostos, e o nome do arquivo
  |   |               contendo coordenada
  |   |
  |   |-tracked_movements.json   # Arquivo contendo cada frame
  |                                detectado como chave, e as
  |                                coordenadas dos pontos corporais como
  |                                valores
  |
```

# 4. Solução

```sh
# Executa a detecção de rostos e gera a pasta /hog
python 00_face_detection.py
> Levou ~136.830 segundos para executar

# Executa a detecção de emoções e gera a pasta /emotions
python 01_emotion_detection.py

# Executa a detecção de movimentos corporais e gera a pasta /movements
python 02_movement_detection.py

# Coleta os arquivos .json gerados nas execuções anteriores e gera um relatório,
# enquanto imprime no terminal
python 03_auto_summary.py
```

# 5. Lógica

Para os arquivos `00_face_detection.py`, `01_emotion_detection.py`, e `02_movement_detection.py`, estes possuem código semelhante. O que os diferencia são os nomes dos arquivos e pastas geradas e as funções de detecção.
Com isso, o fluxo de cada arquivo pode ser resumido nos seguintes passos:

## 5.1 Função principal

Esta função é a que chama o arquivo de vídeo, executa através de uma função que permite disponibilizar o vídeo como stream, que então processa cada frame do vídeo e depois salva os resultados coletados em um .json

## 5.2 Leitor de stream

Além de ser uma função que disponibiliza os frames do vídeo passado como um gerador, ele também repassa as tarefas para múltiplos processos executarem em paralelo.

## 5.3 Função de detecção

Esta função varia ao longo dos arquivos mencionados anteriormente, mas consiste em obter o frame do vídeo, converter a cor do formato que o OpenCV2 usa (BGR) para (RGB)

Então é passado para a biblioteca de detecção, que retorna algumas informações e as coordenadas da detecção caso esta tenha sido sucedida.

Após tal passo, é salvo a imagem detectada na respectiva pasta definida em cada arquivo.

Depois disso, retorna estes valores.

## 5.4 Salvar em .json

Uma simples função utilitária para salvar o dicionário do Python em um arquivo .json

# 6. Relatório

O ideal é que seja executado para comprovar que o relatório foi, de fato, gerado conforme o vídeo fornecido, mas estes foram os valores obtidos:

| GENERAL |
| - |
| Total of 607 frames |
| Total of 713 face anomalies |
| Total of 0 emotion anomalies |
| Total of 2006 movement anomalies |

| FACES |
| - |
| Total of 610 faces |

| EMOTIONS |
| - |
| 226 happy |
| 212 neutral |
| 75 sad |
| 11 angry |
| 66 surprise |
| 101 fear |
| Total of 691 emotions |

| MOVEMENTS |
| - |
| 29 arms_up movements |
| 301 sideways movements |
| Total of 9829 landmarks detected      |

> Para que não fosse considerado uma anomalia, cada frame foi verificado se possuia a localização da face, uma emoção predominante, e se possuia os landmarks do rosto (olho esquerdo, olho direito, nariz, lábio esquerdo, lábio direito)