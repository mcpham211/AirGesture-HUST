"""
@author: Viet Nguyen <nhviet1009@gmail.com>

"""
import numpy as np
import time
import tensorflow as tf
import os
import cv2
from time import sleep
from src.config import HAND_GESTURES
# Tắt cảnh báo log của TensorFlow để Terminal gọn hơn
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.disable_v2_behavior()

def load_graph(model_path):
    # Dùng đường dẫn đầy đủ của compat.v1 để không bao giờ bị lỗi 'module has no attribute'
    # Lưu ý: PHẢI CÓ .compat.v1. ở giữa
    graph_def = tf.compat.v1.GraphDef() 
    
    with tf.io.gfile.GFile(model_path, "rb") as f:
        graph_def.ParseFromString(f.read())

    with tf.compat.v1.Graph().as_default() as graph:
        tf.compat.v1.import_graph_def(graph_def, name="")
    
    # Session cũng phải dùng bản v1
    sess = tf.compat.v1.Session(graph=graph)
    return graph, sess

def detect_hands(image, graph, sess):
    # Lấy các tensor đầu ra từ graph v1
    image_tensor = graph.get_tensor_by_name('image_tensor:0')
    boxes = graph.get_tensor_by_name('detection_boxes:0')
    scores = graph.get_tensor_by_name('detection_scores:0')
    classes = graph.get_tensor_by_name('detection_classes:0')
    num_detections = graph.get_tensor_by_name('num_detections:0')

    image_expanded = np.expand_dims(image, axis=0)
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_expanded})

    return np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes)

def predict(boxes, scores, classes, threshold, width, height):
    results = []
    for i in range(len(scores)):
        if scores[i] > threshold:
            ymin, xmin, ymax, xmax = boxes[i]
            left, right, top, bottom = xmin * width, xmax * width, ymin * height, ymax * height
            category = "Closed" if classes[i] == 1 else "Open"
            results.append([left, right, top, bottom, category])
    return results

def is_in_triangle(point, tri):
    def area(p1, p2, p3):
        return abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])) / 2.0)
    p = point
    a = area(tri[0], tri[1], tri[2])
    a1 = area(p, tri[0], tri[1])
    a2 = area(p, tri[1], tri[2])
    a3 = area(p, tri[2], tri[0])
    return abs(a - (a1 + a2 + a3)) < 0.1

def mario(v, lock):
    import gym_super_mario_bros
    from nes_py.wrappers import JoypadSpace
    from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
    import gym
    env = gym_super_mario_bros.make('SuperMarioBros-1-1-v0')
    env = JoypadSpace(env, COMPLEX_MOVEMENT)
    done = True
    while True:
        if done:
            env.reset()
            with lock:
                v.value = 0
        with lock:
            u = v.value
        step_result = env.step(u)
        if len(step_result) == 5:
            _, _, done, _, _ = step_result
        else:
            _, _, done, _ = step_result
        env.render()
        sleep(0.01)

def dinosaur(v, lock):
    # CHỜ ĐỂ CAMERA VÀ CỬ CHỈ SẴN SÀNG
    print("Hệ thống: Đang đợi tiến trình Camera (dinosaur.py) ổn định...")
    time.sleep(5)
    try:
        import gym
        import gym_chrome_dino
        from gym_chrome_dino.utils.wrappers import make_dino
        print("Hệ thống: Bắt đầu khởi tạo môi trường Chrome Dino qua Selenium...")
        env = gym.make('ChromeDino-v0', render=True)
        env = make_dino(env, timer=True, frame_stack=True)
        # Đợi thêm một lát để đảm bảo Selenium đã chuyển từ 404/tab trắng sang trang game
        time.sleep(3)
        done = True
        print("Hệ thống: KẾT NỐI THÀNH CÔNG. Bắt đầu nhận diện cử chỉ tay!")
        while True:
            if done:
                env.reset()
                with lock:
                    v.value = 0
            # --- LUỒNG NHẬN DỮ LIỆU TỪ DINOSAUR.PY ---
            with lock:
                u = v.value
            # Debug: In ra Terminal nếu nhận được lệnh Nhảy (1) hoặc Cúi (2)
            if u == 1:
                print(">>> GAME: Đang thực hiện NHẢY (u=1)")
            elif u == 2:
                print(">>> GAME: Đang thực hiện CÚI (u=2)")
            # Gửi hành động vào môi trường game
            step_result = env.step(u)
            if len(step_result) == 5:
                _, _, done, _, _ = step_result
            else:
                _, _, done, _ = step_result
            # Nghỉ một chút để luồng Detection có thể ghi dữ liệu vào biến v
            time.sleep(0.015)
    except Exception as e:
        print(f"Lỗi nghiêm trọng tại src/utils.py: {e}")
        
def battle_city(v, lock):
    """
    Hàm điều khiển luồng nhận cho game Battle City
    Dành cho Cường (HUST) - Kết nối biến v với logic xe tăng
    """
    from src.battle_city_utils import BattleCity
    import pygame

    # Khởi tạo đối tượng game
    game = BattleCity()
    
    print("Hệ thống: Đang khởi tạo môi trường Battle City...")
    time.sleep(2)
    print("Hệ thống: KẾT NỐI THÀNH CÔNG. Dùng tay điều khiển xe tăng!")

    while True:
        # 1. Lấy hành động u từ luồng Detection gửi sang
        with lock:
            u = v.value
        
        # 2. Debug lệnh nhận được để Cường dễ theo dõi trên Terminal
        if u != 0:
            actions = {1: "UP", 2: "DOWN", 3: "LEFT", 4: "RIGHT", 5: "FIRE"}
            print(f">>> BATTLE CITY: Thực hiện lệnh {actions.get(u, 'STAY')}")

        # 3. Đưa lệnh u vào hàm cập nhật của game
        # Lưu ý: Hàm game.step hoặc game.update tùy thuộc vào cấu trúc file battle_city_utils.py của bạn
        game.step(u)
        
        # 4. Render lại khung hình game
        game.render()
        
        # Tốc độ phản hồi của xe tăng (0.01s là đủ mượt)
        time.sleep(0.01)