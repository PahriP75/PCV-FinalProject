# 🎥 VTuber Tracking System (MediaPipe + Unity)

Project ini adalah sistem VTuber sederhana yang menghubungkan **Python (MediaPipe)** dengan **Unity**.
Sistem ini membaca gerakan wajah dan tubuh melalui webcam, lalu mengirimkan datanya ke Unity via UDP agar Avatar bergerak secara real-time.

## ✨ Fitur Utama
* **Face Tracking:** Mendeteksi kedipan mata, gerakan mulut, dan toleh kepala.
* **Body Tracking:** Mendeteksi gerakan lengan (Anti T-Pose).
* **Auto-Launch:** Script Python otomatis membuka aplikasi Unity saat dijalankan.

## 📂 Struktur Folder
Pastikan susunan folder kamu seperti ini agar tidak error:

```text
📁 NamaRepo/
├── 📁 Build/               # Folder hasil build Unity
│   ├── AvatarApp.exe       # File aplikasi Unity (Nama bisa beda)
│   └── UnityPlayer.dll     # File pendukung Unity
├── main_app.py             # Script Python utama
└── README.md               # File panduan ini
```
🛠️ Persyaratan :
1. OS: Windows 10/11.

2. Python: Versi 3.7 ke atas.

3. Library Python: Install library yang dibutuhkan dengan perintah ini di terminal:

```pip install opencv-python mediapipe```

🚀 Cara Menjalankan :
1. Setting Lokasi File Unity (Wajib!)
Sebelum menjalankan, kamu harus memberi tahu Python di mana letak file .exe Unity kamu.

1. Buka file main_app.py.

2. Cari variabel UNITY_EXE_PATH (biasanya di baris atas).

3. Ganti isinya dengan alamat lengkap file .exe di komputermu.

Contoh :
```UNITY_EXE_PATH = r"C:\Users\Fahri\Documents\Github\Project\Build\AvatarApp.exe"```

2. Jalankan Script
Buka terminal/CMD di folder project, lalu ketik:
```python main_app.py```

⚙️ Konfigurasi (Opsional)
Kamu bisa mengubah pengaturan di dalam file main_app.py:

* EYE_THRESHOLD: Atur sensitivitas kedip (Default 0.18). Kecilkan jika mata sering kedip sendiri.

* MOUTH_SENSITIVITY: Mengatur seberapa lebar mulut avatar terbuka.

* MIRROR_MODE: True untuk mode cermin, False untuk gerakan asli.

⚠️ Masalah Umum (Troubleshooting)
* SocketException / Error Merah: Port 5052 sedang terpakai. Matikan semua program Python/Unity, lalu jalankan ulang salah satu saja.

* Avatar Diam (T-Pose): Pastikan jendela Unity sedang aktif (klik layar gamenya sekali).
