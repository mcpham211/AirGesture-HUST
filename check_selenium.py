from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time

# Sử dụng đường dẫn tương đối để tránh sai sót giữa các ổ đĩa
# File chromedriver.exe phải nằm cùng thư mục với file check_selenium.py này
current_dir = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(current_dir, 'chromedriver.exe')

print(f"--- Đang kiểm tra Driver tại: {driver_path} ---")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

try:
    # Trỏ trực tiếp vào file thực thi
    # Sửa dòng 18 và 19 thành:
    service = Service(executable_path=driver_path) # Thêm dấu =
    driver = webdriver.Chrome(service=service, options=options) # options=options
    
    print("Đang mở trang game...")
    driver.get('https://elvisyjlin.github.io/t-rex-runner/')
    
    print("THÀNH CÔNG RỒI!")
    time.sleep(5) 
    driver.quit()
except Exception as e:
    print(f"Vẫn lỗi. Hãy đảm bảo file tên là 'chromedriver.exe' và nằm ở: {current_dir}")
    print(f"Lỗi chi tiết: {e}")
    