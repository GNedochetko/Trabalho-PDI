import numpy as np


def cinza(imagem):
    # Recebe uma matriz RGB, como a imagem aberta pelo Pillow na interface.
    if imagem.ndim == 2:
        return imagem.copy()

    altura, largura = imagem.shape[:2]
    resultado = np.zeros((altura, largura), dtype=np.uint8)

    for i in range(altura):
        for j in range(largura):
            r = int(imagem[i, j, 0])
            g = int(imagem[i, j, 1])
            b = int(imagem[i, j, 2])
            resultado[i, j] = int(0.299 * r + 0.587 * g + 0.114 * b + 0.5)

    return resultado

def negativo(imagem):
    # Funciona tanto para RGB quanto para uma imagem em cinza ou binária.
    return 255 - imagem

def otsu(imagem):
    # Adaptado do Otsu próprio da Lista 4 usando laços simples.
    imagem = cinza(imagem)
    altura, largura = imagem.shape
    histograma = [0] * 256

    for i in range(altura):
        for j in range(largura):
            valor = int(imagem[i, j])
            histograma[valor] += 1

    total = altura * largura
    soma_total = 0
    for valor in range(256):
        soma_total += valor * histograma[valor]

    quantidade_fundo = 0
    soma_fundo = 0
    maior_variancia = -1
    limiar = 0

    for valor in range(256):
        quantidade_fundo += histograma[valor]
        soma_fundo += valor * histograma[valor]
        quantidade_objeto = total - quantidade_fundo

        # Precisamos de pixels dos dois lados para comparar as médias.
        if quantidade_fundo == 0:
            continue
        if quantidade_objeto == 0:
            break

        media_fundo = soma_fundo / quantidade_fundo
        media_objeto = (soma_total - soma_fundo) / quantidade_objeto
        variancia = quantidade_fundo * quantidade_objeto * (media_fundo - media_objeto) ** 2

        if variancia > maior_variancia:
            maior_variancia = variancia
            limiar = valor

    resultado = np.zeros((altura, largura), dtype=np.uint8)
    for i in range(altura):
        for j in range(largura):
            if imagem[i, j] > limiar:
                resultado[i, j] = 255

    return limiar, resultado
