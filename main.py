# import pygame
# from mysql.connector import connect

# # Initialisation de Pygame
# pygame.init()

# # Connexion à la base de données MySQL
# mydb = connect(
#     host="localhost",
#     port=8889,
#     user="root",
#     password="root",
#     database="sokoban_db"
# )


# # # Création de la table pour stocker les résultats
# # mycursor = mydb.cursor()
# # mycursor.execute(
# #     "CREATE TABLE results (id INT AUTO_INCREMENT PRIMARY KEY, player_name VARCHAR(255), score INT, date_time DATETIME)")

# # # Définition de la taille de la fenêtre
# win_width = 800
# win_height = 600
# win = pygame.display.set_mode((win_width, win_height))

# # # Chargement des images
# player_img = pygame.image.load('images/player.png')
# wall_img = pygame.image.load('images/wall.png')
# box_img = pygame.image.load('images/box.png')

# # # Ajout de la logique pour suivre le score et la durée de la partie
# score = 0
# start_time = pygame.time.get_ticks()

# # # Boucle principale du jeu
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Ajout de la logique pour déplacer le joueur et les caisses
#     # ...

#     # Ajout de la logique pour vérifier si le joueur a gagné ou perdu
#     if game_won:
#         # end_time = pygame.time.get_ticks()
#         # duration = (end_time - start_time) / 1000
#         player_name = "John Doe"  # Remplacez par le nom du joueur
#         # sql = "INSERT INTO results (player_name, score, date_time) VALUES (%s, %s, %s)"
#         # val = (player_name, score, datetime.datetime.now())
#         # mycursor.execute(sql, val)
#         # mydb.commit()
#         running = False

# pygame.quit()

import pygame
from mysql.connector import connect

# Connexion à la base de données MySQL
mydb = connect(
    host="localhost",
    port=8889,
    user="root",
    password="root",
    database="sokoban_db"
)

# Création de la table pour stocker les résultats et verifier si la table existe deja

mycursor = mydb.cursor()
mycursor.execute("Show tables;")

tables = mycursor.fetchall()

if ("results",) not in tables:
    print("Table does not exist -> so create it")
    mycursor.execute(
        "CREATE TABLE results (id INT AUTO_INCREMENT PRIMARY KEY, player_name VARCHAR(255), score INT, date_time DATETIME)")
else:
    print("Table already exists")

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
WINDOW_WIDTH = 970
WINDOW_HEIGHT = 1000

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Chargement des images
player_img = pygame.image.load('images/player.png')
box_img = pygame.image.load('images/box.png')
box_completed_img = pygame.image.load('images/box-complete.png')
target_img = pygame.image.load('images/target.png')
wall_img = pygame.image.load('images/wall.png')


move_stack = []


def addMoveToStack(move):
    move_stack.append(move)


def undoMove():
    if len(move_stack) > 0:
        # Récupération du dernier mouvement effectué
        last_move = move_stack.pop()

        # Annulation du mouvement
        # code ici pour annuler le mouvement

    else:
        # La pile est vide, il n'y a aucun mouvement à défaire
        print("Aucun mouvement à défaire")


# Définition de la classe Box

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.image = box_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Définition de la classe Player


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def move(self, dx, dy):

        new_rect = self.rect.move(dx, dy)

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return

        for box in boxes:
            if new_rect.colliderect(box.rect):
                return

        self.rect = new_rect

    def move_box(self, dx, dy, boxes, walls):
        # ""Move a box if there is one in front of the player"""
        box_hit = None
        for box in boxes:
            if self.rect.move(dx, dy).colliderect(box.rect):
                box_hit = box
                break
        if box_hit:
            # Check if the box can be moved
            new_rect = box_hit.rect.move(dx, dy)
            if not any(wall.rect.colliderect(new_rect) or
                       box.rect.colliderect(new_rect) for wall in walls
                       for box in boxes if box is not box_hit):
                # Move the box and the player
                box_hit.rect.move_ip(dx, dy)
                self.move(dx, dy)


# Définition de la classe Wall


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = wall_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Définition de la classe Target


class Target(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = target_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Création de la grille de jeu
level = [
    "111111111111",
    "1 @        1",
    "1    2     1",
    "1  .       1",
    "1     .    1",
    "1          1",
    "1  2    2  1",
    "1       .  1",
    "111111111111"
]

# Initialisation des groupes de sprites
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
targets = pygame.sprite.Group()

# Parcours de la grille de jeu pour créer les sprites
for row in range(len(level)):
    for col in range(len(level[row])):
        x = col * 80
        y = row * 80
        if level[row][col] == '1':
            wall = Wall(x, y)
            all_sprites.add(wall)
            walls.add(wall)
        elif level[row][col] == '.':
            target = Target(x, y)
            all_sprites.add(target)
            targets.add(target)
        elif level[row][col] == '@':
            player = Player(x, y)
            all_sprites.add(player)
        elif level[row][col] == '2':
            box = Box(x, y)
            all_sprites.add(box)
            boxes.add(box)

# Définition de la fenêtre
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sokoban")


def reset_level():
    for row in range(len(level)):
        for col in range(len(level[row])):
            x = col * 80
            y = row * 80
            if level[row][col] == '@':
                player.rect.x = x
                player.rect.y = y
            elif level[row][col] == '2':
                for box in boxes:
                    if box.start_x == x and box.start_y == y:
                        box.rect.x = x
                        box.rect.y = y


# Définition de l'écran de démarrage
start_screen = pygame.image.load('images/press-start.png')


# Affichage de l'écran de démarrage


font = pygame.font.SysFont(None, 45)
clock = pygame.time.Clock()
input_box = pygame.Rect(100, 100, 140, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
done = False

# Attente de l'entrée de l'utilisateur pour commencer le jeu
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = True
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if input_box.collidepoint(event.pos):
                # Toggle the active variable.
                active = not active
            else:
                active = False
            # Change the current color of the input box.
            color = color_active if active else color_inactive
        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    print(text)
                    # text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                    print("supprimer", text)
                else:
                    text += event.unicode
                    print("ajout ", text)

        labelInput = font.render('Pseudo : ', True, pygame.Color('pink'))
        window.blit(labelInput, (10, 100))
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width + 100
        # Blit the text.
        window.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(window, color, input_box, 2)

        window.blit(start_screen, (0, 0))
        pygame.display.flip()
        clock.tick(60)

# pygame.display.flip()
# print(pygame.font.get_fonts())

# Boucle principale du jeu
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.move(0, -80)
                player.move_box(0, -80, boxes, walls)
            elif event.key == pygame.K_DOWN:
                player.move(0, 80)
                player.move_box(0, 80, boxes, walls)
            elif event.key == pygame.K_LEFT:
                player.move(-80, 0)
                player.move_box(-80, 0, boxes, walls)
            elif event.key == pygame.K_RIGHT:
                player.move(80, 0)
                player.move_box(80, 0, boxes, walls)
            elif event.key == pygame.K_BACKSPACE:
                undoMove()
            elif event.key == pygame.K_SPACE:
                reset_level()

    # Vérification si une boîte est sur une cible
    scoreBox = 0
    for box in boxes:
        targets_hit = pygame.sprite.spritecollide(box, targets, False)

        if targets_hit:
            scoreBox += 1
            box.image = pygame.Surface((80, 80))
            box.image = box_completed_img
        else:
            box.image = box_img

    if scoreBox == len(boxes):
        print("win")
        reset_level()

    # Affichage des sprites
    window.fill(BLACK)
    police = pygame.font.SysFont('futura', 25)
    text = police.render('Score : '+str(scoreBox), True, pygame.Color('pink'))
    window.blit(text, (10, 899))
    all_sprites.draw(window)

    # Actualisation de l'affichage
    pygame.display.flip()

# Fermeture de Pygame
pygame.quit()
