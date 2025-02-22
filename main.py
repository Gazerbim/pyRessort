import pygame
from pygame.locals import *
import math

pygame.init()
dims = (720, 1080)
fenetre = pygame.display.set_mode(dims)
GRAVITE = 0.2
FROTTEMENT_AIR = 0.95  # Coefficient de frottement
LIM_APPROX = 0  # 0 pour désactiver l'approximation, sinon mettre une valeur
dragging = None
mouse_positions = []  # Liste pour stocker les positions de la souris
COR = 0.8  # Coef de restitution
REPOUSSEMENT = 0.1

def detecter_clic(x, y):
    for balle in balles:
        if math.sqrt((balle.x - x) ** 2 + (balle.y - y) ** 2) <= balle.rayon:
            return balle
    return None


class Boule:
    def __init__(self, x, y, rayon, masse, couleur=(255, 0, 0)):
        self.x = x
        self.y = y
        self.vx = 10
        self.vy = 0
        self.rayon = rayon
        self.masse = masse
        self.partenaires = []
        self.attrapee = False
        self.couleur = couleur

    def relier(self, boule, k, l0):
        if boule not in self.partenaires:
            self.partenaires.append((boule, k, l0))
            boule.partenaires.append((self, k, l0))

    def appliquerForceRessort(self):
        if not self.attrapee:
            for partenaire in self.partenaires:
                dist = self.calculerDist(partenaire[0])
                angle = self.calculerAngle(partenaire[0])
                f = partenaire[1] * (dist - partenaire[2])
                ax = (f * math.cos(angle)) / self.masse
                ay = (f * math.sin(angle)) / self.masse
                self.vx += ax
                self.vy += ay

    def calculerAngle(self, boule):
        return math.atan2(boule.y - self.y, boule.x - self.x)

    def calculerDist(self, boule):
        return math.sqrt((boule.y - self.y) ** 2 + (boule.x - self.x) ** 2)

    def appliquerGravite(self):
        if not self.attrapee:
            self.vy += GRAVITE

    def appliquerFrottement(self):
        if not self.attrapee:
            facteur_frottement = FROTTEMENT_AIR ** (1 / self.masse)
            self.vx *= facteur_frottement
            self.vy *= facteur_frottement

    def checkCollisions(self):
        if self.x >= dims[0] - self.rayon:
            self.x = dims[0] - self.rayon
            self.vx = -self.vx * COR
        if self.x <= self.rayon:
            self.x = self.rayon
            self.vx = -self.vx * COR
        if self.y >= dims[1] - self.rayon:
            self.y = dims[1] - self.rayon
            self.vy = -self.vy * COR
        if self.y <= self.rayon:
            self.y = self.rayon
            self.vy = -self.vy * COR

    def deplacement(self):
        if not self.attrapee:
            self.x += self.vx
            self.y += self.vy

    def approximer(self):
        if abs(self.vx) < LIM_APPROX:
            self.vx = 0
        if abs(self.vy) < LIM_APPROX:
            self.vy = 0

    def gererCollisionsEntreBoules(self):
        COR_BOULES = 0.9  # Coefficient de restitution pour les collisions entre boules

        for autre in balles:
            if autre is not self:
                dist = self.calculerDist(autre)
                min_dist = self.rayon + autre.rayon

                if dist < min_dist:
                    angle = self.calculerAngle(autre)
                    overlap = min_dist - dist

                    # Correction du chevauchement
                    self.x -= overlap / 2 * math.cos(angle) + REPOUSSEMENT * math.cos(angle)
                    self.y -= overlap / 2 * math.sin(angle) + REPOUSSEMENT * math.sin(angle)
                    autre.x += overlap / 2 * math.cos(angle) - REPOUSSEMENT * math.cos(angle)
                    autre.y += overlap / 2 * math.sin(angle) - REPOUSSEMENT * math.sin(angle)

                    # Composantes des vitesses dans le repère de la collision
                    v1x = self.vx * math.cos(angle) + self.vy * math.sin(angle)
                    v1y = -self.vx * math.sin(angle) + self.vy * math.cos(angle)
                    v2x = autre.vx * math.cos(angle) + autre.vy * math.sin(angle)
                    v2y = -autre.vx * math.sin(angle) + autre.vy * math.cos(angle)

                    # Collision élastique avec frottement
                    m1, m2 = self.masse, autre.masse
                    v1x_new = ((v1x * (m1 - m2) + 2 * m2 * v2x) / (m1 + m2)) * COR_BOULES
                    v2x_new = ((v2x * (m2 - m1) + 2 * m1 * v1x) / (m1 + m2)) * COR_BOULES

                    # Retour au repère original
                    self.vx = v1x_new * math.cos(angle) - v1y * math.sin(angle)
                    self.vy = v1x_new * math.sin(angle) + v1y * math.cos(angle)
                    autre.vx = v2x_new * math.cos(angle) - v2y * math.sin(angle)
                    autre.vy = v2x_new * math.sin(angle) + v2y * math.cos(angle)

    def update(self, pause):
        if not pause:
            self.appliquerForceRessort()
            self.appliquerGravite()
            self.appliquerFrottement()
            self.checkCollisions()
            self.gererCollisionsEntreBoules()
            self.approximer()
            self.deplacement()

    def afficher(self, surface):
        for partenaire in self.partenaires:
            pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)),
                             (int(partenaire[0].x), int(partenaire[0].y)), 2)
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.rayon)


balle1 = Boule(320, 240, 15, 10, (255, 0, 255))
balle2 = Boule(350, 240, 15, 10, (0, 255, 255))
balle4 = Boule(350, 240, 15, 10, (255, 255, 0))
balle5 = Boule(350, 240, 15, 10, (255, 0, 0))
balle3 = Boule(380, 240, 40, 20, (255, 255, 255))
balle6 = Boule(380, 240, 40, 20, (255, 255, 255))
balle7 = Boule(380, 240, 100, 100, (128, 128, 128))

balle1.relier(balle2, 0.05, 500)
balle1.relier(balle4, 0.05, 500)
balle1.relier(balle5, 0.01, 500)
balle2.relier(balle5, 0.01, 500)
balle4.relier(balle5, 0.01, 500)
balle4.relier(balle2, 0.01, 500)

#balle7.relier(balle5, 0.1, 1000)

balle3.relier(balle6, 0.03, 100)

balles = [balle1, balle2, balle3, balle5, balle4, balle6, balle7]

pause = False
continuer = True
clock = pygame.time.Clock()
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        elif event.type == MOUSEBUTTONDOWN:
            dragging = detecter_clic(*event.pos)
            if dragging:
                dragging.attrapee = True
                mouse_positions.clear()
                mouse_positions.append(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if dragging and len(mouse_positions) > 1:
                dragging.attrapee = False
                # Utiliser la dernière et l'avant-dernière position pour calculer la vitesse
                dx = mouse_positions[-1][0] - mouse_positions[-2][0]
                dy = mouse_positions[-1][1] - mouse_positions[-2][1]
                dragging.vx = dx
                dragging.vy = dy
            dragging = None
            mouse_positions.clear()
        elif event.type == MOUSEMOTION and dragging:
                mouse_positions.append(event.pos)
                dragging.x, dragging.y = event.pos

    dicKeys = pygame.key.get_pressed()
    pause = dicKeys[K_SPACE]

    fenetre.fill((0, 0, 0))
    for balle in balles:
        balle.update(pause)
        balle.afficher(fenetre)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
