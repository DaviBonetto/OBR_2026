
import tkinter
from datetime import timedelta
from multiprocessing import Process, shared_memory
import threading
import time
import numpy as np
from tkinter import *
import customtkinter as ctk
import cv2
import psutil
from PIL import Image
from numba import njit
import os

# Mock ConfigManager and Timer to avoid imports
class MockConfigManager:
    def __init__(self, config_file): pass
    def read_variable(self, section, variable): return None
    def write_variable(self, section, variable, value): pass

class MockTimer:
    def __init__(self): 
        self.timers = {}
    def set_timer(self, name, duration): 
        self.timers[name] = time.time() + duration
    def get_timer(self, name): 
        if name not in self.timers: return False
        return time.time() < self.timers[name]

# Mock MP variables
class MockValue:
    def __init__(self, val): self.value = val

# Define globals expected by App
config_manager = MockConfigManager('config.ini')
timer = MockTimer()

# Import new movement logic
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../main")
try:
    from movement_utils import calculate_wheel_speeds, normalize_speeds
except ImportError:
    # Fallback if file not finding correct path in dev
    def calculate_wheel_speeds(s, a, w, r=-1): return 0,0,0,0
    def normalize_speeds(fl,fr,bl,br, m): return fl,fr,bl,br

cam_1_stream = None
cam_2_stream = None

terminate = MockValue(False)
sensor_one = MockValue(100)
sensor_two = MockValue(120)
sensor_three = MockValue(50)
sensor_four = MockValue(50)
sensor_five = MockValue(200)
sensor_six = MockValue(300)
sensor_seven = MockValue(0)
sensor_x = MockValue(0)
sensor_y = MockValue(0)
sensor_z = MockValue(0)
line_angle = MockValue(15)
gap_angle = MockValue(0)
program_start_time = MockValue(time.perf_counter())
run_start_time = MockValue(time.perf_counter())
zone_start_time = MockValue(-1)
picked_up_alive_count = MockValue(0)
picked_up_dead_count = MockValue(0)
iterations_control = MockValue(30)
iterations_serial = MockValue(60)
rotation_y = MockValue("none")
turn_dir = MockValue("straight")
objective = MockValue("follow_line")
switch = MockValue(1)
status = MockValue("Running Demo")
capture_image = MockValue(False)
calibrate_color_status = MockValue("none")
calibration_color = MockValue("z-g")

# --- Copied helpers ---

@njit(cache=True)
def get_yaw_pitch(yaw, pitch):
    rounded_yaw = round(yaw / 2) * 2
    rounded_pitch = round(pitch / 2) * 2
    wrapped_yaw = (270 - rounded_yaw) % 360
    clamped_pitch = max(-30, min(rounded_pitch, 30))
    return wrapped_yaw, clamped_pitch


def create_circle(x, y, r, canvas, style):
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r

    if style == 1:
        return canvas.create_oval(x0, y0, x1, y1, outline="#141414", width=3, fill="#292929")
    elif style == 2:
        return canvas.create_oval(x0, y0, x1, y1, outline="#141414", width=3, fill="#BBBBBB")
    elif style == 3:
        return canvas.create_oval(x0, y0, x1, y1, outline="#141414", width=3, fill="Black")

# --- App Class (Modified for Demo) ---

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

camera_width_1 = 448
camera_height_1 = 252
camera_width_2 = 448
camera_height_2 = 151
data_font_size = 15
label_color = "#141414"
button_color = "#141414"
testing_mode = False # Set to False to try loading the 3D model

# Load model map if not testing mode
if not testing_mode:
    try:
        # Robust absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.normpath(os.path.join(base_dir, "../main/resources/robot_model.npz"))
        if os.path.exists(model_path):
            print(f"Loading 3D model from {model_path}...")
            model_map = np.load(model_path, allow_pickle=True)["image_hashmap"].item()
            print("Model loaded.")
        else:
            print(f"Model not found at {model_path}. Disabling 3D view.")
            testing_mode = True
    except Exception as e:
        print(f"Failed to load model: {e}")
        testing_mode = True


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Overengineering² - DEMO")
        self.geometry("1024x600")
        self.resizable(False, False)
        # self.attributes("-topmost", True, "-fullscreen", True) # Disable for demo comfort

        self.mainFrame = ctk.CTkFrame(master=self)
        self.mainFrame.pack(pady=8, padx=8, fill="both", expand=True)

        self.mainFrame.grid_columnconfigure(0, weight=2)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_columnconfigure(2, weight=1)
        self.mainFrame.grid_columnconfigure(3, weight=1)
        self.mainFrame.grid_columnconfigure(4, weight=2)

        self.mainFrame.grid_rowconfigure(0)
        self.mainFrame.grid_rowconfigure(1)
        self.mainFrame.grid_rowconfigure(2)

        # Streams
        self.top_cam = ctk.CTkFrame(master=self.mainFrame)
        self.top_cam.grid(column=0, row=0, columnspan=2, sticky="w", padx=8, pady=8)
        self.top_camera = ctk.CTkLabel(self.top_cam, text="")
        self.top_camera.grid(padx=6, pady=6)

        self.bottom_cam = ctk.CTkFrame(master=self.mainFrame)
        self.bottom_cam.grid(column=3, row=0, columnspan=2, sticky="e", padx=8, pady=8)
        self.bottom_camera = ctk.CTkLabel(self.bottom_cam, text="")
        self.bottom_camera.grid(padx=6, pady=6)

        # DataFrame
        self.dataFrame = ctk.CTkFrame(master=self.mainFrame)
        self.dataFrame.configure(width=self.dataFrame["width"])
        self.dataFrame.grid_propagate(0)
        self.dataFrame.grid(column=0, row=1, sticky="nswe", padx=8, pady=4)

        for i in range(5): self.dataFrame.grid_rowconfigure(i, weight=1)
        
        # Sensor labels structure identical to main.py
        # ... (simplified for brevity, ensuring all used variables are present)
        
        self.label_sensor_1_var = tkinter.StringVar(value="0 mm")
        ctk.CTkLabel(self.dataFrame, text="Front L:", font=("Arial", data_font_size)).grid(column=0, row=0, sticky="e", padx=10)
        ctk.CTkLabel(self.dataFrame, textvariable=self.label_sensor_1_var, fg_color=label_color, corner_radius=4).grid(column=1, row=0, sticky="w", padx=8)

        self.label_sensor_2_var = tkinter.StringVar(value="0 mm")
        ctk.CTkLabel(self.dataFrame, text="Front R:", font=("Arial", data_font_size)).grid(column=2, row=0, sticky="e", padx=10)
        ctk.CTkLabel(self.dataFrame, textvariable=self.label_sensor_2_var, fg_color=label_color, corner_radius=4).grid(column=3, row=0, sticky="w", padx=8)

        # ... (Adding a few more for completeness)
        self.label_angle_var = tkinter.StringVar(value="0")
        
        # 3D Model Frame
        if not testing_mode:
            self.modelFrame = ctk.CTkFrame(master=self.mainFrame, width=266, fg_color="#292929")
            self.modelFrame.grid(column=1, row=1, columnspan=3, sticky="nswe", padx=6, pady=4)
            self.modelImage = ctk.CTkLabel(self.modelFrame, text="")
            self.modelImage.grid(sticky="nswe", padx=8, pady=8)

        # Status
        self.label_status_var = tkinter.StringVar(value=" ")
        self.label_status_font = ctk.CTkFont(family="arial", size=15)
        ctk.CTkLabel(master=self.mainFrame, textvariable=self.label_status_var, font=self.label_status_font).grid(column=3, columnspan=2, sticky="s", row=0, padx=8, pady=17)

        # Zone Frame (Canvas)
        self.zoneFrame = ctk.CTkFrame(master=self.mainFrame)
        self.zoneFrame.grid(column=4, row=1, sticky="nswe", padx=8, pady=4)
        self.canvas = Canvas(self.zoneFrame, width=80, height=30, bg="#292929", highlightthickness=0)
        self.canvas.grid(column=0, row=1, sticky="sw", padx=4, pady=4)

        # Timer
        self.barFrame = ctk.CTkFrame(master=self.mainFrame)
        self.barFrame.grid(column=0, row=2, columnspan=5, sticky="nwe", padx=8, pady=8)
        self.label_timer_var = tkinter.StringVar(value="--:--:--")
        ctk.CTkLabel(master=self.barFrame, textvariable=self.label_timer_var, font=("Arial", 30)).grid(column=2, row=0, sticky="n")

        # --- BOZOTICS OMNI TEST PANEL ---
        self.omni_frame = ctk.CTkFrame(master=self.mainFrame, fg_color="#333333")
        self.omni_frame.grid(column=2, row=0, sticky="nsew", padx=8, pady=8)
        
        ctk.CTkLabel(self.omni_frame, text="Bozotics Omni-Drive Logic", font=("Arial", 12, "bold")).pack(pady=2)
        
        # Speed Slider
        self.speed_slider = ctk.CTkSlider(self.omni_frame, from_=0, to=1000, command=self.update_omni_test)
        self.speed_slider.set(500)
        self.speed_slider.pack(pady=5)
        self.speed_label = ctk.CTkLabel(self.omni_frame, text="Speed: 500")
        self.speed_label.pack()

        # Angle Slider
        self.angle_slider = ctk.CTkSlider(self.omni_frame, from_=0, to=360, command=self.update_omni_test)
        self.angle_slider.set(0)
        self.angle_slider.pack(pady=5)
        self.angle_label = ctk.CTkLabel(self.omni_frame, text="Angle: 0")
        self.angle_label.pack()
        
        self.res_label = ctk.CTkLabel(self.omni_frame, text="FL:0 FR:0\nBL:0 BR:0", font=("Courier", 12))
        self.res_label.pack(pady=5)

        self.expand_button_var = tkinter.StringVar(value="-")

    def update_omni_test(self, _=None):
        speed = self.speed_slider.get()
        angle = self.angle_slider.get()
        
        self.speed_label.configure(text=f"Speed: {int(speed)}")
        self.angle_label.configure(text=f"Angle: {int(angle)}")
        
        fl, fr, bl, br = calculate_wheel_speeds(speed, angle, 0) # 0 rotation for basic test
        fl, fr, bl, br = normalize_speeds(fl, fr, bl, br, 1000)
        
        self.res_label.configure(text=f"FL:{int(fl)} FR:{int(fr)}\nBL:{int(bl)} BR:{int(br)}")

    def main(self):
        global cam_1_stream, cam_2_stream
        
        # Update dummy values
        sensor_x.value = (sensor_x.value + 1) % 360
        self.label_sensor_1_var.set(f"{sensor_one.value} mm")
        self.label_sensor_2_var.set(f"{sensor_two.value} mm")
        self.label_status_var.set(status.value)
        self.label_timer_var.set(str(timedelta(seconds=time.perf_counter() - program_start_time.value)))

        # Update Images from Shared Memory
        try:
             # Cam 1: 252, 448, 3
            bgr_img_arr_cam_1 = np.ndarray((252, 448, 3), dtype=np.uint8, buffer=cam_1_stream.buf)
            rgb_img_arr_cam_1 = cv2.cvtColor(bgr_img_arr_cam_1, cv2.COLOR_BGR2RGB)
            img_cam_1 = Image.fromarray(rgb_img_arr_cam_1)
            img_tks_cam_1 = ctk.CTkImage(img_cam_1, size=(camera_width_1, camera_height_1))
            self.top_camera.configure(image=img_tks_cam_1)

            # Cam 2: 216, 640, 3 (Note: Main.py says 216, 640. CamLoop might resize. We use this size.)
            bgr_img_arr_cam_2 = np.ndarray((216, 640, 3), dtype=np.uint8, buffer=cam_2_stream.buf)
            rgb_img_arr_cam_2 = cv2.cvtColor(bgr_img_arr_cam_2, cv2.COLOR_BGR2RGB)
            img_cam_2 = Image.fromarray(rgb_img_arr_cam_2)
            img_tks_cam_2 = ctk.CTkImage(img_cam_2, size=(camera_width_2, camera_height_2))
            self.bottom_camera.configure(image=img_tks_cam_2)
        except Exception as e:
            print("Cam update error:", e)

        # Update 3D Model
        if not testing_mode:
            try:
                rotation = get_yaw_pitch(sensor_x.value, sensor_y.value)
                if rotation in model_map:
                    image_robot_ctk = model_map[rotation]
                    self.modelImage.configure(image=image_robot_ctk)
            except Exception as e:
                print("Model update error:", e)

        self.after(100, self.main)

def cam_updater(shm_name, shape):
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = np.ndarray(shape, dtype=np.uint8, buffer=shm.buf)
    while not terminate.value:
        # Generate random noise as "video"
        noise = np.random.randint(0, 256, shape, dtype=np.uint8)
        np.copyto(buf, noise)
        time.sleep(0.033) # 30 FPS

if __name__ == "__main__":
    # Create Shared Memory
    try:
        shm1 = shared_memory.SharedMemory(name="shm_cam_1", create=True, size=252*448*3)
        shm2 = shared_memory.SharedMemory(name="shm_cam_2", create=True, size=216*640*3)
    except FileExistsError:
        shm1 = shared_memory.SharedMemory(name="shm_cam_1")
        shm2 = shared_memory.SharedMemory(name="shm_cam_2")

    cam_1_stream = shm1
    cam_2_stream = shm2

    # Start updaters
    t1 = threading.Thread(target=cam_updater, args=("shm_cam_1", (252, 448, 3)), daemon=True)
    t2 = threading.Thread(target=cam_updater, args=("shm_cam_2", (216, 640, 3)), daemon=True)
    t1.start()
    t2.start()

    app = App()
    app.main()
    app.mainloop()

    terminate.value = True
    shm1.close()
    shm1.unlink()
    shm2.close()
    shm2.unlink()
