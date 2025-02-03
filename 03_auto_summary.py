import json
import os

EMOTION_FILE = "emotions/tracked_emotions.json"
FACE_FILE = "hog/tracked_faces.json"
MOVEMENT_FILE = "movements/tracked_movements.json"
OUTPUT_FILE = "summary.json"


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def has_face(landmarks: dict) -> bool:
    required_keys = [
        "RIGHT_EYE",
        "LEFT_EYE",
        "NOSE",
        "MOUTH_LEFT",
        "MOUTH_RIGHT",
    ]
    return all(landmarks.get(key) for key in required_keys)


def remove_anomalies(
    emotions: dict,
    faces: dict,
    movements: dict,
) -> tuple[dict, dict[str, int]]:
    all_frames = map(str, range(3326))

    summary = {}

    face_anomalies = 0
    emotion_anomalies = 0
    movement_anomalies = 0

    for frame in all_frames:
        frame_faces = faces.get(frame, {})
        frame_emotions = emotions.get(frame, [])
        frame_movements = movements.get(frame, {}).get("landmarks", {})

        # Considerar como anomalia caso:
        #   Não encontrar rosto
        #   Não detectar emoção
        #   Não detectar partes do rosto (olhos, nariz, boca)

        if not has_face(frame_movements):
            print(f"[{frame}] Anomaly - no face detected within body parts, skipping")
            movement_anomalies += 1
            continue
        if not frame_emotions:
            print(f"[{frame}] Anomaly - no emotions, skipping")
            emotion_anomalies += 1
            continue
        if not frame_faces:
            print(f"[{frame}] Anomaly - no faces, skipping")
            face_anomalies += 1
            continue

        summary[frame] = {
            "emotions": frame_emotions,
            "faces": frame_faces,
            "movements": frame_movements,
        }

    anomalies = {
        "faces": face_anomalies,
        "emotions": emotion_anomalies,
        "movements": movement_anomalies,
    }

    return summary, anomalies


def get_unique_emotions(summary: dict) -> dict:
    unique_emotions = {}
    for frame in summary:
        emotions = summary[frame].get("emotions", [])
        for emo in emotions:
            e = emo["DOMINANT_EMOTION"]
            if e not in unique_emotions:
                unique_emotions[e] = 0
            unique_emotions[e] += 1
    return unique_emotions


def has_both_arms_up(movements: dict) -> bool:
    left_elbow = movements.get("LEFT_ELBOW", {})
    right_elbow = movements.get("RIGHT_ELBOW", {})
    left_shoulder = movements.get("LEFT_SHOULDER", {})
    right_shoulder = movements.get("RIGHT_SHOULDER", {})

    left_arm_up = left_elbow.get("y", 0) > left_shoulder.get("y", 0)
    right_arm_up = right_elbow.get("y", 0) > right_shoulder.get("y", 0)
    return left_arm_up and right_arm_up


def is_sideways(movements: dict) -> bool:
    left_eye = movements.get("LEFT_EYE", {})
    right_eye = movements.get("RIGHT_EYE", {})
    left_shoulder = movements.get("LEFT_SHOULDER", {})
    right_shoulder = movements.get("RIGHT_SHOULDER", {})

    left_eye_past_shoulder = left_eye.get("x", 0) < left_shoulder.get("x", 0)
    right_eye_past_shoulder = right_eye.get("x", 0) > right_shoulder.get("x", 0)
    return left_eye_past_shoulder or right_eye_past_shoulder


def get_custom_movements(summary: dict) -> dict:
    result = {
        "arms_up": {
            "active": False,
            "count": 0,
        },
        "sideways": {
            "active": False,
            "count": 0,
        },
    }
    for frame in summary:
        movements: dict[str, dict[str, float]] = summary[frame]["movements"]

        # Cotovelos acima do ombro representa braços levantados
        if has_both_arms_up(movements):
            if not result["arms_up"]["active"]:
                result["arms_up"]["active"] = True
                result["arms_up"]["count"] += 1
            else:
                result["arms_up"]["active"] = False

        # De lado, caso o olho esteja mais longe do que ombro
        if is_sideways(movements):
            if not result["sideways"]["active"]:
                result["sideways"]["active"] = True
                result["sideways"]["count"] += 1
            else:
                result["sideways"]["active"] = False

    return result


if __name__ == "__main__":
    all_emotions = load_json(EMOTION_FILE)
    all_faces = load_json(FACE_FILE)
    all_movements = load_json(MOVEMENT_FILE)

    summary, anomalies = remove_anomalies(
        emotions=all_emotions,
        faces=all_faces,
        movements=all_movements,
    )

    print("[GENERAL]".ljust(25, "*").rjust(40, "*"))
    print("Total of", len(summary), "frames")
    print("Total of", anomalies["faces"], "face anomalies")
    print("Total of", anomalies["emotions"], "emotion anomalies")
    print("Total of", anomalies["movements"], "movement anomalies")

    print("[FACES]".ljust(25, "*").rjust(40, "*"))
    print("Total of", sum([len(i["faces"]) for i in summary.values()]), "faces")

    print("[EMOTIONS]".ljust(25, "*").rjust(40, "*"))
    unique_emotions = get_unique_emotions(summary=summary)
    for emotion in unique_emotions:
        print(unique_emotions[emotion], emotion)
    print("Total of", sum([len(i["emotions"]) for i in summary.values()]), "emotions")

    print("[MOVEMENTS]".ljust(25, "*").rjust(40, "*"))
    custom_movements = get_custom_movements(summary=summary)
    for custom in custom_movements:
        print(custom_movements[custom]["count"], custom, "movements")
    print(
        "Total of",
        sum([len(i["movements"]) for i in summary.values()]),
        "landmarks detected",
    )

    with open(OUTPUT_FILE, "w") as f:
        json.dump(summary, f)
