import math

import numpy as np


def rotular(imagem, conectividade=8):
    # Imagem binária: 255 é objeto e 0 é fundo.
    # Segue a ideia de expandir uma semente da Lista 5, sem funções prontas.
    altura, largura = imagem.shape
    rotulos = np.zeros((altura, largura), dtype=np.int32)
    componentes = []
    vizinhos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if conectividade == 8:
        vizinhos += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for i in range(altura):
        for j in range(largura):
            if imagem[i, j] != 255 or rotulos[i, j] != 0:
                continue

            rotulo = len(componentes) + 1
            rotulos[i, j] = rotulo
            pendentes = [(i, j)]
            pixels = []

            while pendentes:
                y, x = pendentes.pop()
                pixels.append((y, x))
                for dy, dx in vizinhos:
                    ny = y + dy
                    nx = x + dx
                    if 0 <= ny < altura and 0 <= nx < largura:
                        if imagem[ny, nx] == 255 and rotulos[ny, nx] == 0:
                            rotulos[ny, nx] = rotulo
                            pendentes.append((ny, nx))

            componentes.append(pixels)

    # A quantidade de componentes é a contagem de objetos.
    return rotulos, componentes


def perimetro_e_contorno(rotulos, pixels, rotulo):
    # Cada lado do pixel que encosta no fundo conta 1 px de perímetro.
    # Também conta os contornos de buracos e as bordas da imagem.
    altura, largura = rotulos.shape
    perimetro = 0
    contorno = []
    vizinhos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y, x in pixels:
        na_borda = False
        for dy, dx in vizinhos:
            ny = y + dy
            nx = x + dx
            if ny < 0 or ny >= altura or nx < 0 or nx >= largura:
                perimetro += 1
                na_borda = True
            elif rotulos[ny, nx] != rotulo:
                perimetro += 1
                na_borda = True
        if na_borda:
            contorno.append((y, x))

    return perimetro, contorno


def diametro(contorno):
    # Maior distância entre os centros dos pixels do contorno.
    # Um objeto com apenas um pixel tem diâmetro zero por esta definição.
    maior_distancia = 0
    for i in range(len(contorno)):
        y1, x1 = contorno[i]
        for j in range(i + 1, len(contorno)):
            y2, x2 = contorno[j]
            distancia = (y2 - y1) ** 2 + (x2 - x1) ** 2
            maior_distancia = max(maior_distancia, distancia)

    return math.sqrt(maior_distancia)


def medir_objetos(rotulos, componentes):
    medidas = []
    for i in range(len(componentes)):
        rotulo = i + 1
        pixels = componentes[i]
        area = len(pixels)
        perimetro, contorno = perimetro_e_contorno(rotulos, pixels, rotulo)
        medidas.append((rotulo, area, perimetro, round(diametro(contorno), 2)))

    return medidas


def colorir(rotulos):
    altura, largura = rotulos.shape
    resultado = np.zeros((altura, largura, 3), dtype=np.uint8)
    cores = [(230, 70, 70), (70, 180, 90), (80, 130, 240), (230, 180, 50),
             (170, 90, 220), (50, 190, 190), (230, 120, 60), (220, 100, 180)]

    for i in range(altura):
        for j in range(largura):
            rotulo = int(rotulos[i, j])
            if rotulo != 0:
                resultado[i, j] = cores[(rotulo - 1) % len(cores)]

    return resultado
