# 1. Problema

# 2. Otimizações iniciais

# 3. Solução
## 3.1. Detecção de rostos

face-recognition(hog modelo de detecção) + opencv2
{
  "FRAME_RESIZE_FACTOR": 0.9,
  "INPUT_FILE": "./input.1.mp4",
  "MAX_COUNT": 3326,
  "MAX_WORKERS": 12,
  "OUTPUT_DIR": "detected_faces",
  "OUTPUT_FILE": "tracked_faces.json"
}
Detecting faces: 100%|████████████████████████████████████████████████████████████| 3326/3326 [00:19<00:00, 171.78it/s]
Processing frames: 100%|███████████████████████████████████████████████████████████| 1663/1663 [02:32<00:00, 10.91it/s] 
Tracking faces: 1663it [02:52,  9.66it/s]█████████████████████████████████████████▉| 1662/1663 [02:32<00:00, 10.34it/s]
Saving JSON: 100%|██████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 199.99it/s] 
Tracked 601 faces. Data saved to tracked_faces.json.
Took 144.61160509998444s

Tive alguns problemas ao rodar o cnn, mas vi que ele conseguiu detectar o rosto da menina deitada e o da animação 3d, diferente do modelo hog

## 3.2 Detecção de emoções

deepface, usando peso `facial_expression_model_weights.h5`

{
  "FRAME_RESIZE_FACTOR": 0.9,
  "INPUT_FILE": "./input.1.mp4",
  "MAX_COUNT": 3326,
  "MAX_WORKERS": 12,
  "OUTPUT_DIR": "detected_emotions",
  "OUTPUT_FILE": "tracked_emotions.json"
}
Detecting faces: 100%|█████████████████████| 3326/3326 [00:10<00:00, 331.21it/s]
Processing frames:   0%|                               | 0/1663 [00:00<?, ?it/s]
Tracked 1663 emotions. Data saved to tracked_emotions.json.
Took 177.56159889994888s

## 3.3 Detecção de movimento

mediapipe

{
  "FRAME_RESIZE_FACTOR": 0.9,
  "INPUT_FILE": "./input.1.mp4",
  "MAX_COUNT": 3326,
  "MAX_WORKERS": 12,
  "OUTPUT_DIR": "detected_movements",
  "OUTPUT_FILE": "tracked_movements.json"
}
Detecting faces: 100%|█████████████████████| 3326/3326 [00:10<00:00, 313.16it/s]
Processing frames: 100%|████████████████████| 1663/1663 [00:17<00:00, 97.18it/s]
Saving JSON: 100%|████████████████████████████████| 1/1 [00:00<00:00,  2.16it/s]
Tracked 1663 movements. Data saved to tracked_movements.json.
Took 29.380796500016004s

## 3.4 Geração de resumo

Após gerar o .json para a detecção de rostos, emoções, e movimentos corporais, juntei todos em um dicionário.
As chaves são os frames e os valores representam os resultados de cada um