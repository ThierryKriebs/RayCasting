
import pygame as pg
import levels as lev
import math
import constantes as const

#Objet chargé de dessiner le monde (incluant la boussole et la carte)
#Selon les options, dessine le monde en 2D ou en 3D raycasting
class Map():
    def __init__(self, game, coord_x, coord_y):
        self.level_courant = ""
        self.taille_case = const.taille_case  #Taille de case en x et y et Z
        self.map_coord_x = coord_x            #Début de la Map en X
        self.map_coord_y = coord_y            #Début de la Map en Y (en-dessous des infos du jeu radar...)

        self.flag_map_2d = False              #Par défaut on dessine la MAP en 3d

        self.game = game

        self.couleur_mur = (128, 128, 255)
        self.couleur_sol = (0, 128, 128)
        self.flag_texturer = True             #Indique si on doit texturer le niveau
        self.texture_mur1 = pg.image.load(const.texture_mur1).convert()
        self.dimensions_texture = self.texture_mur1.get_size()
       
        #Boussole:
        self.bouss_pos = (100, 75)
        self.bouss_color_ext1 = (128, 128, 128)
        self.bouss_rayon_ext1 = 60
        self.bouss_epaisseur_ext1 = 5

        self.bouss_color_ext2 = (50, 50, 50)
        self.bouss_rayon_ext2 = 63
        self.bouss_epaisseur_ext2 = 3

        #Pour la mini-carte-2d:
        self.coord_x_mini_carte = 400
        self.echelle_mini_carte = 0
        self.taille_mini_carte_pixel = (200, self.map_coord_y)

        self.nbre_max_case_x = 0  #Nbre max de case en x
        self.nbre_max_case_y = 0

        self.nbre_max_pixel_x = 0 #Nbre max de pixel x
        self.nbre_max_pixel_y = 0

        #Messages:
        self.mess_pos_x = 50
        self.taille_police = 20
        self.espace_vertical = 5
        self.nbre_ligne_max = self.map_coord_y / (self.taille_police + self.espace_vertical)    #150/15 => 10 lignes
        self.myfont = pg.font.SysFont('Comic Sans MS', self.taille_police)                      #Init de la police et de la taille
        self.couleur_mess = (125, 0, 0)     #Couleur des messages

        pg.font.init()                      #Initialisation de l'espace de message

        #Pour affichage 3d:
        self.centre_vertical_ecran =  const.reso_y_jeu / 2
        self.centre_horizontal_ecran = const.resolution[0] / 2
        self.demi_angle_player = self.game.player.angle_vue/2
        self.dce = self.centre_horizontal_ecran / math.tan(self.demi_angle_player * math.pi / 180)  #Distance Caméra Ecran
        self.dce_diag = self.dce / math.cos(self.demi_angle_player * math.pi / 180)

        self.angle_droit_rad = 90 * math.pi / 180
        self.angle_droit_en_rad = self.game.player.conv_degre_en_rad(90)

        #Récupération de la map courante
        self.lire_map()

    #Lit la map + calcul de l'échelle
    def lire_map(self):
        self.level_courant= lev.level1
    
        #----------------------------------------
        #1) Calcul de l'échelle de la mini-carte|
        #----------------------------------------
        #1-1) Nbre_max de case en x et y
        self.nbre_max_case_y = 0
        self.nbre_max_case_x = 0

        for l_cour in self.level_courant:
            nbre_case_cour_x = len(l_cour)

            if nbre_case_cour_x > self.nbre_max_case_x:
                self.nbre_max_case_x = nbre_case_cour_x

            self.nbre_max_case_y += 1

        # 1-2)Nbre_max de pixels en x et y
        self.nbre_max_pixel_x = self.nbre_max_case_x * self.taille_case[0]
        self.nbre_max_pixel_y = self.nbre_max_case_y * self.taille_case[1]

        # 1-3)Calcul échelle
        ech_temp_x = self.taille_mini_carte_pixel[0] / self.nbre_max_pixel_x
        ech_temp_y = self.taille_mini_carte_pixel[1] / self.nbre_max_pixel_y

        if ech_temp_x < ech_temp_y:
            self.echelle_mini_carte = ech_temp_x
        else:
            self.echelle_mini_carte = ech_temp_y


    #------------------------------------------------
    #Dessine la map à l'écran:
    #En 2D si la touche P est activée. Sinon en 3D
    #Dessine ensuite la carte
    # -----------------------------------------------
    def draw_map(self):

        if self.flag_map_2d == True:
            self.draw_2d_map()

        else:
            self.draw_3d_map()

        #Affichage de la boussole
        self.draw_boussole()

        #Affichage de la mini carte
        self.draw_mini_carte()


    def draw_2d_map(self):
        coord_x = self.map_coord_x
        coord_y = self.map_coord_y

        for l_cour in self.level_courant:

            for col in l_cour:
                if col == '1':
                    #On dessine un mur
                    pg.draw.rect(self.game.screen, self.couleur_mur,
                                 (coord_x, coord_y, self.taille_case[0], self.taille_case[1]))

                else:
                    #On dessine le sol
                    pg.draw.rect(self.game.screen, self.couleur_sol,
                                 (coord_x, coord_y, self.taille_case[0], self.taille_case[1]))

                coord_x += self.taille_case[0]

            coord_y += self.taille_case[1]
            coord_x = 0

        # 2) Dessine le joueur
        rayon = self.taille_case[0]/2
        player_x_pixel = self.game.player.coord_x_pixel
        player_y_pixel = self.game.player.coord_y_pixel 

        player_x_pixel += self.map_coord_x
        player_y_pixel += self.map_coord_y

        pg.draw.circle(self.game.screen, (255, 0, 0), (player_x_pixel, player_y_pixel), rayon)

        # 3) Dessine les rayons (cone de vision d joueur)
        for i in range(0, len(self.game.player.l_rayons)):
            angle_courant = self.game.player.l_rayons[i]

            x = angle_courant["dist_x"]  + self.map_coord_x
            y = angle_courant["dist_y"]  + self.map_coord_y
            pg.draw.line(self.game.screen, (0, 255, 0), (player_x_pixel, player_y_pixel), (x, y))


    #Déssiné la map en 3 dimension
    def draw_3d_map(self):
        '''
              self.rayon_info = {                                    #exemple dictionnaire stockant les informations du rayon courant
                  "angle" : 0,
                  "angle_rad": 0,
                  "mur_coord_x" : 0,
                  "mur_coord_y": 0,
                  "dist_x" : 0,
                  "dist_y" : 0,
                  "diag" : 0
              }

        '''
        #plafond
        pg.draw.rect(self.game.screen, (45, 48, 255), (const.coord_surface_jeu[0], const.coord_surface_jeu[1],
                                                const.resolution[0], (const.resolution[1] - const.coord_surface_jeu[1]) / 2  ))
        #sol
        pg.draw.rect(self.game.screen, (170, 80, 30), (const.coord_surface_jeu[0],
                                                        const.coord_surface_jeu[1] + (const.resolution[1] - const.coord_surface_jeu[1]) / 2,
                                                         const.resolution[0], const.resolution[1] ))

        #Affiche les murs en fonction des diagonales (vision du joueur):
        for res in range (0, const.resolution[0]):
            rayon_courant = self.game.player.l_rayons[res]
            cos_rayon_courant = math.cos(rayon_courant["angle_rad"])
            d_corrige = rayon_courant["diag"] * cos_rayon_courant #anti fisch eye

            dce_diag = self.dce_diag * self.taille_case[2]
            Hme = dce_diag / d_corrige

            Hme *= cos_rayon_courant

            if Hme > const.resolution[1] - const.coord_surface_jeu[1]:
                Hme_final = const.resolution[1] - const.coord_surface_jeu[1]
            else:
                Hme_final = Hme

            coord_y = const.coord_surface_jeu[1] + self.centre_vertical_ecran  - (Hme_final / 2)  #milieu écran - moitié du mur

            #Affiche les murs sans texture
            if self.flag_texturer == False:
                pg.draw.rect(self.game.screen, self.couleur_mur,(res, coord_y, 1, Hme_final))     #mur carré!!

            #On texture:
            else:
                #Murs
                self.dimensions_texture = self.texture_mur1.get_size()
                coordx_a_texturer = rayon_courant["case_exacte_x"] - rayon_courant["mur_coord_x"] #ex: 2.6 - 2
                coordy_a_texturer = rayon_courant["case_exacte_y"] - rayon_courant["mur_coord_y"]

                if coordx_a_texturer > 0:  #Sélectionne la partie qui varie
                    debut_texture_x = round(coordx_a_texturer, 3) * self.dimensions_texture[0]
                elif coordy_a_texturer > 0:
                    debut_texture_x = round(coordy_a_texturer, 3) * self.dimensions_texture[0]
                else:
                    debut_texture_x = round(abs(coordx_a_texturer), 3) * self.dimensions_texture[0]

                if debut_texture_x >= self.dimensions_texture[0]:
                    debut_texture_x %= self.dimensions_texture[0]
                largeur_texture = 1

                #1) récupérer une partie de l'image (1 pixel de large)
                if Hme <= self.dimensions_texture[1]:
                    hauteur_texture = self.dimensions_texture[1]
                    debut_img_y = 0

                else:  #Si mur > a hauteur de l'image => zoom sur  l'image!!!
                    depassement = math.floor(Hme - self.dimensions_texture[1])
                    if depassement > self.dimensions_texture[1] / 2:
                        depassement = math.floor(self.dimensions_texture[1] / 3)

                    debut_img_y = depassement / 2
                    hauteur_texture = self.dimensions_texture[1] - depassement

                texture = pg.Surface.subsurface(self.texture_mur1, (debut_texture_x, debut_img_y, largeur_texture, hauteur_texture))

                #2) Redimentionner à la taille du mur
                texture_transformée = pg.transform.scale(texture, (largeur_texture, int(Hme_final)))

                #3) Affichage
                self.game.fenetre.blit(texture_transformée, (res, coord_y))
               

    def draw_boussole(self):
        pg.draw.circle(self.game.screen, self.bouss_color_ext1, self.bouss_pos, self.bouss_rayon_ext1,
                       self.bouss_epaisseur_ext1)  #Contour de la boussole
        pg.draw.circle(self.game.screen, self.bouss_color_ext2, self.bouss_pos, self.bouss_rayon_ext2,
                       self.bouss_epaisseur_ext2)  #Contour extérieur de la boussole

        #Dessine l'aiguille de la boussole (orientation du joueur)
        aiguille_x = (self.bouss_rayon_ext1 - self.bouss_epaisseur_ext1) * math.cos(self.game.player.rotation * math.pi / 180)
        aiguille_y = -(self.bouss_rayon_ext1 - self.bouss_epaisseur_ext1) * math.sin(self.game.player.rotation * math.pi / 180)

        pg.draw.line(self.game.screen, (255, 0, 0), self.bouss_pos,
                     (self.bouss_pos[0] + aiguille_x, self.bouss_pos[1] + aiguille_y), 2)

    def draw_mini_carte(self):
        offcet_x = self.coord_x_mini_carte
        coord_x = 0
        coord_y = 0

        #1) Dessine la mini carte 2d:
        for l_cour in self.level_courant:

            for col in l_cour:
                if col == '1':
                    #On dessine un mur
                    pg.draw.rect(self.game.screen, self.couleur_mur,
                                 (offcet_x + (coord_x ), coord_y ,
                                  self.taille_case[0] * self.echelle_mini_carte,
                                  self.taille_case[1] * self.echelle_mini_carte))

                else:
                    #On dessine le sol
                    pg.draw.rect(self.game.screen, self.couleur_sol,
                                 (offcet_x + (coord_x ), coord_y ,
                                  self.taille_case[0] * self.echelle_mini_carte,
                                  self.taille_case[1] * self.echelle_mini_carte))

                coord_x += self.taille_case[0] * self.echelle_mini_carte

            coord_y += self.taille_case[1] * self.echelle_mini_carte
            coord_x = 0

        #2) Dessine le joueur
        rayon = (self.taille_case[0] / 2) * self.echelle_mini_carte
        player_x_pixel = self.game.player.coord_x_pixel #+ rayon
        player_y_pixel = self.game.player.coord_y_pixel #+ rayon

        player_x_pixel = offcet_x + (player_x_pixel * self.echelle_mini_carte)
        player_y_pixel = player_y_pixel * self.echelle_mini_carte

        pg.draw.circle(self.game.screen, (255, 0, 0), (player_x_pixel, player_y_pixel), 2)

    #Ecrit des informations à l'écran
    def write_screen (self, message, num_ligne):

        if num_ligne < self.nbre_ligne_max and num_ligne > 0:

            coord_y = (num_ligne-1) * (self.taille_police + self.espace_vertical)
            rendu_mess = self.myfont.render(message, False, self.couleur_mess)
            self.game.screen.blit(rendu_mess, (self.mess_pos_x, coord_y))