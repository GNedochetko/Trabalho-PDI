import cv2

if __package__:
    from . import conversoes
else:
    import conversoes


def filtro_media(imagem, tamanho_janela=3):
    if tamanho_janela < 1 or tamanho_janela % 2 == 0:
        raise ValueError("O tamanho da janela deve ser positivo e ímpar.")

    altura, largura = imagem.shape
    resultado = imagem.copy()
    margem = tamanho_janela // 2
    quantidade = tamanho_janela * tamanho_janela

    # Mantemos as bordas originais, como na lista.
    for i in range(margem, altura - margem):
        for j in range(margem, largura - margem):
            soma = 0
            for di in range(-margem, margem + 1):
                for dj in range(-margem, margem + 1):
                    soma += int(imagem[i + di, j + dj])

            resultado[i, j] = soma // quantidade

    return resultado


def filtro_mediana(imagem, tamanho_janela=3):
    # Adaptado da Lista 2: ordena os vizinhos e pega o valor do meio.
    if tamanho_janela < 1 or tamanho_janela % 2 == 0:
        raise ValueError("O tamanho da janela deve ser positivo e ímpar.")

    altura, largura = imagem.shape
    resultado = imagem.copy()
    margem = tamanho_janela // 2

    for i in range(margem, altura - margem):
        for j in range(margem, largura - margem):
            valores = []
            for di in range(-margem, margem + 1):
                for dj in range(-margem, margem + 1):
                    valores.append(int(imagem[i + di, j + dj]))

            valores.sort()
            resultado[i, j] = valores[len(valores) // 2]

    return resultado


def suavizar(imagem, tamanho_janela, metodo):
    # Para imagens coloridas, aplicamos o filtro em cada canal separadamente.
    if imagem.ndim == 2:
        if metodo == "Média":
            return filtro_media(imagem, tamanho_janela)
        return filtro_mediana(imagem, tamanho_janela)

    resultado = imagem.copy()
    for canal in range(3):
        if metodo == "Média":
            resultado[:, :, canal] = filtro_media(imagem[:, :, canal], tamanho_janela)
        else:
            resultado[:, :, canal] = filtro_mediana(imagem[:, :, canal], tamanho_janela)

    return resultado


def canny(imagem, limiar_minimo=50, limiar_maximo=150):
    # Mesmos parâmetros da Lista 4, com os limiares escolhidos na interface.
    if limiar_minimo < 0 or limiar_minimo > limiar_maximo:
        raise ValueError("O limiar mínimo deve ser >= 0 e não pode passar do máximo.")

    imagem_cinza = conversoes.cinza(imagem)
    suave = cv2.GaussianBlur(imagem_cinza, (5, 5), 1.0,
                             borderType=cv2.BORDER_REPLICATE)
    return cv2.Canny(suave, limiar_minimo, limiar_maximo, L2gradient=True)
