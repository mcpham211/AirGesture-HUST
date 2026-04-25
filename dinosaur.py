"""
@author: Viet Nguyen <nhviet1009@gmail.com>
Sửa đổi bởi: Gemini - Hỗ trợ Cường (HUST) kết nối luồng Dino
"""
import tensorflow.compat.v1 as tf
import cv2
import numpy as np
import multiprocessing as _mp
import time
import os 
from src.utils import load_graph, detect_hands, predict, dinosaur
from src.config import RED, GREEN, YELLOW

# Tắt các thông báo rác của TF
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.disable_v2_behavior()

tf.compat.v1.flags.DEFINE_integer("width", 640, "Screen width")
tf.compat.v1.flags.DEFINE_integer("height", 480, "Screen height")
tf.compat.v1.flags.DEFINE_float("threshold", 0.6, "Threshold for score")
tf.compat.v1.flags.DEFINE_float("alpha", 0.3, "Transparent level")
tf.compat.v1.flags.DEFINE_string("pre_trained_model_path", "src/pretrained_model.pb", "Path to pre-trained model")

FLAGS = tf.compat.v1.flags.FLAGS

def main():
    graph, sess = load_graph(FLAGS.pre_trained_model_path)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FLAGS.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FLAGS.height)
    
    # Khởi tạo multiprocessing context
    mp = _mp.get_context("spawn")
    v = mp.Value('i', 0)
    lock = mp.Lock()
    
    # Khởi động luồng Game (Dinosaur)
    process = mp.Process(target=dinosaur, args=(v, lock))
    process.start()
    
    print("--- HỆ THỐNG ĐANG KHỞI CHẠY ---")
    print("Lưu ý: Giơ tay 'Open' ở vùng VÀNG để Nhảy")

    while True:
        key = cv2.waitKey(10)
        if key == ord("q"):
            process.terminate() # Đóng luồng game khi thoát
            break
            
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Nhận diện bàn tay
        boxes, scores, classes = detect_hands(frame_rgb, graph, sess)
        results = predict(boxes, scores, classes, FLAGS.threshold, FLAGS.width, FLAGS.height)

        action = 0  # Mặc định là chạy (Run)
        text = "Run"

        if len(results) >= 1:
            # Lấy kết quả bàn tay đầu tiên
            x_min, x_max, y_min, y_max, category = results[0]
            x = int((x_min + x_max) / 2)
            y = int((y_min + y_max) / 2)
            
            # Vẽ điểm định vị tay
            cv2.circle(frame, (x, y), 10, RED, -1)
            
            # LOGIC ĐIỀU KHIỂN:
            # 1. Nếu tay Mở và nằm ở nửa trên (vùng màu vàng) -> NHẢY
            if category == "Open" and y < FLAGS.height / 2:
                action = 1 
                text = "JUMP!"
            # 2. Nếu tay Mở và nằm ở nửa dưới -> CÚI
            elif category == "Open" and y >= FLAGS.height / 2:
                action = 2
                text = "DUCK!"
            # 3. Nếu tay nắm (Closed) -> CHẠY BÌNH THƯỜNG
            else:
                action = 0
                text = "Run"

            # Gửi hành động vào luồng Game thông qua biến v dùng chung
            with lock:
                v.value = action
            
            # Hiển thị trạng thái lên màn hình camera
            cv2.putText(frame, text, (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2)

        # Vẽ vùng nhận diện màu vàng (nửa trên)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (FLAGS.width, int(FLAGS.height / 2)), YELLOW, -1)
        cv2.addWeighted(overlay, FLAGS.alpha, frame, 1 - FLAGS.alpha, 0, frame)
        
        cv2.imshow('Detection - Tay phai vung VANG de NHAY', frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()