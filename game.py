
import pygame as pg
import Constantes as const
import map as map
import player as player


class Game():
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.end_game = False                   #Drapeau pour la fin du jeu
        self.keys = pg.key.get_pressed()        #Contiendra l'état de toutes les touches du clavier (enfoncées ou non)
        self.clock = pg.time.Clock()            #Pour réglage des FPS
        self.screen = pg.display.get_surface()  #Création de la fenêtre du jeu
        self.map_coord_x = 0
        self.map_coord_y = 150

       #Création d'un joueur en lui passant l'instance de l'objet game
        self.player = player.Player(self)

       #Création d'un objet map en lui passant l'instance de l'objet game + coord en x et y
        self.map = map.Map(self, self.map_coord_x, self.map_coord_y)

    def start_game(self):
        pg.time.Clock()  #Pour réglage nbre images/sec
        self.update_game()

    def update_game(self):
        while not self.end_game:

           #Remet l'écran en noir
            pg.draw.rect(self.screen, (0, 0, 0), (0, 0, const.resolution[0], const.resolution[1]))

           #1) Gestion des évènements
            self.update_evenements()

           #2) Affichage du joueur
            self.player.update_player()

           #3) Affichage de la map et de la carte 2d
            self.map.draw_map()

           #4) MAJ de l'image
            pg.display.update()

           #Fin) Ajustement des FPS
            self.clock.tick(const.fps)
            fps = f"Nombre de fps: {int(self.clock.get_fps())}"
            pg.display.set_caption(fps)


    #-----------------------------------------------------------------
    #Enregistre les évènements du clavier dans la variables self.keys|
    # -----------------------------------------------------------------
    def update_evenements(self):
        for event in pg.event.get():

            if event.type == pg.QUIT:
                self.end_game = True

            elif event.type in (pg.KEYDOWN, pg.KEYUP):

                self.keys = pg.key.get_pressed() #Actualise la liste des touches enfoncées/relachées

                if self.keys[pg.K_ESCAPE]:
                    self.end_game = True

                if self.keys[pg.K_p]:            #La touche p permet d'activer/désactiver l'affichage en 2d

                    if self.map.flag_map_2d == True:
                        self.map.flag_map_2d = False

                    else:
                        self.map.flag_map_2d = True

                if self.keys[pg.K_t]:
                    if self.map.flag_texturer == True:
                        self.map.flag_texturer = False

                    else:
                        self.map.flag_texturer = True