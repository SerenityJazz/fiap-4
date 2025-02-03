from concurrent.futures import ProcessPoolExecutor
from deepface import DeepFace
from time import perf_counter
from tqdm import tqdm
from typing import Dict, Iterable, List
import cv2
import json
import multiprocessing
import numpy as np
import os


MAX_COUNT = 3326
# FRAME_RESIZE_FACTOR = 0.9
FRAME_RESIZE_FACTOR = 1
MAX_WORKERS = multiprocessing.cpu_count()
# INPUT_FILE = "./input.1.mp4"
INPUT_FILE = "./input.mp4"
BASE_DIR = "emotions"
OUTPUT_DIR = "detected_emotions"
OUTPUT_FILE = "tracked_emotions.json"

os.makedirs(os.path.join(BASE_DIR, OUTPUT_DIR), exist_ok=True)


def process_frame(
    frame: np.ndarray,
    frame_index: int,
) -> List[str]:
    # Reduzir para 90% do frame original
    small_frame = cv2.resize(
        frame,
        (0, 0),
        fx=FRAME_RESIZE_FACTOR,
        fy=FRAME_RESIZE_FACTOR,
    )
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Obter emoção dominante usando DeepFace
    result = DeepFace.analyze(
        rgb_frame,
        actions=["emotion"],
        enforce_detection=False,
    )

    # Salvar a emoção e posição do rosto
    detected_emotions = []
    for face in result:
        dominant_emotion = face["dominant_emotion"]
        x, y, w, h = (
            face["region"]["x"],
            face["region"]["y"],
            face["region"]["w"],
            face["region"]["h"],
        )
        emotion_str = (
            f"frame{frame_index:04d}_emotion{dominant_emotion}_x{x}_y{y}_w{w}_h{h}"
        )
        emotion_img = rgb_frame[y : y + h, x : x + w]
        emotion_filename = os.path.join(BASE_DIR, OUTPUT_DIR, f"{emotion_str}.jpg")

        # Criar um arquivo com o rosto e emoção detectada
        cv2.imwrite(
            emotion_filename,
            cv2.cvtColor(emotion_img, cv2.COLOR_RGB2BGR),
        )
        detected_emotions.append(
            {
                "DOMINANT_EMOTION": dominant_emotion,
                "X": x,
                "Y": y,
                "W": w,
                "H": h,
            }
        )
    return detected_emotions


def stream_reader(video_source: str) -> Iterable[List[str]]:
    # Ler vídeo
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_iterator = tqdm(
        range(min(total_frames, MAX_COUNT)),
        desc="Detecting emotions",
    )
    # Passar frames para múltiplos processos, detectar emoções,
    # e retornar resultados
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_frame, cap.read()[1], i)
            for i in frame_iterator
            if cap.read()[0]
        ]
        for future in tqdm(futures, desc="Processing frames"):
            yield future.result()
    cap.release()


def track_emotions(video_source: str):
    # Função principal, vê frames de vídeos, obtém resultados de
    # múltiplos processos e salva em um .json
    data = {}
    for i, detected_emotions in enumerate(
        stream_reader(video_source=video_source),
    ):
        if not detected_emotions:
            continue
        data[i] = detected_emotions

    save_to_json(
        data=data,
        filename=os.path.join(BASE_DIR, OUTPUT_FILE),
    )
    return data


def save_to_json(data: Dict[int, List[str]], filename: str) -> None:
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
    tracked_emotions = track_emotions(INPUT_FILE)
    end = perf_counter()
    print(f"Tracked {len(tracked_emotions)} emotions. Data saved to {OUTPUT_FILE}.")
    print(f"Took {end - start}s")
