"""Opt-in webcam gesture recognition using MediaPipe Tasks."""

import os

from .actions import desktop_actions, execute_with_confirmation


def run_gesture_viewer() -> None:
    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError("Gesture packages are missing from the portable runtime.") from exc

    root = os.environ.get("JARVIS_ASSETS", os.getcwd())
    model_path = os.path.join(root, "assets", "gesture_recognizer.task")
    if not os.path.isfile(model_path):
        raise RuntimeError("Gesture model is not bundled at assets\\gesture_recognizer.task.")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam. Check Windows camera privacy settings.")
    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
    )
    print("Camera active locally: Open_Palm = Notepad, Victory = Calculator. Hold 1 sec; keyboard confirmation required. Q/Esc stops.")
    chosen_action = None
    previous = ""
    stable_frames = 0
    try:
        with mp.tasks.vision.GestureRecognizer.create_from_options(options) as recognizer:
            timestamp = 0
            while True:
                ok, frame = camera.read()
                if not ok:
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                timestamp += 33
                result = recognizer.recognize_for_video(image, timestamp)
                label = "No hand"
                if result.gestures and result.gestures[0]:
                    category = result.gestures[0][0]
                    label = f"{category.category_name} ({category.score:.0%})"
                    gesture = category.category_name if category.score >= 0.8 else ""
                    if gesture == previous and gesture:
                        stable_frames += 1
                    else:
                        previous, stable_frames = gesture, 1
                    if stable_frames >= 24 and gesture in {"Open_Palm", "Victory"}:
                        chosen_action = "notepad" if gesture == "Open_Palm" else "calculator"
                        break
                else:
                    previous, stable_frames = "", 0
                cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 230, 120), 2)
                cv2.imshow("Jarvis Gestures (Q/Esc to close)", frame)
                if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    if chosen_action:
        action = desktop_actions().get(chosen_action)
        if action:
            print(f"Gesture selected {chosen_action}. Proceed? [y/N]")
            answer = input("Confirm > ").strip().casefold()
            print(execute_with_confirmation(action, lambda _: answer in {"y", "yes"}))

