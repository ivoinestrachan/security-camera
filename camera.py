import cv2
from time import time, sleep, strftime
import socket
from goprocam import GoProCamera, constants


def initialize_camera():
    gpCam = GoProCamera.GoPro()
    gpCam.livestream("start")
    gpCam.video_settings(res='720p', fps='30')
    gpCam.gpControlSet(constants.Stream.WINDOW_SIZE,
                       constants.Stream.WindowSize.R480)
    return gpCam


def initialize_capture():
    cap = cv2.VideoCapture("udp://10.5.5.9:8554", cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    return cap


WRITE = False
gpCam = initialize_camera()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
t = time()
cap = initialize_capture()
counter = 0

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Failed to read frame. Reinitializing capture...")
        cap.release()
        sleep(1)
        cap = initialize_capture()
        continue

    if frame.size == 0:
        print("Empty frame. Reinitializing capture...")
        cap.release()
        sleep(1)
        cap = initialize_capture()
        continue

    timestamp = strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Security Camera", frame)

    if WRITE:
        cv2.imwrite(f"{counter}.jpg", frame)
        counter += 1
        if counter >= 10:
            break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if time() - t >= 2.5:
        try:
            sock.sendto("_GPHD_:0:0:2:0.000000\n".encode(),
                        ("10.5.5.9", 8554))
        except Exception as e:
            print(f"Failed to send keep-alive packet: {e}")
        t = time()

cap.release()
cv2.destroyAllWindows()
