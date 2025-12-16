import cv2
import mediapipe as mp
import socket
import math

# ================= KONFIGURASI =================
UDP_IP = "127.0.0.1"
UDP_PORT = 5052
MOUTH_SENSITIVITY = 100.0 
EYE_THRESHOLD = 0.22      

# [SETTING PENTING] 
MIRROR_MODE = True 
# ===============================================

# Setup Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Setup Mediapipe & Drawing Utils (Untuk Menggambar Garis)
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0) # Ganti 1 jika kamera tidak muncul

def dist(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def get_eye_ratio(eye_points, landmarks):
    v1 = dist(landmarks[eye_points[1]], landmarks[eye_points[5]])
    v2 = dist(landmarks[eye_points[2]], landmarks[eye_points[4]])
    h = dist(landmarks[eye_points[0]], landmarks[eye_points[3]])
    if h == 0: return 0
    return (v1 + v2) / (2.0 * h)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH = [13, 14]

print(f"✅ Tracker Siap! (Face Mesh: ON)")
print(f"📡 Mengirim ke Unity port {UDP_PORT}...")

# refine_face_landmarks=True agar mata & bibir lebih presisi
with mp_holistic.Holistic(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5,
    refine_face_landmarks=True) as holistic:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        if MIRROR_MODE:
            image = cv2.flip(image, 1)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Default Values
        head_yaw = head_pitch = 0.0
        blink_left = blink_right = 0.0
        mouth_open = 0.0
        body_z = body_y = 0.0
        arm_l = arm_r = 0.0
        
        # STATUS WAJAH (Debug)
        face_status = "FACE: LOST"
        color_status = (0, 0, 255) # Merah

        # --- 1. WAJAH (FACE) ---
        if results.face_landmarks:
            face_status = "FACE: DETECTED"
            color_status = (0, 255, 0) # Hijau
            
            lm = results.face_landmarks.landmark
            nose = lm[1]
            
            if MIRROR_MODE:
                head_yaw = (nose.x - 0.5) * 180 
            else:
                head_yaw = (nose.x - 0.5) * -180
            head_pitch = (nose.y - 0.5) * 100

            mouth_dist = dist(lm[MOUTH[0]], lm[MOUTH[1]])
            mouth_open = mouth_dist * MOUTH_SENSITIVITY
            if mouth_open > 1.0: mouth_open = 1.0
            if mouth_open < 0.0: mouth_open = 0.0

            left_ratio = get_eye_ratio(LEFT_EYE, lm)
            right_ratio = get_eye_ratio(RIGHT_EYE, lm)
            
            blink_left = 1.0 if left_ratio < EYE_THRESHOLD else 0.0
            blink_right = 1.0 if right_ratio < EYE_THRESHOLD else 0.0

            if mouth_open > 0.3:
                blink_left = 0.0
                blink_right = 0.0

        # --- 2. BADAN (POSE) ---
        if results.pose_landmarks:
            plm = results.pose_landmarks.landmark
            shoulder_l = plm[11]
            shoulder_r = plm[12]
            
            if MIRROR_MODE:
                 body_z = (shoulder_l.y - shoulder_r.y) * 50  
                 body_y = (shoulder_l.z - shoulder_r.z) * -30 
            else:
                 body_z = (shoulder_l.y - shoulder_r.y) * -50
                 body_y = (shoulder_l.z - shoulder_r.z) * 30

            if abs(body_y) < 5: body_y = 0
            if abs(body_z) < 5: body_z = 0

            # --- TANGAN ---
            elbow_l = plm[13]
            elbow_r = plm[14]
            
            arm_l = (shoulder_l.y - elbow_l.y) * 300 
            arm_r = (shoulder_r.y - elbow_r.y) * 300
            
            # Batas bawah jadi 0
            if arm_l < 0: arm_l = 0
            if arm_r < 0: arm_r = 0
            if arm_l > 170: arm_l = 170
            if arm_r > 170: arm_r = 170

        # KIRIM DATA
        if MIRROR_MODE:
             message = f"{head_yaw:.2f},{head_pitch:.2f},{blink_left:.2f},{blink_right:.2f},{mouth_open:.2f},{body_z:.2f},{body_y:.2f},{arm_l:.2f},{arm_r:.2f}"
        else:
             message = f"{head_yaw:.2f},{head_pitch:.2f},{blink_right:.2f},{blink_left:.2f},{mouth_open:.2f},{body_z:.2f},{body_y:.2f},{arm_l:.2f},{arm_r:.2f}"
        
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

        # ================= VISUALISASI KEREN =================
        # 1. Gambar Jaring Wajah (Face Mesh)
        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.face_landmarks,
                mp_holistic.FACEMESH_TESSELATION, # Jaring-jaring wajah
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
            
            # Gambar Kontur Wajah (Mata, Bibir, Alis lebih tebal)
            mp_drawing.draw_landmarks(
                image,
                results.face_landmarks,
                mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

        # 2. Gambar Tulang Badan (Pose)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        # =====================================================

        cv2.putText(image, face_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_status, 2)
        cv2.imshow('Tracker Full Body', image)
        if cv2.waitKey(5) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()