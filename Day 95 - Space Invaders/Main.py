import pygame
import sys
import random
import math
import os

# Inicializar Pygame
pygame.init()

# Tentar inicializar mixer, mas continuar sem áudio se falhar
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except:
    AUDIO_ENABLED = False
    print("Áudio não disponível - jogo rodará sem som")

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (255, 0, 255)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 30
        self.speed = 5
        self.color = GREEN
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Carregar sprite se disponível
        self.sprite = None
        try:
            if os.path.exists('player-ship.png'):
                self.sprite = pygame.image.load('player-ship.png')
                self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
            else:
                print("Erro: Arquivo 'player-ship.png' não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar sprite do jogador: {e}")

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            # Detalhes da nave
            pygame.draw.rect(screen, WHITE, (self.x + 20, self.y + 5, 10, 5))
            pygame.draw.rect(screen, WHITE, (self.x + 15, self.y + 15, 20, 3))


class Bullet:
    def __init__(self, x, y, speed, damage=1, bullet_type='normal', angle=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.type = bullet_type
        self.angle = angle
        if bullet_type == 'laser':
            self.width = 4
            self.height = SCREEN_HEIGHT
            self.rect = pygame.Rect(x, 0, self.width, self.height)
            self.life = 10
        else:
            self.width = 4
            self.height = 10
            self.rect = pygame.Rect(x, y, self.width, self.height)
            self.life = 0

    def update(self):
        if self.type == 'laser':
            self.life -= 1
            return self.life > 0
        else:
            self.x += math.sin(self.angle) * self.speed
            self.y -= self.speed
            self.rect.x = self.x
            self.rect.y = self.y
            return self.y > -self.height

    def draw(self, screen):
        if self.type == 'laser':
            # Desenhar laser com efeito de brilho
            pygame.draw.rect(screen, CYAN, (self.x, 0, self.width + 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, WHITE, (self.x + 1, 0, self.width, SCREEN_HEIGHT))
        else:
            pygame.draw.rect(screen, GREEN, self.rect)


class EnemyBullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 8
        self.speed = speed
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        return self.y < SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)


class Enemy:
    def __init__(self, x, y, enemy_type='basic', level=1):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.direction = 1
        self.last_shot = pygame.time.get_ticks()
        self.type = enemy_type
        self.level = level

        # Configurações por tipo
        if enemy_type == 'basic':
            self.health = 1 + level // 2
            self.speed = 1 + level * 0.2
            self.color = RED
            self.value = 10
        elif enemy_type == 'fast':
            self.health = 1 + level // 2
            self.speed = 2 + level * 0.2
            self.color = ORANGE
            self.value = 15
        elif enemy_type == 'tank':
            self.health = 3 + level // 2
            self.speed = 0.5 + level * 0.1
            self.color = YELLOW
            self.value = 25
        elif enemy_type == 'shooter':
            self.health = 2 + level // 2
            self.speed = 1 + level * 0.2
            self.color = PURPLE
            self.value = 20
        elif enemy_type == 'boss':
            self.health = 20 + level * 2
            self.speed = 0.5
            self.color = RED
            self.value = 200
            self.width = 120
            self.height = 60
        else:
            raise ValueError(f"Tipo de inimigo desconhecido: {enemy_type}")

        self.max_health = self.health
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Carregar sprites se disponíveis
        self.sprite = None
        try:
            sprite_file = None
            if enemy_type == 'basic' and os.path.exists('enemy-basic.png'):
                sprite_file = 'enemy-basic.png'
            if enemy_type == 'tank' and os.path.exists('enemy-tank.png'):
                sprite_file = 'enemy-tank.png'
            elif enemy_type == 'fast' and os.path.exists('enemy-fast.png'):
                sprite_file = 'enemy-fast.png'
            elif enemy_type == 'shooter' and os.path.exists('shooter.png'):
                sprite_file = 'shooter.png'
            elif enemy_type == 'boss' and os.path.exists('boss.png'):
                sprite_file = 'boss.png'

            if sprite_file:
                self.sprite = pygame.image.load(sprite_file)
                self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
            else:
                print(f"Erro: Arquivo de sprite para {enemy_type} não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar sprite do inimigo {enemy_type}: {e}")

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x

    def move_down(self):
        self.y += 20
        self.direction *= -1
        self.rect.y = self.y

    def can_shoot(self, level):
        now = pygame.time.get_ticks()
        fire_rate = 2000 // level
        return now - self.last_shot > fire_rate and random.random() < 0.001 * level

    def shoot(self, level):
        self.last_shot = pygame.time.get_ticks()
        return EnemyBullet(self.x + self.width // 2 - 2, self.y + self.height, 3 + level * 0.5)

    def draw(self, screen):
        if self.sprite and self.type != 'boss':
            screen.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect)

            # Detalhes especiais por tipo
            if self.type == 'boss':
                pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 10, self.width - 20, self.height - 20))
                pygame.draw.rect(screen, self.color, (self.x + 20, self.y + 20, self.width - 40, self.height - 40))
            elif self.type == 'tank' and not self.sprite:
                pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, self.width - 10, 5))
            elif self.type == 'fast' and not self.sprite:
                pygame.draw.rect(screen, WHITE, (self.x + 15, self.y + 10, 10, 10))

        # Barra de vida
        if self.health < self.max_health:
            health_percent = self.health / self.max_health
            pygame.draw.rect(screen, RED, (self.x, self.y - 8, self.width, 4))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, self.width * health_percent, 4))


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * 8
        self.vy = (random.random() - 0.5) * 8
        self.life = 30
        self.max_life = 30
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        alpha = self.life / self.max_life
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.rect(screen, color, (int(self.x), int(self.y), 3, 3))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        # Estado do jogo
        self.state = 'start'  # start, playing, upgrade, game_over
        self.score = 0
        self.lives = 3
        self.level = 1
        self.money = 0

        # Objetos do jogo
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 60)
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []

        # Upgrades
        self.upgrades = {
            'damage': 1,
            'fire_rate': 1,
            'multishot': False,
            'laser': False
        }

        # Controles
        self.last_shot = 0
        self.shoot_cooldown = 300

        # Fonte
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Sons (apenas se áudio estiver disponível)
        self.sounds = {}
        if AUDIO_ENABLED:
            try:
                if os.path.exists('shoot.wav'):
                    self.sounds['shoot'] = pygame.mixer.Sound('shoot.wav')
                    self.sounds['shoot'].set_volume(0.3)
                if os.path.exists('explosion.wav'):
                    self.sounds['explosion'] = pygame.mixer.Sound('explosion.wav')
                    self.sounds['explosion'].set_volume(0.5)
                if os.path.exists('background-music.wav'):
                    self.sounds['background'] = pygame.mixer.Sound('background-music.wav')
                    self.sounds['background'].set_volume(0.2)
            except:
                print("Erro ao carregar sons")

        # Música de fundo
        self.music_playing = False

    def play_sound(self, sound_name):
        if AUDIO_ENABLED and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def start_background_music(self):
        if AUDIO_ENABLED and not self.music_playing and 'background' in self.sounds:
            try:
                pygame.mixer.Sound.play(self.sounds['background'], loops=-1)
                self.music_playing = True
            except:
                pass

    def spawn_enemies(self):
        self.enemies = []
        rows = 3 + self.level // 3
        cols = 8 + self.level // 2

        for row in range(rows):
            for col in range(cols):
                enemy_type = self.get_enemy_type(row, self.level)
                x = 50 + col * 80
                y = 50 + row * 60
                self.enemies.append(Enemy(x, y, enemy_type, self.level))

        # Boss a cada 5 níveis
        if self.level % 5 == 0:
            boss = Enemy(SCREEN_WIDTH // 2 - 60, 30, 'boss', self.level)
            self.enemies.append(boss)

    def get_enemy_type(self, row, level):
        types = ['basic', 'fast', 'tank', 'shooter']
        type_index = min(row + level // 2, len(types) - 1)
        return types[type_index]

    def shoot_player_bullet(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown // self.upgrades['fire_rate']:
            return

        self.last_shot = now
        self.play_sound('shoot')
        damage = self.upgrades['damage']

        # Atirar tiros normais ou multishot
        if self.upgrades['multishot']:
            for i in range(-2, 3):
                bullet = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y,
                                8, damage, 'normal', i * 0.2)
                self.player_bullets.append(bullet)
        else:
            bullet = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y,
                            8, damage, 'normal')
            self.player_bullets.append(bullet)

        # Adicionar laser se upgrade ativado
        if self.upgrades['laser']:
            laser = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y,
                           0, damage * 2, 'laser')
            self.player_bullets.append(laser)

    def create_explosion(self, x, y, color):
        for _ in range(8):
            self.particles.append(Particle(x, y, color))

    def update_game(self):
        keys = pygame.key.get_pressed()

        # Atualizar jogador
        self.player.update(keys)

        # Tiro do jogador
        if keys[pygame.K_SPACE]:
            self.shoot_player_bullet()

        # Atualizar balas
        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.update()]
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.update()]

        # Verificar se algum inimigo atingiu as bordas
        move_down = False
        for enemy in self.enemies:
            if enemy.x <= 0 or enemy.x >= SCREEN_WIDTH - enemy.width:
                move_down = True
                break

        # Controlar frequência de descida
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_move_down'):
            self.last_move_down = 0
        if move_down and current_time - self.last_move_down > 500:  # 500ms cooldown
            for enemy in self.enemies:
                if enemy.y + enemy.height < SCREEN_HEIGHT - 150:  # Limite de descida
                    enemy.move_down()
            self.last_move_down = current_time
        else:
            for enemy in self.enemies:
                enemy.update()

        # Inimigos atiram
        for enemy in self.enemies:
            if enemy.can_shoot(self.level):
                bullet = enemy.shoot(self.level)
                self.enemy_bullets.append(bullet)

        # Atualizar partículas
        self.particles = [particle for particle in self.particles if particle.update()]

        # Colisões
        self.check_collisions()

        # Verificar fim de nível
        if not self.enemies:
            self.level += 1
            self.state = 'upgrade'

    def check_collisions(self):
        # Balas do jogador vs inimigos
        for bullet in self.player_bullets[:]:
            hit_enemies = []
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= bullet.damage
                    self.create_explosion(bullet.x, enemy.y if bullet.type == 'laser' else bullet.y, YELLOW)
                    if enemy.health <= 0:
                        self.score += enemy.value * self.level
                        self.money += enemy.value // 2 * self.level
                        self.play_sound('explosion')
                        self.create_explosion(enemy.x + enemy.width // 2,
                                              enemy.y + enemy.height // 2, enemy.color)
                        self.enemies.remove(enemy)
                    if bullet.type != 'laser':
                        hit_enemies.append(bullet)
                    if bullet.type == 'laser':
                        # Continua para checar outros enemies
                        continue
                    else:
                        break  # Para non-laser, para após primeiro hit

            # Remove bullet se non-laser e hit
            if bullet in hit_enemies:
                self.player_bullets.remove(bullet)

        # Balas dos inimigos vs jogador
        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.lives -= 1
                self.play_sound('explosion')
                self.create_explosion(self.player.x + self.player.width // 2,
                                      self.player.y + self.player.height // 2, RED)
                self.enemy_bullets.remove(bullet)

                if self.lives <= 0:
                    self.state = 'game_over'

        # Inimigos vs jogador
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.state = 'game_over'
                break

    def draw_ui(self):
        # HUD
        score_text = self.small_font.render(f"Pontuação: {self.score}", True, GREEN)
        lives_text = self.small_font.render(f"Vidas: {self.lives}", True, GREEN)
        level_text = self.small_font.render(f"Fase: {self.level}", True, GREEN)
        money_text = self.small_font.render(f"Dinheiro: {self.money}", True, GREEN)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (200, 10))
        self.screen.blit(level_text, (350, 10))
        self.screen.blit(money_text, (500, 10))

    def draw_start_screen(self):
        title = self.font.render("SPACE INVADERS", True, GREEN)
        instruction1 = self.small_font.render("Use as setas para mover e ESPAÇO para atirar", True, WHITE)
        instruction2 = self.small_font.render("Pressione ENTER para upgrades entre as fases", True, WHITE)
        start_text = self.small_font.render("Pressione ESPAÇO para iniciar", True, GREEN)

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        inst1_rect = instruction1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        inst2_rect = instruction2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(instruction1, inst1_rect)
        self.screen.blit(instruction2, inst2_rect)
        self.screen.blit(start_text, start_rect)

    def draw_upgrade_screen(self):
        title = self.font.render("UPGRADES DE ARMAS", True, GREEN)
        money_text = self.small_font.render(f"Dinheiro: {self.money}", True, WHITE)

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        money_rect = money_text.get_rect(center=(SCREEN_WIDTH // 2, 150))

        self.screen.blit(title, title_rect)
        self.screen.blit(money_text, money_rect)

        # Opções de upgrade
        upgrades_info = [
            ("1 - Aumentar Dano", f"Custo: {100 * self.upgrades['damage']}", 200),
            ("2 - Velocidade de Tiro", f"Custo: {150 * self.upgrades['fire_rate']}", 250),
            ("3 - Tiro Múltiplo", f"Custo: 300 {'(Comprado)' if self.upgrades['multishot'] else ''}", 300),
            ("4 - Laser Contínuo", f"Custo: 500 {'(Comprado)' if self.upgrades['laser'] else ''}", 350),
            ("ESPAÇO - Continuar Jogo", "", 450)
        ]

        for upgrade, cost, y in upgrades_info:
            upgrade_text = self.small_font.render(upgrade, True, WHITE)
            cost_text = self.small_font.render(cost, True, YELLOW)

            upgrade_rect = upgrade_text.get_rect(center=(SCREEN_WIDTH // 2 - 100, y))
            cost_rect = cost_text.get_rect(center=(SCREEN_WIDTH // 2 + 100, y))

            self.screen.blit(upgrade_text, upgrade_rect)
            if cost:
                self.screen.blit(cost_text, cost_rect)

    def draw_game_over_screen(self):
        game_over = self.font.render("GAME OVER", True, RED)
        final_score = self.small_font.render(f"Pontuação Final: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Pressione R para jogar novamente", True, GREEN)

        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        self.screen.blit(game_over, game_over_rect)
        self.screen.blit(final_score, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def handle_upgrade_input(self, key):
        if key == pygame.K_1:  # Aumentar dano
            cost = 100 * self.upgrades['damage']
            if self.money >= cost:
                self.money -= cost
                self.upgrades['damage'] += 1
        elif key == pygame.K_2:  # Velocidade de tiro
            cost = 150 * self.upgrades['fire_rate']
            if self.money >= cost:
                self.money -= cost
                self.upgrades['fire_rate'] += 1
        elif key == pygame.K_3:  # Tiro múltiplo
            if not self.upgrades['multishot'] and self.money >= 300:
                self.money -= 300
                self.upgrades['multishot'] = True
        elif key == pygame.K_4:  # Laser
            if not self.upgrades['laser'] and self.money >= 500:
                self.money -= 500
                self.upgrades['laser'] = True
        elif key == pygame.K_SPACE:  # Continuar
            self.state = 'playing'
            self.spawn_enemies()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.money = 0
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 60)
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.upgrades = {
            'damage': 1,
            'fire_rate': 1,
            'multishot': False,
            'laser': False
        }

    def draw_stars(self):
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 73 + pygame.time.get_ticks() * 0.01) % SCREEN_HEIGHT
            pygame.draw.rect(self.screen, WHITE, (x, y, 1, 1))

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == 'start':
                        if event.key == pygame.K_SPACE:
                            self.state = 'playing'
                            self.spawn_enemies()
                            self.start_background_music()
                    elif self.state == 'upgrade':
                        self.handle_upgrade_input(event.key)
                    elif self.state == 'playing':
                        if event.key == pygame.K_RETURN:
                            self.state = 'upgrade'
                    elif self.state == 'game_over':
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.state = 'start'

            # Atualizar
            if self.state == 'playing':
                self.update_game()

            # Desenhar
            self.screen.fill(BLACK)
            self.draw_stars()

            if self.state == 'start':
                self.draw_start_screen()
            elif self.state == 'upgrade':
                self.draw_upgrade_screen()
            elif self.state == 'game_over':
                self.draw_game_over_screen()
            elif self.state == 'playing':
                # Desenhar objetos do jogo
                self.player.draw(self.screen)

                for bullet in self.player_bullets:
                    bullet.draw(self.screen)

                for bullet in self.enemy_bullets:
                    bullet.draw(self.screen)

                for enemy in self.enemies:
                    enemy.draw(self.screen)

                for particle in self.particles:
                    particle.draw(self.screen)

                self.draw_ui()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
