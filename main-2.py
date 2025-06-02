import pygame
import random
import sys
import os

# Inicialização da biblioteca Pygame
pygame.init()

# Define as dimensões da tela (aumentamos a altura para 1600)
LARGURA, ALTURA = 1500, 1034
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Herói dos Pampas")

# Carrega imagens (assets) da pasta 'assets' e redimensiona o fundo para ocupar toda a tela
CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
FUNDO = pygame.transform.scale(
    pygame.image.load(os.path.join(CAMINHO_ASSETS, 'fundo_pampa.jpg')),
    (LARGURA, ALTURA)
)
GAUCHO = pygame.image.load(os.path.join(CAMINHO_ASSETS, 'gaucho.png'))
INIMIGO = pygame.image.load(os.path.join(CAMINHO_ASSETS, 'inimigo.png'))
BALA = pygame.image.load(os.path.join(CAMINHO_ASSETS, 'bala.png'))

# Tenta carregar os sons (opcional)
try:
    TIRO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'tiro.wav'))
    IMPACTO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'impacto.wav'))
except:
    TIRO_SOM = IMPACTO_SOM = None

# Redimensiona os sprites do jogador, inimigo e bala
GAUCHO = pygame.transform.scale(GAUCHO, (100, 100))
INIMIGO = pygame.transform.scale(INIMIGO, (100, 100))
BALA = pygame.transform.scale(BALA, (20, 10))

# Controla os frames por segundo (FPS)
FPS = 60
clock = pygame.time.Clock()

# Classe do jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = GAUCHO
        self.rect = self.image.get_rect()
        self.rect.center = (100, ALTURA // 2)  # Começa no lado esquerdo da tela
        self.vida = 10  # Quantidade de vidas

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
        self.rect.x = LARGURA  # Começa fora da tela (direita)
        self.rect.y = random.randint(0, ALTURA - self.rect.height)  # Posição vertical aleatória

    def update(self):
        self.rect.x -= 5  # Move para a esquerda
        if self.rect.right < 0:
            self.kill()  # Remove se sair da tela

# Classe das balas
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

# Pontuação e fonte usada
pontos = 0
fonte = pygame.font.SysFont("arial", 28)

# Define um evento para gerar inimigos periodicamente
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1500)  # A cada 1,5 segundos

# Loop principal do jogo
rodando = True
while rodando:
    clock.tick(FPS)
    TELA.blit(FUNDO, (0, 0))  # Desenha o fundo

    # Captura as teclas pressionadas
    keys = pygame.key.get_pressed()
    
    # Lida com os eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False  # Fecha o jogo
        if evento.type == TIMER_EVENT:
            inimigos.add(Inimigo())  # Adiciona um novo inimigo
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                # Dispara uma bala
                bala = Bala(jogador.rect.right, jogador.rect.centery)
                balas.add(bala)
                if TIRO_SOM:
                    TIRO_SOM.play()

    # Atualiza todos os sprites
    jogador.update(keys)
    inimigos.update()
    balas.update()

    # Desenha os sprites na tela
    jogador_group.draw(TELA)
    inimigos.draw(TELA)
    balas.draw(TELA)

    # Verifica colisão entre balas e inimigos
    for bala in pygame.sprite.groupcollide(balas, inimigos, True, True):
        pontos += 10
        if IMPACTO_SOM:
            IMPACTO_SOM.play()

    # Verifica se algum inimigo atingiu o jogador
    if pygame.sprite.spritecollideany(jogador, inimigos):
        jogador.vida -= 1
        for inimigo in inimigos:
            inimigo.kill()
        if jogador.vida <= 0:
            rodando = False  # Encerra o jogo se perder todas as vidas

    # Exibe pontuação e vidas na tela
    texto = fonte.render(f"Pontos: {pontos}  Vida: {jogador.vida}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    pygame.display.flip()  # Atualiza a tela

# Finaliza o jogo
pygame.quit()
sys.exit()


#Francisco de Freitas Kemle
#RU: 5082822