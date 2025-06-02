# Importação das bibliotecas essenciais
import pygame  # Biblioteca para jogos em Python
import random  # Para gerar números aleatórios (posições dos inimigos)
import sys     # Para finalizar o jogo corretamente
import os      # Para manipular caminhos de arquivos

# Inicializa o Pygame
pygame.init()

# Define dimensões da tela
LARGURA, ALTURA = 1536, 1024
TELA = pygame.display.set_mode((LARGURA, ALTURA))  # Cria janela do jogo
pygame.display.set_caption("Herói dos Pampas")  # Título da janela

# Caminho dos assets (imagens e sons)
CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# Carrega os fundos das fases e redimensiona para caber na tela
diretorios_fundos = [
    'fundo_pampa.jpg',     # Menu
    'fundo_pampa-2.jpg',   # Fase 1
    'fundo_pampa-3.jpg',   # Fase 2
    'fundo_pampa-4.jpg',   # Fase 3
    'fundo_pampa-5.jpg',   # Fase 4
    'fundo_pampa-6.jpg'    # Fase 5
]
fundos = [pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, fundo)), (LARGURA, ALTURA)) for fundo in diretorios_fundos]

# Carrega e redimensiona os sprites
GAUCHO = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'gaucho.png')), (100, 100))
INIMIGO = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo.png')), (100, 100))
BALA = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'bala.png')), (50, 50))  # Chimarrão como bala

# Tenta carregar sons
try:
    TIRO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'tiro.wav'))
    IMPACTO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'impacto.wav'))
except:
    TIRO_SOM = IMPACTO_SOM = None

# Configurações de tempo e desempenho
FPS = 60
clock = pygame.time.Clock()

# Classe do jogador (herda de Sprite)
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = GAUCHO
        self.rect = self.image.get_rect()
        self.rect.center = (100, ALTURA // 2)
        self.vida = 10  # Vidas do jogador

    def update(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < ALTURA:
            self.rect.y += 5

# Classe dos inimigos
class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = INIMIGO
        self.rect = self.image.get_rect()
        self.rect.x = LARGURA
        self.rect.y = random.randint(0, ALTURA - self.rect.height)

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

# Classe das balas (chimarrão)
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BALA
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += 10
        if self.rect.left > LARGURA:
            self.kill()

# Grupos de sprites
jogador = Jogador()
jogador_group = pygame.sprite.Group(jogador)
inimigos = pygame.sprite.Group()
balas = pygame.sprite.Group()

# Fonte para textos
fonte = pygame.font.SysFont("arial", 48)

# Evento para gerar inimigos
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1500)

# Inicializa pontuação e controle de fase
pontos = 0
fase_atual = 0
nomes_fase = {
    1: "Fase Bagé",
    2: "Fase Lajeado",
    3: "Fase Gramado",
    4: "Fase Campo Bom",
    5: "Fase Piratini"
}

# Loop principal do jogo
rodando = True
while rodando:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    # Tela de menu
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

    # Atualiza fase com base nos pontos
    if pontos >= 400:
        fase_atual = 5
    elif pontos >= 300:
        fase_atual = 4
    elif pontos >= 200:
        fase_atual = 3
    elif pontos >= 100:
        fase_atual = 2

    # Exibe fundo da fase
    TELA.blit(fundos[fase_atual], (0, 0))

    # Eventos do jogo
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

    # Atualiza e desenha sprites
    jogador.update(keys)
    inimigos.update()
    balas.update()

    jogador_group.draw(TELA)
    inimigos.draw(TELA)
    balas.draw(TELA)

    # Colisões entre balas e inimigos
    for bala in pygame.sprite.groupcollide(balas, inimigos, True, True):
        pontos += 10
        if IMPACTO_SOM:
            IMPACTO_SOM.play()

    # Colisão entre inimigos e jogador
    if pygame.sprite.spritecollideany(jogador, inimigos):
        jogador.vida -= 1
        for inimigo in inimigos:
            inimigo.kill()
        if jogador.vida <= 0:
            rodando = False

    # Texto de pontuação centralizado
    texto_pontos = fonte.render(f"Pontos: {pontos}  Vida: {jogador.vida}", True, (255, 255, 255))
    TELA.blit(texto_pontos, ((LARGURA - texto_pontos.get_width()) // 2, 30))

    # Nome da fase (acima do jogador)
    if fase_atual > 0:
        texto_fase = fonte.render(nomes_fase.get(fase_atual, ""), True, (255, 255, 255))
        TELA.blit(texto_fase, ((LARGURA - texto_fase.get_width()) // 2, 90))

    # Atualiza tela
    pygame.display.flip()

# Sai do jogo ao terminar
pygame.quit()
sys.exit()
