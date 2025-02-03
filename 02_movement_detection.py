from concurrent.futures import ProcessPoolExecutor
from mediapipe.python.solutions import pose, drawing_utils
from time import perf_counter
from tqdm import tqdm
from typing import Dict, Iterable, List
import cv2
import json
import multiprocessing
import numpy as np
import os


MAX_COUNT = 3326
FRAME_RESIZE_FACTOR = 1
MAX_WORKERS = multiprocessing.cpu_count()
INPUT_FILE = "./input.mp4"
BASE_DIR = "movements"
OUTPUT_DIR = "detected_movements"
OUTPUT_FILE = "tracked_movements.json"

os.makedirs(os.path.join(BASE_DIR, OUTPUT_DIR), exist_ok=True)


mp_pose = pose.Pose()


def process_frame(frame: np.ndarray, frame_index: int) -> Dict[str, bool]:
    # Reduzir para 90% do frame original
    small_frame = cv2.resize(
        frame,
        (0, 0),
        fx=FRAME_RESIZE_FACTOR,
        fy=FRAME_RESIZE_FACTOR,
    )
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(rgb_frame)

    # Obter partes do corpo e salvar a coordenada de cada uma
    detected_landmarks = {}

    if results.pose_landmarks:
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            # Guardar apenas se a parte estiver visível
            if landmark.visibility > 0.5:
                landmark_name = pose.PoseLandmark(idx).name
                detected_landmarks[landmark_name] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                }
        body_filename = os.path.join(BASE_DIR, OUTPUT_DIR, f"{frame_index}.jpg")
        img = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        drawing_utils.draw_landmarks(img, results.pose_landmarks, pose.POSE_CONNECTIONS)
        cv2.imwrite(body_filename, img)

    return {
        f"frame{frame_index:04d}_landmarks": len(detected_landmarks),
        "landmarks": detected_landmarks,
    }


def stream_reader(video_source: str) -> Iterable[List[str]]:
    # Ler vídeo
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_iterator = tqdm(
        range(min(total_frames, MAX_COUNT)),
        desc="Detecting body parts",
    )
    # Passar frames para múltiplos processos, detectar partes de corpo,
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


def track_movements(video_source: str):
    # Função principal, vê frames de vídeos, obtém resultados de
    # múltiplos processos e salva em um .json
    data = {}
    for i, detected_movements in enumerate(
        stream_reader(video_source=video_source),
    ):
        if not detected_movements:
            continue
        data[i] = detected_movements

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
    tracked_movements = track_movements(INPUT_FILE)
    end = perf_counter()
    print(f"Tracked {len(tracked_movements)} frames with body parts detected. Data saved to {OUTPUT_FILE}.")
    print(f"Took {end - start}s")
