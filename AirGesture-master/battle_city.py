import tensorflow as tf
import cv2
import numpy as np
import multiprocessing as _mp
import os
import sys

# Ép TensorFlow dùng mode v1 để tránh lỗi GraphDef
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.compat.v1.disable_v2_behavior()


from src.utils import load_graph, detect_hands, predict, is_in_triangle
from src.battle_city_utils import battle_city
from src.config import RED, CYAN, YELLOW, BLUE, GREEN

tf.compat.v1.flags.DEFINE_integer("width", 640, "Screen width")
tf.compat.v1.flags.DEFINE_integer("height", 480, "Screen height")
tf.compat.v1.flags.DEFINE_float("threshold", 0.6, "Threshold for score")
tf.compat.v1.flags.DEFINE_float("alpha", 0.2, "Transparent level")
tf.compat.v1.flags.DEFINE_string("pre_trained_model_path", "src/pretrained_model.pb", "Path to model")

FLAGS = tf.compat.v1.flags.FLAGS

def main():
    # Phải đặt load_graph trong try-except để nếu lỗi nó vẫn in ra chi tiết
    try:
        graph, sess = load_graph(FLAGS.pre_trained_model_path)
        print("--- Đã load Model AI thành công ---")
    except Exception as e:
        print(f"LỖI LOAD MODEL: {e}")
        import traceback
        traceback.print_exc() # In chi tiết lỗi để mình biết sai ở đâu
        return

    cap = cv2.VideoCapture(0) # Đảm bảo số 0 là camera mặc định của máy
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FLAGS.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FLAGS.height)
    
    # 3. Chạy Game Process
    mp = _mp.get_context("spawn")
    v = mp.Value('i', 0)
    lock = mp.Lock()
    
    process = mp.Process(target=battle_city, args=(v, lock))
    process.start()
    
    x_center, y_center = int(FLAGS.width / 2), int(FLAGS.height / 2)
    radius = int(min(FLAGS.width, FLAGS.height) / 6)

    print("Hệ thống đang chạy... Nhấn 'Q' tại cửa sổ Detection để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Nhận diện
        boxes, scores, classes = detect_hands(frame_rgb, graph, sess)
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        results = predict(boxes, scores, classes, FLAGS.threshold, FLAGS.width, FLAGS.height)
        
        action = 0
        if len(results) >= 1:
            x_min, x_max, y_min, y_max, category = results[0]
            x, y = int((x_min + x_max) / 2), int((y_min + y_max) / 2)
            cv2.circle(frame, (x, y), 5, RED, -1)
            
            if category == "Closed":
                dist = np.linalg.norm((x - x_center, y - y_center))
                if dist <= radius: action = 0
                elif is_in_triangle((x, y), [(0, 0), (FLAGS.width, 0), (x_center, y_center)]): action = 1
                elif is_in_triangle((x, y), [(0, FLAGS.height), (FLAGS.width, FLAGS.height), (x_center, y_center)]): action = 2
                elif is_in_triangle((x, y), [(0, 0), (0, FLAGS.height), (x_center, y_center)]): action = 3
                elif is_in_triangle((x, y), [(FLAGS.width, 0), (FLAGS.width, FLAGS.height), (x_center, y_center)]): action = 4
            elif category == "Open": action = 5
            
            with lock: v.value = action

        # Vẽ Overlay
        overlay = frame.copy()
        cv2.circle(overlay, (x_center, y_center), radius, BLUE, -1)
        cv2.addWeighted(overlay, FLAGS.alpha, frame, 1 - FLAGS.alpha, 0, frame)
        
        cv2.imshow('Detection', frame)
        
        # Sửa waitKey để cửa sổ không bị đóng ngay
        if cv2.waitKey(1) & 0xFF == ord("q"):
            process.terminate()
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()