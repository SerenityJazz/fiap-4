from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
from tqdm import tqdm
from typing import List, Dict, Iterable
import cv2
import face_recognition
import json
import multiprocessing
import numpy as np
import os


MAX_COUNT = 3326
FRAME_RESIZE_FACTOR = 1
MAX_WORKERS = multiprocessing.cpu_count()
INPUT_FILE = "./input.mp4"
BASE_DIR = "hog"
OUTPUT_DIR = "detected_faces"
OUTPUT_FILE = "tracked_faces.json"

os.makedirs(os.path.join(BASE_DIR, OUTPUT_DIR), exist_ok=True)


def process_frame(
    frame: np.ndarray,
    frame_index: int,
) -> List[dict[str, float]]:
    # Usando OpenCV2, é redimensionado para 90% do tamanho original por questões de performance
    # Com isso, é usado o modelo de detecção padrão HOG, e é executado a lógica de obter as coordenadas
    # caso um ou mais rostos tenham sido detectados naquele frame.
    # Salva também o rosto detectado em um arquivo local.

    small_frame = cv2.resize(
        frame,
        (0, 0),
        fx=FRAME_RESIZE_FACTOR,
        fy=FRAME_RESIZE_FACTOR,
    )
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")

    detected_faces = []
    for loc in face_locations:
        top, right, bottom, left = loc
        face_str = f"frame{frame_index:04d}_top{top:.3f}_right{right:.3f}_bottom{bottom:.3f}_left{left:.3f}"
        detected_faces.append(
            {
                "TOP": top,
                "RIGHT": right,
                "BOTTOM": bottom,
                "LEFT": left,
            }
        )
        face_img = rgb_frame[top:bottom, left:right]

        face_filename = os.path.join(BASE_DIR, OUTPUT_DIR, f"{face_str}.jpg")
        cv2.imwrite(face_filename, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))

    return detected_faces


def stream_reader(video_source: str) -> Iterable[List[str]]:
    # Ler o vídeo e passar a detecção de faces para múltiplos processos
    # para que aumente a performance
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_iterator = tqdm(range(min(total_frames, MAX_COUNT)), desc="Detecting faces")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_frame, cap.read()[1], i)
            for i in frame_iterator
            if cap.read()[0]
        ]
        for future in tqdm(futures, desc="Processing frames"):
            yield future.result()
    cap.release()


def track_faces(video_source: str) -> Dict[int, List[str]]:
    # Função principal, executa o leitor de stream e salva o resultado
    # após percorrer todos os frames em um .json
    data = {}
    for i, detected_faces in enumerate(
        stream_reader(video_source=video_source),
    ):
        if not detected_faces:
            continue
        data[i] = detected_faces

    save_to_json(
        data=data,
        filename=os.path.join(BASE_DIR, OUTPUT_FILE),
    )
    return data


def save_to_json(data: Dict[int, List[str]], filename: str) -> None:
    # Função para salvar os dados em JSON
    with tqdm(total=1, desc="Saving JSON") as pbar:
        with open(filename, "w") as f:
            json.dump(data, f)
        pbar.update(1)


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "FRAME_RESIZE_FACTOR": FRAME_RESIZE_FACTOR,
                "INPUT_FILE": INPUT_FILE,
                "MAX_COUNT": MAX_COUNT,
                "MAX_WORKERS": MAX_WORKERS,
                "OUTPUT_DIR": OUTPUT_DIR,
                "OUTPUT_FILE": OUTPUT_FILE,
            },
            indent=2,
        )
    )

    start = perf_counter()
    tracked_faces = track_faces(INPUT_FILE)
    end = perf_counter()
    print(f"Tracked {len(tracked_faces)} faces. Data saved to {OUTPUT_FILE}.")
    print(f"Took {end - start}s")
