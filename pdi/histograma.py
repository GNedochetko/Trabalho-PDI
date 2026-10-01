def calcular_histograma(imagem):
    # A Lista 4 conta as intensidades para o Otsu. Aqui fazemos isso com laços.
    # Recebe uma imagem em cinza ou um único canal de uma imagem RGB.
    altura, largura = imagem.shape
    contagem = [0] * 256

    for i in range(altura):
        for j in range(largura):
            valor = int(imagem[i, j])
            contagem[valor] += 1

    return contagem


def calcular_histogramas_rgb(imagem):
    # Na interface as cores estão na ordem vermelho, verde e azul.
    vermelho = calcular_histograma(imagem[:, :, 0])
    verde = calcular_histograma(imagem[:, :, 1])
    azul = calcular_histograma(imagem[:, :, 2])

    return vermelho, verde, azul
