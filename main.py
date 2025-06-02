# ================================
# Author: Francisco de Freitas Kemle
# JOGO: Herói dos Pampas
# Desenvolvido em Python com Pygame
# O jogador controla um gaúcho que atira chimarrões nos inimigos.
# As fases fazem alusão a cidades do Rio Grande do Sul.
# ================================

# Importação das bibliotecas essenciais
import pygame   # Biblioteca principal para jogos 2D em Python
import random   # Para gerar posições aleatórias dos inimigos
import sys      # Para encerrar o jogo corretamente
import os       # Para lidar com caminhos de arquivos

# Inicializa todos os módulos do Pygame
pygame.init()

# Define as dimensões da tela do jogo
LARGURA, ALTURA = 1536, 1024  # Largura e altura da janela
TELA = pygame.display.set_mode((LARGURA, ALTURA))  # Cria a janela do jogo
pygame.display.set_caption("Herói dos Pampas")  # Define o título da janela

# Define o caminho da pasta onde estão os assets (imagens, sons, etc.)
CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# Lista com os arquivos dos fundos de cada fase
# As imagens são redimensionadas para o tamanho da tela
# A última imagem é usada como tela final de sucesso
# (e.g., quando o jogador termina o jogo com vitória)
diretorios_fundos = [
    'fundo_pampa.jpg',     # Menu
    'fundo_pampa-2.jpg',   # Fase 1
    'fundo_pampa-3.jpg',   # Fase 2
    'fundo_pampa-4.jpg',   # Fase 3
    'fundo_pampa-5.jpg',   # Fase 4
    'fundo_pampa-6.jpg',   # Fase 5
    'fundo_pampa-7.jpg',   # Fase 6
    'fundo_pampa-8.jpg',   # Fase 7
    'fundo_pampa-9.jpg',   # Fase 8
    'success.jpg'          # Fundo final (usado para proteção de índice)
]
fundos = [
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, fundo)), (LARGURA, ALTURA))
    for fundo in diretorios_fundos
]

# Carrega a imagem do jogador (gaúcho) e redimensiona
GAUCHO = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'gaucho.png')), (120, 120))

# Carrega múltiplos sprites de inimigos com tamanhos fixos
sprites_inimigos = [
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo.png')), (120, 120)),
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo-2.png')), (120, 120)),
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo-3.png')), (120, 120)),
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo-4.png')), (120, 120)),
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo-5.png')), (120, 120))
]

# Carrega o sprite do chimarrão (projetil) e redimensiona
BALA = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'bala.png')), (70, 70))

# Tenta carregar os arquivos de som (tiro e impacto)
try:
    TIRO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'tiro.wav'))
    IMPACTO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'impacto.wav'))
except:
    TIRO_SOM = IMPACTO_SOM = None  # Se der erro, desativa os sons

# Carrega imagem de Game Over redimensionada
GAME_OVER_IMG = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'game-over.jpg')), (900, 450))

# Carrega imagem final de sucesso redimensionada
FINAL_SUCCESS_IMG = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'success.jpg')), (900, 450))

# Define os frames por segundo do jogo
FPS = 60
clock = pygame.time.Clock()

# ================================
# CLASSES PRINCIPAIS DO JOGO
# ================================

# Classe que representa o jogador (gaúcho)
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = GAUCHO
        self.rect = self.image.get_rect()
        self.rect.center = (100, ALTURA // 2)  # Começa centralizado verticalmente na lateral esquerda
        self.vida = 10  # Número de vidas

    # Atualiza posição com base nas teclas pressionadas
    def update(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < ALTURA:
            self.rect.y += 5

# Classe que representa o inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(sprites_inimigos)
        self.rect = self.image.get_rect()
        self.rect.x = LARGURA  # Começa na lateral direita da tela
        self.rect.y = random.randint(0, ALTURA - self.rect.height)  # Posição vertical aleatória

    # Move o inimigo para a esquerda
    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()  # Remove se sair da tela

# Classe que representa a bala (chimarrão)
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BALA
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    # Move a bala para a direita
    def update(self):
        self.rect.x += 10
        if self.rect.left > LARGURA:
            self.kill()  # Remove se sair da tela

# ================================
# CONFIGURAÇÕES E VARIÁVEIS DO JOGO
# ================================

# Instancia o jogador e grupos de sprites
jogador = Jogador()
jogador_group = pygame.sprite.Group(jogador)
inimigos = pygame.sprite.Group()
balas = pygame.sprite.Group()

# Define a fonte usada nos textos
fonte = pygame.font.SysFont("calibri", 40, bold=True)

# Cria evento para gerar inimigos a cada 0.5 segundos
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 500)

# Variáveis de controle de jogo
pontos = 0
fase_atual = 0  # Começa no menu

# Nomes das fases baseados em cidades do RS
nomes_fase = {
    1: "Fase Bagé",
    2: "Fase Pelotas",
    3: "Fase Rio Grande",
    4: "Fase Aceguá",
    5: "Fase Lajeado",
    6: "Fase Gramado",
    7: "Fase Campo Bom",
    8: "Fase Piratini"
}

# ================================
# LOOP PRINCIPAL DO JOGO
# ================================

# Flag para manter o jogo rodando
rodando = True
while rodando:
    clock.tick(FPS)  # Controla os FPS
    keys = pygame.key.get_pressed()  # Verifica teclas pressionadas

    # Tela de menu inicial
    if fase_atual == 0:
        TELA.blit(fundos[0], (0, 0))
        texto_menu = fonte.render("Pressione ENTER para iniciar", True, (255, 255, 255))
        TELA.blit(texto_menu, ((LARGURA - texto_menu.get_width()) // 2, (ALTURA - texto_menu.get_height()) // 2))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                fase_atual = 1
        continue

    # Define a fase de acordo com a pontuação
    if pontos >= 800:
        fase_atual = 9
    elif pontos >= 700:
        fase_atual = 8
    elif pontos >= 600:
        fase_atual = 7
    elif pontos >= 500:
        fase_atual = 6
    elif pontos >= 400:
        fase_atual = 5
    elif pontos >= 300:
        fase_atual = 4
    elif pontos >= 200:
        fase_atual = 3
    elif pontos >= 100:
        fase_atual = 2

    # Exibe o fundo da fase atual (protege o índice com min)
    TELA.blit(fundos[min(fase_atual, len(fundos)-1)], (0, 0))

    # Captura eventos do jogo
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == TIMER_EVENT:
            inimigos.add(Inimigo())
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            nova_bala = Bala(jogador.rect.right, jogador.rect.centery)
            balas.add(nova_bala)
            if TIRO_SOM:
                TIRO_SOM.play()

    # Atualiza todos os sprites
    jogador.update(keys)
    inimigos.update()
    balas.update()

    # Desenha todos os sprites na tela
    jogador_group.draw(TELA)
    inimigos.draw(TELA)
    balas.draw(TELA)

    # Verifica colisões entre balas e inimigos
    for bala in pygame.sprite.groupcollide(balas, inimigos, True, True):
        pontos += 10
        if IMPACTO_SOM:
            IMPACTO_SOM.play()

    # Verifica colisão entre inimigos e o jogador
    if pygame.sprite.spritecollideany(jogador, inimigos):
        jogador.vida -= 1
        for inimigo in inimigos:
            inimigo.kill()

    # Mostra texto com pontuação e vida
    texto_pontos = fonte.render(f"Pontos: {pontos}  Vida: {jogador.vida}", True, (255, 255, 255))
    TELA.blit(texto_pontos, (20, 90))

    # Mostra o nome da fase atual
    if fase_atual > 0 and fase_atual <= 8:
        texto_fase = fonte.render(nomes_fase.get(fase_atual, ""), True, (255, 255, 255))
        TELA.blit(texto_fase, ((LARGURA - texto_fase.get_width()) // 2, 90))

    # Atualiza o conteúdo da tela
    pygame.display.flip()

    # Se perder todas as vidas: tela de Game Over
    if jogador.vida <= 0:
        TELA.fill((0, 0, 0))
        TELA.blit(GAME_OVER_IMG, ((LARGURA - 800) // 2, (ALTURA - 400) // 2))
        pygame.display.flip()
        pygame.time.wait(4000)
        rodando = False

    # Se chegar à fase final: mostra imagem de sucesso
    if fase_atual == 9:
        TELA.fill((0, 0, 0))
        TELA.blit(FINAL_SUCCESS_IMG, ((LARGURA - 800) // 2, (ALTURA - 400) // 2))
        pygame.display.flip()
        pygame.time.wait(4000)
        rodando = False

# Finaliza o jogo
pygame.quit()
sys.exit()
