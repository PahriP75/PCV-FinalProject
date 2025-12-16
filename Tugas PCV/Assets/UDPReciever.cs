using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Globalization;

public class UDPReceiver : MonoBehaviour
{
    [Header("Connection Settings")]
    public int port = 5052;

    [Header("Live Data (Do Not Edit)")]
    public float headYaw;
    public float headPitch;
    public float blinkLeft;
    public float blinkRight;
    public float mouthOpen;
    public float bodyZ;
    public float bodyY;
    public float armLeft;
    public float armRight;
    public float handLeftOpen;
    public float handRightOpen;

    private Thread receiveThread;
    private UdpClient client;
    private bool isRunning = true;

    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (isRunning)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);

                // Urutan data dari Python:
                // yaw, pitch, blinkL, blinkR, mouth, bodyZ, bodyY, armL, armR, handL, handR
                string[] points = text.Split(',');

                if (points.Length >= 11)
                {
                    // Gunakan InvariantCulture agar titik (.) terbaca sebagai desimal, bukan ribuan
                    headYaw = float.Parse(points[0], CultureInfo.InvariantCulture);
                    headPitch = float.Parse(points[1], CultureInfo.InvariantCulture);
                    blinkLeft = float.Parse(points[2], CultureInfo.InvariantCulture);
                    blinkRight = float.Parse(points[3], CultureInfo.InvariantCulture);
                    mouthOpen = float.Parse(points[4], CultureInfo.InvariantCulture);
                    bodyZ = float.Parse(points[5], CultureInfo.InvariantCulture);
                    bodyY = float.Parse(points[6], CultureInfo.InvariantCulture);
                    armLeft = float.Parse(points[7], CultureInfo.InvariantCulture);
                    armRight = float.Parse(points[8], CultureInfo.InvariantCulture);
                    handLeftOpen = float.Parse(points[9], CultureInfo.InvariantCulture);
                    handRightOpen = float.Parse(points[10], CultureInfo.InvariantCulture);
                }
            }
            catch (Exception err)
            {
                Debug.LogWarning("UDP Error: " + err.Message);
            }
        }
    }

    void OnDisable()
    {
        isRunning = false;
        if (client != null) client.Close();
        if (receiveThread != null) receiveThread.Abort();
    }
}