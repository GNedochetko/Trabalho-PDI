import cv2

def processar_quadro(quadro, operacao, tamanho_filtro=3,
                     limiar_minimo=50, limiar_maximo=150, tamanho_elemento=3):
    if operacao == "Original":
        return quadro.copy()
    if operacao == "Negativo":
        return cv2.bitwise_not(quadro)
    if operacao == "Média":
        return cv2.blur(quadro, (tamanho_filtro, tamanho_filtro))
    if operacao == "Mediana":
        return cv2.medianBlur(quadro, tamanho_filtro)

    cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY)
    if operacao == "Níveis de cinza":
        return cinza
    if operacao == "Binário — Otsu":
        _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binaria
    if operacao == "Canny":
        suave = cv2.GaussianBlur(cinza, (5, 5), 1.0, borderType=cv2.BORDER_REPLICATE)
        return cv2.Canny(suave, limiar_minimo, limiar_maximo, L2gradient=True)

    elemento = cv2.getStructuringElement(cv2.MORPH_RECT,
                                         (tamanho_elemento, tamanho_elemento))
    if operacao == "Erosão":
        return cv2.erode(cinza, elemento)
    if operacao == "Dilatação":
        return cv2.dilate(cinza, elemento)
    if operacao == "Abertura":
        return cv2.morphologyEx(cinza, cv2.MORPH_OPEN, elemento)
    if operacao == "Fechamento":
        return cv2.morphologyEx(cinza, cv2.MORPH_CLOSE, elemento)

    return quadro.copy()


def converter_rgb(quadro):
    # A câmera fornece BGR, mas o Pillow exibe RGB. Cinza já pode ser exibido.
    if quadro.ndim == 2:
        return quadro
    return cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)


def selecionar_regiao(quadro):
    # O próprio OpenCV permite arrastar um retângulo e confirmar com Enter.
    titulo = "Selecionar objeto - Enter confirma, Esc cancela"
    regiao = cv2.selectROI(titulo, quadro, showCrosshair=False, fromCenter=False)
    cv2.destroyWindow(titulo)
    return regiao


def iniciar_rastreamento(quadro, regiao):
    rastreador = cv2.TrackerCSRT_create()
    rastreador.init(quadro, regiao)
    return rastreador


def localizar_objeto(quadro, referencia, semelhanca_minima=0.9):
    # Comparação de imagem: procura a referência em todo o quadro, sem rastreador.
    altura, largura = referencia.shape[:2]
    if altura > quadro.shape[0] or largura > quadro.shape[1]:
        return None, 0

    comparacao = cv2.matchTemplate(quadro, referencia, cv2.TM_SQDIFF_NORMED)
    menor_erro, _, posicao, _ = cv2.minMaxLoc(comparacao)
    semelhanca = max(0, min(1, 1 - menor_erro))
    if semelhanca >= semelhanca_minima:
        x, y = posicao
        return (x, y, largura, altura), semelhanca
    return None, semelhanca


def desenhar_caixa(quadro, regiao, texto, cor):
    # Converte cinza para colorido apenas para desenhar as marcações.
    if quadro.ndim == 2:
        resultado = cv2.cvtColor(quadro, cv2.COLOR_GRAY2BGR)
    else:
        resultado = quadro.copy()
    x, y, largura, altura = regiao
    x, y, largura, altura = int(x), int(y), int(largura), int(altura)
    cv2.rectangle(resultado, (x, y), (x + largura, y + altura), cor, 2)
    cv2.putText(resultado, texto, (x, max(20, y - 6)),
                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 1)
    return resultado
