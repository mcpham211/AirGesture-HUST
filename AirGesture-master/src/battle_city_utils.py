import pygame
import os

# --- BƯỚC 1: ĐỊNH NGHĨA MÀU SẮC (Sửa lỗi NameError) ---
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0) # Màu xe tăng của Cường
BRICK_COLOR = (165, 42, 42) # Màu gạch đỏ
STEEL_COLOR = (192, 192, 192) # Màu thép xám

class myRect(pygame.Rect):
    def __init__(self, x, y, width, height, type):
        super().__init__(x, y, width, height)
        self.type = type

walls = []

def load_level(level_name):
    global walls
    walls = []
    
    # Lấy đường dẫn chuẩn của thư mục dự án (đi từ src ngược ra ngoài)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # --- BƯỚC 2: KHÔNG TỰ THÊM .TXT ---
    # Vì file của Cường tên chính xác là "1", không có đuôi
    target_path = os.path.join(project_root, "resources", "levels", level_name)

    if os.path.exists(target_path):
        print(f"--- Đã nạp bản đồ thành công từ: {target_path} ---")
        with open(target_path, "r") as f:
            for row, line in enumerate(f.read().splitlines()):
                for col, char in enumerate(line):
                    if char == "#":
                        walls.append(myRect(col*24, row*24, 24, 24, "brick"))
                    elif char == "@":
                        walls.append(myRect(col*24, row*24, 24, 24, "steel"))
        return True
    else:
        print(f"LỖI: Python vẫn không thấy file ở: {target_path}")
        return False

# --- BƯỚC 3: HÀM CHÍNH ĐỂ CHẠY GAME (Phần bạn đang thiếu) ---
def battle_city(v, lock):
    pygame.init()
    # Khởi tạo màn hình khớp với kích thước bản đồ
    screen = pygame.display.set_mode((624, 624))
    pygame.display.set_caption("HUST K67 - AirGesture Tank Game")
    
    # Nạp bản đồ tên là "1"
    load_level("1") 
    
    # Khởi tạo vị trí xe tăng (Hình vuông màu vàng)
    # Tọa độ x=288, y=550 để xe nằm ở giữa phía dưới màn hình
    tank_rect = pygame.Rect(288, 550, 24, 24)
    
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Đọc hành động từ AI gửi sang qua multiprocessing
        action = 0
        with lock:
            action = v.value

        # Logic di chuyển dựa trên AI (Action: 1-Up, 2-Down, 3-Left, 4-Right)
        speed = 3
        if action == 1: tank_rect.y -= speed
        elif action == 2: tank_rect.y += speed
        elif action == 3: tank_rect.x -= speed
        elif action == 4: tank_rect.x += speed

        # Giới hạn xe tăng không chạy ra khỏi màn hình
        tank_rect.clamp_ip(screen.get_rect())

        # --- BẮT ĐẦU VẼ ---
        screen.fill(BLACK) # Xóa màn hình cũ bằng màu đen
        
        # Vẽ bản đồ (Gạch và Thép)
        for wall in walls:
            if wall.type == "brick":
                pygame.draw.rect(screen, BRICK_COLOR, wall)
            elif wall.type == "steel":
                pygame.draw.rect(screen, STEEL_COLOR, wall)

        # Vẽ xe tăng của Cường (Sử dụng biến YELLOW đã khai báo)
        pygame.draw.rect(screen, YELLOW, tank_rect)
        
        # Nếu AI gửi action 5 (Xòe tay), vẽ vòng tròn đỏ thể hiện đang bắn
        if action == 5:
            pygame.draw.circle(screen, (255, 0, 0), tank_rect.center, 30, 2)

        pygame.display.flip() # Cập nhật màn hình
        clock.tick(30) # Giới hạn 30 khung hình/giây
        
    pygame.quit()