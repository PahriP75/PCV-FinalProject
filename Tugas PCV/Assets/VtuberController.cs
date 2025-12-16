using UnityEngine;

public class VtuberController : MonoBehaviour
{
    [Header("Sumber Data")]
    public UDPReceiver receiver;

    [Header("Target Tulang (Drag Bone Disini)")]
    public Transform headBone;
    // Spine dihapus agar badan diam
    public Transform leftArmBone;
    public Transform rightArmBone;

    [Header("Target Wajah (Skinned Mesh Renderer)")]
    public SkinnedMeshRenderer faceMesh;

    [Header("Nama BlendShapes (Cek di Inspector)")]
    public string blinkLeftName = "Blink_L";
    public string blinkRightName = "Blink_R";
    public string mouthOpenName = "Mouth_Open";

    [Header("Pengaturan Gerakan")]
    public float smoothSpeed = 10f;
    public float headRotMultiplier = 1.0f;

    [Tooltip("Seberapa jauh tangan turun saat nilai input 0. Coba nilai 70-90.")]
    public float armDownOffset = 80f; // ATUR INI: Semakin besar, tangan makin rapat ke badan saat diam.

    // Variabel untuk menyimpan rotasi awal
    private Quaternion startHeadRot;
    // Kita tidak butuh start rotation tangan lagi karena kita pakai absolute rotation dari T-pose

    void Start()
    {
        if (headBone) startHeadRot = headBone.localRotation;
        // startLArmRot & startRArmRot dihapus, kita pakai asumsi T-pose adalah (0,0,0)
    }

    void Update()
    {
        if (receiver == null) return;

        // --- 1. KEPALA ---
        if (headBone)
        {
            Quaternion targetHead = Quaternion.Euler(
                receiver.headPitch * headRotMultiplier,
                receiver.headYaw * headRotMultiplier,
                0);

            headBone.localRotation = Quaternion.Lerp(headBone.localRotation, startHeadRot * targetHead, Time.deltaTime * smoothSpeed);
        }

        // --- 2. TANGAN (Logika Baru Anti T-Pose) ---
        // Asumsi: Rotasi (0,0,0) adalah T-Pose.
        // Sumbu Z Positif (+) memutar tangan KIRI ke bawah.
        // Sumbu Z Negatif (-) memutar tangan KANAN ke bawah.

        // Pengali 1.6f adalah estimasi agar input 0-100 mencakup rentang gerak dari bawah ke atas.

        if (leftArmBone)
        {
            // Saat input 0 -> Sudut jadi +80 (Turun). Saat input 100 -> Sudut jadi -80 (Naik).
            float targetAngleL = armDownOffset - (receiver.armLeft * 1.6f);
            Quaternion finalRotL = Quaternion.Euler(0, 0, targetAngleL);
            leftArmBone.localRotation = Quaternion.Lerp(leftArmBone.localRotation, finalRotL, Time.deltaTime * smoothSpeed);
        }

        if (rightArmBone)
        {
            // Tangan kanan adalah cerminan (kebalikannya)
            float targetAngleR = -armDownOffset + (receiver.armRight * 1.6f);
            Quaternion finalRotR = Quaternion.Euler(0, 0, targetAngleR);
            rightArmBone.localRotation = Quaternion.Lerp(rightArmBone.localRotation, finalRotR, Time.deltaTime * smoothSpeed);
        }

        // --- 3. WAJAH (BlendShapes) ---
        if (faceMesh)
        {
            SetBlendShape(blinkLeftName, receiver.blinkLeft * 100);
            SetBlendShape(blinkRightName, receiver.blinkRight * 100);
            SetBlendShape(mouthOpenName, receiver.mouthOpen * 100);
        }
    }

    void SetBlendShape(string name, float value)
    {
        int index = faceMesh.sharedMesh.GetBlendShapeIndex(name);
        if (index != -1)
        {
            float current = faceMesh.GetBlendShapeWeight(index);
            float next = Mathf.Lerp(current, value, Time.deltaTime * 20f);
            faceMesh.SetBlendShapeWeight(index, next);
        }
    }
}