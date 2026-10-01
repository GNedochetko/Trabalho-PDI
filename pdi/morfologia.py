def erosao(imagem, tamanho=3):
    # Elemento quadrado: cada pixel recebe o menor valor da vizinhança.
    if tamanho < 1 or tamanho % 2 == 0:
        raise ValueError("O elemento deve ter tamanho positivo e ímpar.")

    altura, largura = imagem.shape
    resultado = imagem.copy()
    margem = tamanho // 2

    for i in range(altura):
        for j in range(largura):
            menor = 255
            for di in range(-margem, margem + 1):
                for dj in range(-margem, margem + 1):
                    y = i + di
                    x = j + dj
                    # Fora da imagem não há pixels para comparar.
                    if 0 <= y < altura and 0 <= x < largura:
                        menor = min(menor, int(imagem[y, x]))
            resultado[i, j] = menor

    return resultado


def dilatacao(imagem, tamanho=3):
    # Elemento quadrado: cada pixel recebe o maior valor da vizinhança.
    if tamanho < 1 or tamanho % 2 == 0:
        raise ValueError("O elemento deve ter tamanho positivo e ímpar.")

    altura, largura = imagem.shape
    resultado = imagem.copy()
    margem = tamanho // 2

    for i in range(altura):
        for j in range(largura):
            maior = 0
            for di in range(-margem, margem + 1):
                for dj in range(-margem, margem + 1):
                    y = i + di
                    x = j + dj
                    if 0 <= y < altura and 0 <= x < largura:
                        maior = max(maior, int(imagem[y, x]))
            resultado[i, j] = maior

    return resultado


def abertura(imagem, tamanho=3):
    # Mesma sequência da Lista 5: erosão e depois dilatação.
    return dilatacao(erosao(imagem, tamanho), tamanho)


def fechamento(imagem, tamanho=3):
    # Mesma sequência da Lista 5: dilatação e depois erosão.
    return erosao(dilatacao(imagem, tamanho), tamanho)
