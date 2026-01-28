# OBR 2026 Strategy Map - High Performance Rescue

## Core Philosophy: "Overengineering"

We do not rely on a single sensor. We use a **Sensory Fusion** approach (Vision + IR + IMU) to guarantee robustness.

---

## 🔋 Two-Battery Architecture (Noise Isolation)

**Rationale:** Motors generate significant electrical noise and voltage spikes that can reset the Raspberry Pi. Isolate "Dirty" power from "Clean" power.

1.  **Dirty Circuit (3S LiPo - 11.1V)**
    - Powers: 4x High Power Motors (via Driver), Solenoids (if any), High-Torque Servos.
    - **Isolation:** Physically separate ground loops where possible, united only at the controller common ground with optocouplers if needed.

2.  **Clean Circuit (2S LiPo - 7.4V -> Regulated 5V)**
    - Powers: Raspberry Pi 5, Coral TPU, Arduino Nanos, Sensors.
    - **Stability:** Ensures the "Brain" never dies even if motors stall and drop the main battery voltage.

---

## 🗺️ Navigation Phases

### Phase A: Predictive Navigation (Line Following)

**Goal:** High-speed traversal of the arena.

- **Primary:** Vector-based line following using OpenCV (Green/White separation).
- **Secondary:** PID control loop using Pololu IR arrays for "blind" spots or tight corners.
- **Logic:** The robot "looks ahead" with the camera. If a curve is detected 20cm away, it begins decelerating _before_ it hits the curve.

### Phase B: Smart Intersections (Green Markers)

**Goal:** Perfect intersection handling.

- **Detection:** YOLOv8 Classification (`silver_classify_s.onnx` repurposing or HSV filtering) + Contour analysis.
- **Logic:**
  1. Detect Green Marker.
  2. Identify side (Left/Right/Both).
  3. Cross-reference with Grid Map (SLAM-lite) if enabled.
  4. Build trajectory path (e.g., "Turn Right 90 degrees").

### Phase C: Victim Rescue (Rescue Zone)

**Goal:** Retrieve victims (Spheres) and place in Safe Zone.

- **Entrance:** Detect Silver Tape (YOLO Classify). Switch `State Machine` to `ZONE_MODE`.
- **Search:** Spin or Sweep.
- **Detection:** YOLOv8 Detection (`ball_detect_s_edgetpu.tflite`).
  - _Classes:_ `Live_Victim` (Silver), `Dead_Victim` (Black).
- **Retrieval:**
  - Align Gripper Center to Victim Bounding Box.
  - Drive forward with Ultrasound distance check.
  - Actuate Servos (Grab -> Lift).
- **Drop-off:** Locate Triangle (Black/Green corner) or Box contours. Drive and Release.
