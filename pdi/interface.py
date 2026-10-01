"""Interface do trabalho para processamento de imagens e câmera."""

import tkinter as tk
from tkinter import filedialog, ttk

import cv2
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageDraw, ImageTk

if __package__:
    from . import audio, conversoes, entrada, filtros, histograma, morfologia, objetos, video
else:
    import audio
    import conversoes
    import entrada
    import filtros
    import histograma
    import morfologia
    import objetos
    import video


class Interface:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Processamento de imagens e vídeo")
        self.janela.geometry("1100x760")
        self.janela.minsize(950, 740)

        self.imagem_original = None
        self.imagem_resultado = None
        self.caminho_musica = ""
        self.camera = None
        self.atualizacao_camera = None
        self.ultimo_quadro = None
        self.rastreador = None
        self.referencia_objeto = None
        self.objeto_presente = False
        self.quadros_presente = 0
        self.quadros_ausente = 0
        self.semelhanca_minima = tk.DoubleVar(value=0.9)
        self.situacao_rastreamento = tk.StringVar(value="Sem rastreamento")
        self.situacao_identificacao = tk.StringVar(value="Identificação desativada")
        self.operacao_video = tk.StringVar(value="Original")
        self.status = tk.StringVar(value="Abra uma imagem ou escolha a aba Câmera.")
        self.tamanho_filtro = tk.IntVar(value=3)
        self.tamanho_elemento = tk.IntVar(value=3)
        self.limiar_minimo = tk.IntVar(value=50)
        self.limiar_maximo = tk.IntVar(value=150)
        self.conectividade = tk.StringVar(value="8")
        self.indice_camera = tk.IntVar(value=0)
        self.identificar_objeto = tk.BooleanVar(value=False)

        conteudo = ttk.Frame(janela, padding=10)
        conteudo.pack(fill="both", expand=True)

        painel = ttk.Frame(conteudo, width=225)
        painel.pack(side="left", fill="y", padx=(0, 10))
        self.criar_operacoes(painel)

        self.abas = ttk.Notebook(conteudo)
        self.abas.pack(side="left", fill="both", expand=True)
        self.aba_imagem = ttk.Frame(self.abas, padding=8)
        self.aba_camera = ttk.Frame(self.abas, padding=8)
        self.abas.add(self.aba_imagem, text="Imagem")
        self.abas.add(self.aba_camera, text="Câmera")
        self.criar_aba_imagem()
        self.criar_aba_camera()
        self.abas.bind("<<NotebookTabChanged>>", self.mudar_aba)

        ttk.Label(janela, textvariable=self.status, padding=(10, 6)).pack(fill="x")
        janela.protocol("WM_DELETE_WINDOW", self.fechar)

    def criar_operacoes(self, painel):
        conversoes = ttk.LabelFrame(painel, text="Conversões", padding=6)
        conversoes.pack(fill="x", pady=(0, 8))
        self.criar_botao(conversoes, "Níveis de cinza")
        self.criar_botao(conversoes, "Negativo")
        self.criar_botao(conversoes, "Binário — Otsu")

        filtros = ttk.LabelFrame(painel, text="Filtros e bordas", padding=6)
        filtros.pack(fill="x", pady=(0, 8))
        self.criar_parametro(filtros, "Janela do filtro", self.tamanho_filtro,
                             3, 31, 2)
        self.criar_botao(filtros, "Média")
        self.criar_botao(filtros, "Mediana")
        self.criar_parametro(filtros, "Limiar mínimo", self.limiar_minimo,
                             0, 255)
        self.criar_parametro(filtros, "Limiar máximo", self.limiar_maximo,
                             0, 255)
        self.criar_botao(filtros, "Canny")

        morfologia = ttk.LabelFrame(painel, text="Morfologia", padding=6)
        morfologia.pack(fill="x", pady=(0, 8))
        self.criar_parametro(morfologia, "Elemento quadrado",
                             self.tamanho_elemento, 3, 31, 2)
        self.criar_botao(morfologia, "Erosão")
        self.criar_botao(morfologia, "Dilatação")
        self.criar_botao(morfologia, "Abertura")
        self.criar_botao(morfologia, "Fechamento")

        analise = ttk.LabelFrame(painel, text="Análise de imagem", padding=6)
        analise.pack(fill="x")
        linha = ttk.Frame(analise)
        linha.pack(fill="x", pady=2)
        ttk.Label(linha, text="Conectividade").pack(side="left")
        ttk.Combobox(linha, textvariable=self.conectividade,
                     values=("4", "8"), state="readonly", width=4).pack(side="right")
        self.botoes_analise = [
            self.criar_botao(analise, "Histograma"),
            self.criar_botao(analise, "Detectar e contar objetos"),
            self.criar_botao(analise, "Calcular medidas"),
        ]

    def criar_botao(self, grupo, nome):
        botao = ttk.Button(grupo, text=nome,
                           command=lambda: self.executar_operacao(nome))
        botao.pack(fill="x", pady=1)
        return botao

    def criar_parametro(self, grupo, nome, variavel, minimo, maximo, passo=1):
        linha = ttk.Frame(grupo)
        linha.pack(fill="x", pady=3)
        ttk.Label(linha, text=nome).pack(side="left")
        ttk.Spinbox(linha, from_=minimo, to=maximo, increment=passo,
                    textvariable=variavel, width=5, state="readonly").pack(side="right")

    def criar_previa(self, grupo, titulo):
        quadro = ttk.LabelFrame(grupo, text=titulo, padding=6)
        quadro.pack(side="left", fill="both", expand=True, padx=3)
        previa = ttk.Label(quadro, text="Sem imagem", anchor="center")
        previa.pack(fill="both", expand=True)
        return previa

    def criar_aba_imagem(self):
        barra = ttk.Frame(self.aba_imagem)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Button(barra, text="Abrir imagem", command=self.abrir_imagem).pack(side="left")
        ttk.Button(barra, text="Restaurar original",
                   command=self.restaurar_original).pack(side="left", padx=6)
        ttk.Button(barra, text="Salvar resultado",
                   command=self.salvar_resultado).pack(side="left")

        self.nome_arquivo = ttk.Label(self.aba_imagem, text="Nenhuma imagem carregada")
        self.nome_arquivo.pack(anchor="w", pady=(0, 8))

        previas = ttk.Frame(self.aba_imagem)
        previas.pack(fill="both", expand=True)
        self.previa_original = self.criar_previa(previas, "Original")
        self.previa_resultado = self.criar_previa(previas, "Resultado")

        medidas = ttk.LabelFrame(self.aba_imagem, text="Objetos", padding=6)
        medidas.pack(fill="x", pady=(8, 0))
        self.contagem = ttk.Label(medidas, text="Objetos encontrados: —")
        self.contagem.pack(anchor="w", pady=(0, 4))

        colunas = ("objeto", "area", "perimetro", "diametro")
        self.tabela = ttk.Treeview(medidas, columns=colunas, show="headings", height=5)
        titulos = ("Objeto", "Área (px²)", "Perímetro (px)", "Diâmetro (px)")
        for coluna, titulo in zip(colunas, titulos):
            self.tabela.heading(coluna, text=titulo)
            self.tabela.column(coluna, width=100, anchor="center")
        rolagem = ttk.Scrollbar(medidas, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="x", expand=True)
        rolagem.pack(side="right", fill="y")

    def criar_aba_camera(self):
        barra = ttk.Frame(self.aba_camera)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Câmera").pack(side="left", padx=(0, 4))
        self.seletor_camera = ttk.Spinbox(barra, from_=0, to=5,
                                          textvariable=self.indice_camera,
                                          width=3, state="readonly")
        self.seletor_camera.pack(side="left")
        self.botao_iniciar_camera = ttk.Button(barra, text="Iniciar", command=self.iniciar_camera)
        self.botao_iniciar_camera.pack(side="left", padx=6)
        self.botao_parar_camera = ttk.Button(barra, text="Parar", command=self.parar_camera,
                                              state="disabled")
        self.botao_parar_camera.pack(side="left")
        ttk.Button(barra, text="Sem efeito", command=self.remover_efeito_video).pack(side="left", padx=6)

        linha_efeito = ttk.Frame(self.aba_camera)
        linha_efeito.pack(fill="x", pady=(0, 8))
        ttk.Label(linha_efeito, text="Operação: ").pack(side="left")
        ttk.Label(linha_efeito, textvariable=self.operacao_video).pack(side="left")

        previas = ttk.Frame(self.aba_camera)
        previas.pack(fill="both", expand=True)
        self.previa_camera = self.criar_previa(previas, "Câmera")
        self.previa_video = self.criar_previa(previas, "Resultado")

        controles = ttk.LabelFrame(self.aba_camera, text="Objeto e música", padding=8)
        controles.pack(fill="x", pady=(8, 0))
        linha = ttk.Frame(controles)
        linha.pack(fill="x")
        ttk.Button(linha, text="Selecionar objeto para rastrear",
                   command=self.selecionar_objeto).pack(side="left")
        ttk.Button(linha, text="Parar rastreamento",
                   command=self.parar_rastreamento).pack(side="left", padx=6)
        ttk.Label(controles, textvariable=self.situacao_rastreamento).pack(anchor="w", pady=4)

        linha_referencia = ttk.Frame(controles)
        linha_referencia.pack(fill="x", pady=4)
        ttk.Button(linha_referencia, text="Abrir referência",
                   command=self.escolher_referencia).pack(side="left")
        ttk.Button(linha_referencia, text="Selecionar no vídeo",
                   command=self.selecionar_referencia).pack(side="left", padx=6)
        ttk.Label(linha_referencia, text="Semelhança mínima").pack(side="left", padx=6)
        ttk.Spinbox(linha_referencia, from_=0.5, to=1.0, increment=0.05,
                    textvariable=self.semelhanca_minima, width=5,
                    state="readonly").pack(side="left")
        self.nome_referencia = ttk.Label(controles, text="Nenhuma referência selecionada",
                                          wraplength=650)
        self.nome_referencia.pack(anchor="w")
        ttk.Checkbutton(controles, text="Identificar objeto específico e tocar música",
                         variable=self.identificar_objeto,
                         command=self.alterar_identificacao).pack(anchor="w", pady=4)
        ttk.Label(controles, textvariable=self.situacao_identificacao).pack(anchor="w", pady=(0, 4))
        linha_audio = ttk.Frame(controles)
        linha_audio.pack(fill="x")
        ttk.Button(linha_audio, text="Escolher música",
                   command=self.escolher_musica).pack(side="left")
        ttk.Button(linha_audio, text="Parar música", command=audio.parar_musica).pack(side="left", padx=6)
        self.nome_musica = ttk.Label(controles, text="Nenhuma música selecionada", wraplength=650)
        self.nome_musica.pack(anchor="w", pady=(4, 0))

    def mudar_aba(self, evento=None):
        modo_imagem = self.abas.select() == str(self.aba_imagem)
        for botao in self.botoes_analise:
            botao.configure(state="normal" if modo_imagem else "disabled")

    def exibir_imagem(self, imagem, previa):
        # A cópia reduzida serve apenas para exibição; preserva a resolução original.
        copia = imagem.copy()
        largura = max(previa.winfo_width(), 300)
        altura = max(previa.winfo_height(), 250)
        copia.thumbnail((largura, altura))
        foto = ImageTk.PhotoImage(copia)
        previa.configure(image=foto, text="")
        previa.image = foto  # Mantém a imagem disponível para o Tkinter.

    def abrir_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Abrir imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                       ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        with Image.open(caminho) as imagem:
            self.imagem_original = imagem.convert("RGB")
        self.abas.select(self.aba_imagem)
        self.nome_arquivo.configure(text=caminho)
        self.exibir_imagem(self.imagem_original, self.previa_original)
        self.restaurar_original()

    def mostrar_resultado(self, imagem):
        """Recebe uma imagem PIL produzida pelo processamento."""
        self.imagem_resultado = imagem.copy()
        self.exibir_imagem(self.imagem_resultado, self.previa_resultado)

    def restaurar_original(self):
        if self.imagem_original is None:
            self.status.set("Abra uma imagem primeiro.")
            return
        self.mostrar_resultado(self.imagem_original)
        self.tabela.delete(*self.tabela.get_children())
        self.contagem.configure(text="Objetos encontrados: —")
        self.status.set("Imagem original restaurada.")

    def salvar_resultado(self):
        if self.imagem_resultado is None:
            self.status.set("Abra uma imagem primeiro.")
            return
        caminho = filedialog.asksaveasfilename(
            title="Salvar resultado", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")],
        )
        if caminho:
            self.imagem_resultado.convert("RGB").save(caminho)
            self.status.set("Resultado salvo.")

    def mostrar_objetos(self, objetos):
        """Recebe linhas no formato (rótulo, área, perímetro, diâmetro)."""
        self.tabela.delete(*self.tabela.get_children())
        for objeto in objetos:
            self.tabela.insert("", "end", values=objeto)
        self.contagem.configure(text=f"Objetos encontrados: {len(objetos)}")

    def mostrar_histograma(self, imagem):
        # Mostra o histograma do resultado atual sem modificar a imagem.
        janela_histograma = tk.Toplevel(self.janela)
        janela_histograma.title("Histograma do resultado atual")
        janela_histograma.geometry("700x550")

        figura = Figure(figsize=(7, 5), dpi=100, tight_layout=True)
        imagem_cinza = conversoes.cinza(imagem)
        contagem = histograma.calcular_histograma(imagem_cinza)

        if imagem.ndim == 3:
            grafico_cinza = figura.add_subplot(211)
            grafico_rgb = figura.add_subplot(212)
            vermelho, verde, azul = histograma.calcular_histogramas_rgb(imagem)
            grafico_rgb.step(range(256), vermelho, color="red", label="Vermelho", where="mid")
            grafico_rgb.step(range(256), verde, color="green", label="Verde", where="mid")
            grafico_rgb.step(range(256), azul, color="blue", label="Azul", where="mid")
            grafico_rgb.set_title("Canais RGB")
            grafico_rgb.set_xlabel("Intensidade")
            grafico_rgb.set_ylabel("Quantidade de pixels")
            grafico_rgb.set_xlim(-0.5, 255.5)
            grafico_rgb.set_ylim(bottom=0)
            grafico_rgb.legend()
        else:
            grafico_cinza = figura.add_subplot(111)

        grafico_cinza.bar(range(256), contagem, color="gray", width=1)
        grafico_cinza.set_title("Níveis de cinza")
        grafico_cinza.set_xlabel("Intensidade")
        grafico_cinza.set_ylabel("Quantidade de pixels")
        grafico_cinza.set_xlim(-0.5, 255.5)
        grafico_cinza.set_ylim(bottom=0)

        canvas = FigureCanvasTkAgg(figura, master=janela_histograma)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        janela_histograma.canvas = canvas
        self.status.set("Histograma do resultado atual exibido.")

    def mostrar_componentes(self, rotulos, componentes):
        # A visualização colorida fica separada para preservar a imagem binária.
        janela = tk.Toplevel(self.janela)
        janela.title("Objetos rotulados")
        janela.geometry("700x550")
        ttk.Label(janela, text=f"Objetos brancos encontrados: {len(componentes)}",
                   padding=8).pack()
        previa = ttk.Label(janela, anchor="center")
        previa.pack(fill="both", expand=True, padx=8, pady=8)

        imagem = Image.fromarray(objetos.colorir(rotulos))
        desenho = ImageDraw.Draw(imagem)
        for i in range(len(componentes)):
            y, x = componentes[i][0]
            desenho.text((x, y), str(i + 1), fill="white", stroke_width=1,
                          stroke_fill="black")
        janela.update_idletasks()
        self.exibir_imagem(imagem, previa)

    def analisar_objetos(self, imagem, calcular_medidas):
        binaria = conversoes.cinza(imagem)
        if not np.all((binaria == 0) | (binaria == 255)):
            self.status.set("Use Otsu primeiro. A análise precisa de objetos brancos e fundo preto.")
            return

        conectividade = int(self.conectividade.get())
        rotulos, componentes = objetos.rotular(binaria, conectividade)
        if calcular_medidas:
            medidas = objetos.medir_objetos(rotulos, componentes)
        else:
            medidas = []
            for i in range(len(componentes)):
                medidas.append((i + 1, "—", "—", "—"))

        self.mostrar_objetos(medidas)
        self.mostrar_componentes(rotulos, componentes)
        self.status.set(f"{len(componentes)} objetos; conectividade {conectividade}. "
                        "Diâmetro: maior distância entre centros dos pixels do contorno.")

    def executar_operacao(self, nome):
        # As operações de imagem usam o resultado atual, permitindo combiná-las.
        modo = "imagem" if self.abas.select() == str(self.aba_imagem) else "vídeo"
        if modo == "imagem" and self.imagem_original is None:
            self.status.set("Abra uma imagem primeiro.")
            return
        if modo == "vídeo":
            if nome == "Canny" and self.limiar_minimo.get() > self.limiar_maximo.get():
                self.status.set("O limiar mínimo deve ser menor ou igual ao máximo.")
                return
            self.operacao_video.set(nome)
            self.status.set(f"{nome} selecionado para o vídeo.")
            return

        imagem = np.array(self.imagem_resultado)
        mensagem = f"{nome} aplicado."

        if nome == "Níveis de cinza":
            resultado = conversoes.cinza(imagem)
        elif nome == "Negativo":
            resultado = conversoes.negativo(imagem)
        elif nome == "Binário — Otsu":
            limiar, resultado = conversoes.otsu(imagem)
            mensagem = f"Otsu aplicado. Limiar automático: {limiar}."
        elif nome == "Média" or nome == "Mediana":
            tamanho = self.tamanho_filtro.get()
            resultado = filtros.suavizar(imagem, tamanho, nome)
            mensagem = f"{nome} aplicado com janela {tamanho} × {tamanho}."
        elif nome == "Canny":
            minimo = self.limiar_minimo.get()
            maximo = self.limiar_maximo.get()
            if minimo > maximo:
                self.status.set("O limiar mínimo deve ser menor ou igual ao máximo.")
                return
            resultado = filtros.canny(imagem, minimo, maximo)
            mensagem = f"Canny aplicado com limiares {minimo} e {maximo}."
        elif nome in ("Erosão", "Dilatação", "Abertura", "Fechamento"):
            tamanho = self.tamanho_elemento.get()
            imagem_cinza = conversoes.cinza(imagem)
            if nome == "Erosão":
                resultado = morfologia.erosao(imagem_cinza, tamanho)
            elif nome == "Dilatação":
                resultado = morfologia.dilatacao(imagem_cinza, tamanho)
            elif nome == "Abertura":
                resultado = morfologia.abertura(imagem_cinza, tamanho)
            else:
                resultado = morfologia.fechamento(imagem_cinza, tamanho)
            mensagem = f"{nome} aplicado em cinza com elemento {tamanho} × {tamanho}."
        elif nome == "Detectar e contar objetos" or nome == "Calcular medidas":
            self.analisar_objetos(imagem, nome == "Calcular medidas")
            return
        elif nome == "Histograma":
            self.mostrar_histograma(imagem)
            return
        else:
            self.status.set(f"{nome}: processamento ainda não implementado.")
            return

        self.mostrar_resultado(Image.fromarray(resultado))
        self.tabela.delete(*self.tabela.get_children())
        self.contagem.configure(text="Objetos encontrados: —")
        self.status.set(mensagem)

    def iniciar_camera(self):
        if self.camera is not None:
            return
        indice = self.indice_camera.get()
        self.camera = entrada.abrir_camera(indice)
        if self.camera is None:
            self.status.set(f"Câmera {indice} não disponível. Conecte uma webcam ou escolha outro índice.")
            return

        self.botao_iniciar_camera.configure(state="disabled")
        self.botao_parar_camera.configure(state="normal")
        self.seletor_camera.configure(state="disabled")
        self.status.set(f"Câmera {indice} iniciada.")
        self.atualizar_camera()

    def atualizar_camera(self):
        self.atualizacao_camera = None
        if self.camera is None:
            return

        sucesso, quadro = self.camera.read()
        if not sucesso:
            self.parar_camera()
            self.status.set("Não foi possível receber o quadro da câmera. Tente iniciar novamente.")
            return

        self.ultimo_quadro = quadro
        operacao = self.operacao_video.get()
        minimo = self.limiar_minimo.get()
        maximo = self.limiar_maximo.get()
        if operacao == "Canny" and minimo > maximo:
            resultado = quadro
            self.status.set("Ajuste os limiares: o mínimo não pode passar do máximo.")
        else:
            resultado = video.processar_quadro(quadro, operacao,
                                               self.tamanho_filtro.get(), minimo, maximo,
                                               self.tamanho_elemento.get())

        exibicao = quadro.copy()
        if self.rastreador is not None:
            encontrado, regiao = self.rastreador.update(quadro)
            if encontrado:
                exibicao = video.desenhar_caixa(exibicao, regiao, "Rastreamento", (0, 255, 0))
                resultado = video.desenhar_caixa(resultado, regiao, "Rastreamento", (0, 255, 0))
            else:
                self.rastreador = None
                self.situacao_rastreamento.set("Objeto perdido. Selecione novamente.")

        if self.identificar_objeto.get():
            regiao = self.atualizar_identificacao(quadro)
            if regiao is not None:
                exibicao = video.desenhar_caixa(exibicao, regiao, "Objeto identificado", (0, 255, 255))
                resultado = video.desenhar_caixa(resultado, regiao, "Objeto identificado", (0, 255, 255))

        self.exibir_imagem(Image.fromarray(video.converter_rgb(exibicao)), self.previa_camera)
        self.exibir_imagem(Image.fromarray(video.converter_rgb(resultado)), self.previa_video)
        # Agenda o próximo quadro sem usar um laço que bloqueie a janela.
        self.atualizacao_camera = self.janela.after(30, self.atualizar_camera)

    def parar_camera(self):
        if self.atualizacao_camera is not None:
            self.janela.after_cancel(self.atualizacao_camera)
            self.atualizacao_camera = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.ultimo_quadro = None
        self.parar_rastreamento()
        self.desativar_identificacao()
        self.botao_iniciar_camera.configure(state="normal")
        self.botao_parar_camera.configure(state="disabled")
        self.seletor_camera.configure(state="readonly")
        for previa in (self.previa_camera, self.previa_video):
            previa.configure(image="", text="Câmera parada")
            previa.image = None
        self.status.set("Câmera parada.")

    def remover_efeito_video(self):
        self.operacao_video.set("Original")
        self.status.set("Vídeo sem efeito.")

    def fechar(self):
        self.parar_camera()
        audio.fechar_audio()
        self.janela.destroy()

    def selecionar_objeto(self, usar_como_referencia=False):
        if self.ultimo_quadro is None:
            self.status.set("Inicie a câmera antes de selecionar o objeto.")
            return

        # Pausa os quadros enquanto o usuário escolhe o retângulo no OpenCV.
        if self.atualizacao_camera is not None:
            self.janela.after_cancel(self.atualizacao_camera)
            self.atualizacao_camera = None
        regiao = video.selecionar_regiao(self.ultimo_quadro)
        x, y, largura, altura = regiao
        if largura > 0 and altura > 0:
            if usar_como_referencia:
                recorte = self.ultimo_quadro[y:y + altura, x:x + largura]
                self.definir_referencia(recorte, "Recorte selecionado no vídeo")
            else:
                self.rastreador = video.iniciar_rastreamento(self.ultimo_quadro, regiao)
                self.situacao_rastreamento.set("Rastreamento CSRT ativo")
                self.status.set("Objeto selecionado. A caixa verde acompanha o movimento.")
        else:
            self.status.set("Seleção cancelada.")
        self.atualizacao_camera = self.janela.after(30, self.atualizar_camera)

    def parar_rastreamento(self):
        self.rastreador = None
        self.situacao_rastreamento.set("Sem rastreamento")

    def selecionar_referencia(self):
        self.selecionar_objeto(usar_como_referencia=True)

    def escolher_referencia(self):
        caminho = filedialog.askopenfilename(
            title="Escolher uma imagem recortada do objeto",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")],
        )
        if not caminho:
            return
        with Image.open(caminho) as imagem:
            referencia = cv2.cvtColor(np.array(imagem.convert("RGB")), cv2.COLOR_RGB2BGR)
        self.definir_referencia(referencia, caminho)

    def definir_referencia(self, referencia, nome):
        if not np.any(referencia):
            self.status.set("Escolha uma referência com o objeto visível, não uma imagem toda preta.")
            return
        self.desativar_identificacao()
        self.referencia_objeto = referencia.copy()
        self.nome_referencia.configure(text=nome)
        self.status.set("Referência selecionada. Use um recorte do objeto no tamanho em que aparece no vídeo.")

    def desativar_identificacao(self):
        self.identificar_objeto.set(False)
        self.objeto_presente = False
        self.quadros_presente = 0
        self.quadros_ausente = 0
        self.situacao_identificacao.set("Identificação desativada")
        audio.parar_musica()

    def alterar_identificacao(self):
        if not self.identificar_objeto.get():
            self.desativar_identificacao()
            return
        if self.referencia_objeto is None or not self.caminho_musica:
            self.desativar_identificacao()
            self.status.set("Escolha a imagem do objeto e uma música antes de ativar a identificação.")
            return
        if not audio.carregar_musica(self.caminho_musica):
            self.desativar_identificacao()
            self.status.set("Não foi possível carregar a música. Verifique o arquivo e a saída de áudio.")
            return
        self.objeto_presente = False
        self.quadros_presente = 0
        self.quadros_ausente = 0
        self.situacao_identificacao.set("Procurando o objeto")
        self.status.set("Identificação ativada. A música toca quando o objeto aparecer.")

    def atualizar_identificacao(self, quadro):
        altura, largura = self.referencia_objeto.shape[:2]
        if altura > quadro.shape[0] or largura > quadro.shape[1]:
            self.desativar_identificacao()
            self.status.set("A referência é maior que o vídeo. Selecione um recorte menor do objeto.")
            return None
        regiao, semelhanca = video.localizar_objeto(quadro, self.referencia_objeto,
                                                    self.semelhanca_minima.get())
        if regiao is not None:
            self.quadros_presente += 1
            self.quadros_ausente = 0
            # Confirma em três quadros para evitar disparos por uma coincidência.
            if self.quadros_presente >= 3:
                self.situacao_identificacao.set(f"Objeto encontrado ({semelhanca:.0%} de semelhança)")
                if not self.objeto_presente:
                    audio.tocar_musica()
                    self.objeto_presente = True
            return regiao

        self.quadros_presente = 0
        self.quadros_ausente += 1
        self.situacao_identificacao.set("Procurando o objeto")
        # Só permite outro disparo depois de cinco quadros sem encontrar o objeto.
        if self.quadros_ausente >= 5:
            self.objeto_presente = False
        return None

    def escolher_musica(self):
        caminho = filedialog.askopenfilename(
            title="Escolher música",
            filetypes=[("Áudio", "*.mp3 *.wav *.ogg"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.desativar_identificacao()
            self.caminho_musica = caminho
            self.nome_musica.configure(text=caminho)
            self.status.set("Música selecionada.")


def iniciar_interface():
    janela = tk.Tk()
    Interface(janela)
    janela.mainloop()


if __name__ == "__main__":
    iniciar_interface()
