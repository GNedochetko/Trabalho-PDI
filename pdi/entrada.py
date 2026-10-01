import cv2


def abrir_camera(indice=0):
    camera = cv2.VideoCapture(indice)
    if not camera.isOpened():
        camera.release()
        return None

    # Solicita uma resolução leve para o processamento em tempo real.
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera
