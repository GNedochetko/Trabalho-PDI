import pygame


def carregar_musica(caminho):
    # Arquivo inválido ou saída de áudio indisponível são problemas comuns aqui.
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(caminho)
    except (pygame.error, OSError):
        return False
    return True


def tocar_musica():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()


def parar_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def fechar_audio():
    if pygame.mixer.get_init():
        pygame.mixer.quit()
