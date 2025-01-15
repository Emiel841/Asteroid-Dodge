import pygame
import random
from os.path import join
import asyncio

async def main():

    pygame.init()

    WIDTH, HEIGHT = 1280, 720

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dodge game")

    class Player(pygame.sprite.Sprite):
        def __init__(self, groups):
            super().__init__(groups)
            self.image = pygame.image.load("images/player.png").convert_alpha()
            self.rect = self.image.get_frect()
            self.rect.center = (640, 360)
            self.direction = pygame.math.Vector2()
            self.speed = 400

            self.can_shoot = True
            self.shoot_time = 0
            self.cooldown_duration = 400

            self.original_img = self.image
            self.roteate_l_img = pygame.transform.rotate(self.image, -15)
            self.rotate_r_img = pygame.transform.rotate(self.image, 15)

        def shoot_timer(self):
            if not self.can_shoot:
                now = pygame.time.get_ticks()
                if now - self.shoot_time >= self.cooldown_duration:
                    self.can_shoot = True



        def update(self, delta_time):
            keys = pygame.key.get_pressed()
            self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            player_direction = self.direction.normalize() if self.direction else self.direction
            player.rect.center += player_direction * self.speed * delta_time

            if self.direction.x > 0:
                self.image = self.roteate_l_img
                self.rect = self.image.get_frect(center = self.rect.center)
            elif self.direction.x < 0:
                self.image = self.rotate_r_img
                self.rect = self.image.get_frect(center = self.rect.center)
            else: self.image = self.original_img

            recent_keys = pygame.key.get_just_pressed()
            if recent_keys[pygame.K_SPACE] and self.can_shoot:
                Projectile(laser_img, self.rect.midtop, (all_sprites, projectile_sprites))
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

            self.shoot_timer()

    class Star(pygame.sprite.Sprite):
        def __init__(self, groups, surface):
            super().__init__(groups)
            self.image = surface
            self.rect = self.image.get_frect()
            self.rect.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

    class Projectile(pygame.sprite.Sprite):
        def __init__(self, surf, pos, groups):
            super().__init__(groups)
            self.image = surf
            self.rect = self.image.get_frect(midbottom = pos)

        def update(self, dt):
            self.rect.centery -= 400 * dt
            if self.rect.bottom < 0:
                self.kill()

    class Meteor(pygame.sprite.Sprite):
        def __init__(self, surf, pos, groups):
            super().__init__(groups)
            self.image = surf
            self.rect = self.image.get_frect(center = pos)
            self.direction = pygame.Vector2(random.uniform(-0.5, 0.5), 1)
            self.speed = random.randint(400, 500)

            self.rotation_speed = random.randint(20, 120)
            self.original_surface = self.image
            self.rotation = 0



        def update(self, dt):
            self.rect.center += self.direction * self.speed * dt
            self.rotation += self.rotation_speed * dt
            self.image = pygame.transform.rotate(self.original_surface, self.rotation)
            self.rect = self.image.get_frect(center=self.rect.center)
            if self.rect.top >= 720:
                self.kill()

    meteor_img = pygame.image.load("images/meteor.png").convert_alpha()
    laser_img = pygame.image.load("images/laser.png").convert_alpha()
    star_surface = pygame.image.load("images/star.png").convert_alpha()

    explosion_frames = [pygame.image.load(join("images", "explosion", str(i)+".png")).convert_alpha() for i in range(21)]

    class AnimateExplosion(pygame.sprite.Sprite):
        def __init__(self, frames, pos, groups):
            self.frames = frames
            self.frame_index = 0
            super().__init__(groups)
            self.image = frames[0]
            self.rect = self.image.get_frect(center = pos)

        def update(self, dt):
            self.frame_index += 30 * dt
            if self.frame_index < len(self.frames):
                self.image = self.frames[int(self.frame_index)]
            else:
                self.kill()

    font = pygame.font.Font("images/Oxanium-Bold.ttf", 40)

    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    projectile_sprites = pygame.sprite.Group()

    for i in range(20):
        Star(all_sprites, star_surface)
    player = Player(all_sprites)

    meteor_spawn_time = 200
    meteor_event = pygame.event.custom_type()
    pygame.time.set_timer(meteor_event, meteor_spawn_time)

    running = True
    clock = pygame.time.Clock()

    def collision():

        if pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask): return False

        for projectile in projectile_sprites:
            if pygame.sprite.spritecollide(projectile, meteor_sprites, True):
                projectile.kill()
                AnimateExplosion(explosion_frames, projectile.rect.midtop, all_sprites)

        return True
    def display_score():
        current_time = pygame.time.get_ticks() // 10
        points_surfce = font.render(str(current_time), True, (240, 240, 240))
        text_rect = points_surfce.get_frect(midbottom = (WIDTH/2, HEIGHT-50))
        screen.blit(points_surfce, text_rect)

    while running:
        delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x, y = random.randint(0, WIDTH), random.randint(-200, -100)
                Meteor(meteor_img, (x, y), (all_sprites, meteor_sprites))

        all_sprites.update(delta_time)
        running = collision()
        screen.fill('#3a2e3f')
        all_sprites.draw(screen)
        display_score()
        pygame.display.update()
        await asyncio.sleep(0)




    pygame.quit()


asyncio.run( main() )
