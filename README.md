# Trabalho prático de Processamento Digital de Imagens

Programa em Python com interface Tkinter para processar imagens e vídeo da câmera.
Desenvolvido para a disciplina de Computação Gráfica e Processamento Digital de Imagens.

## Instalação e execução

Use Python com suporte a Tkinter e uma sessão gráfica. O projeto foi desenvolvido com Python 3.12.

Se usar um ambiente virtual, ative-o antes de executar os comandos.

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Inicie o programa:

```bash
python main.py
```

## Modo Imagem

1. Abra a aba **Imagem** e clique em **Abrir imagem**.
2. Escolha uma operação no painel esquerdo.
3. Ajuste os parâmetros quando necessário e aplique a operação.
4. Use **Restaurar original** para recomeçar ou **Salvar resultado** para exportar em PNG ou JPEG.

A imagem original fica preservada. As operações seguintes usam o resultado atual,
permitindo combinar etapas. O tamanho mostrado na tela é apenas uma prévia;
o processamento e o salvamento usam a resolução completa.

### Operações disponíveis

| Operação | Resultado |
|---|---|
| Níveis de cinza | Converte RGB usando pesos 0,299, 0,587 e 0,114 |
| Negativo | Inverte cada intensidade com `255 - valor` |
| Binário — Otsu | Escolhe automaticamente um limiar e produz pixels 0 ou 255 |
| Média | Substitui o pixel pela média da janela |
| Mediana | Substitui o pixel pelo valor central dos vizinhos ordenados |
| Canny | Detecta bordas usando suavização gaussiana e dois limiares |
| Erosão | Usa o menor valor da vizinhança quadrada |
| Dilatação | Usa o maior valor da vizinhança quadrada |
| Abertura | Erosão seguida de dilatação |
| Fechamento | Dilatação seguida de erosão |
| Histograma | Mostra a contagem por intensidade e, para RGB, os três canais |
| Detectar e contar objetos | Rotula componentes conexos e mostra a contagem |
| Calcular medidas | Calcula área, perímetro e diâmetro de cada objeto |

## Modo Câmera

1. Conecte uma webcam e abra a aba **Câmera**.
2. Escolha o índice do dispositivo. Comece com **0**; se necessário, tente outro índice.
3. Clique em **Iniciar**.
4. Escolha uma operação no painel esquerdo para aplicá-la a cada quadro.
5. Use **Sem efeito** para voltar ao vídeo original e **Parar** para liberar a câmera.

Os parâmetros podem ser alterados durante o vídeo. Uma operação é aplicada por vez,
sempre sobre o quadro original.

### Rastreamento

1. Com a câmera iniciada, clique em **Selecionar objeto para rastrear**.
2. Na janela do OpenCV, arraste um retângulo ao redor do objeto.
3. Confirme com **Enter** ou cancele com **Esc**.

A captura fica pausada durante a seleção. O rastreador **CSRT** acompanha o objeto
e desenha uma caixa verde sobre o vídeo. Se ele perder o objeto, selecione novamente.
Use **Parar rastreamento** para encerrar apenas esse recurso.

### Identificação de objeto e música

1. Use **Abrir referência** para escolher uma imagem recortada do objeto, ou
   **Selecionar no vídeo** para recortá-lo no quadro atual, arrastando e confirmando com Enter.
2. Clique em **Escolher música** e selecione um arquivo MP3, WAV ou OGG.
3. Ajuste **Semelhança mínima**, se necessário. O valor inicial é `0.9`.
4. Marque **Identificar objeto específico e tocar música**.

A identificação procura a referência em todo o quadro usando comparação de imagens
(`matchTemplate`). Ela funciona independentemente do rastreamento e desenha uma caixa amarela.
A semelhança exibida é uma pontuação de comparação, não uma probabilidade de reconhecimento.

Use uma referência recortada próxima ao objeto, com tamanho, orientação e iluminação
semelhantes aos do vídeo. Este método não reconhece uma categoria inteira de objetos
e não procura automaticamente diferentes escalas ou rotações.

O objeto precisa ser encontrado em três quadros seguidos para disparar a música.
Ela não reinicia enquanto ele permanece visível.

Use **Parar música** para interromper o áudio. Desmarcar a identificação ou parar a câmera
também interrompe a música. A troca de referência ou música desativa a identificação;
marque a opção novamente para usar a nova escolha.

## Organização

```text
main.py                 Inicia a interface
requirements.txt        Dependências externas
.gitignore              Arquivos locais e gerados que o Git deve ignorar
pdi/
    interface.py        Janela, controles e integração
    entrada.py          Abertura e configuração da câmera
    conversoes.py       Cinza, negativo e Otsu
    filtros.py          Média, mediana e Canny
    morfologia.py       Erosão, dilatação, abertura e fechamento
    histograma.py       Contagens de intensidade e canais RGB
    objetos.py          Componentes conexos e medidas
    video.py            Processamento dos quadros, rastreamento e identificação
    audio.py            Carregamento, reprodução e parada da música
```

Os arquivos podem ser escolhidos de qualquer pasta pelos controles da interface.
