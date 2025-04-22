import pygame as pg
import math
import levels as lev
import constantes as const


class Player():

    def __init__(self, game):
        self.game = game

        self.coord_x_case = 1.6  #Coord sur la MAP => 1,6 case depuis la gauche de l'écran
        self.coord_y_case = 1.6

        self.coord_x_pixel = 0   #Coord du joueur en pixel
        self.coord_y_pixel = 0

        self.rotation = 0.0      #Angle de rotation du joueur
        self.rotation_rad = 0.0

        self.v_rotation = 1.5    #Vitesse de rotation
        self.v_avancer = const.taille_case[0]/10              #Vitesse pour avancer

        #Pour la gestion du lancé de rayon (détection des murs)
        self.angle_vue = 60                                    #Angle de vue du joueur en degré
        self.distance_vue_cases = 30                           #Distance max à laquelle le joueur distingue les objets (évite de ramer)
        self.nbre_rayons = const.resolution[0] #600            #Nombre de rayon à lancer
        self.pas_angulaire = self.angle_vue / self.nbre_rayons #Pas angulaire entre chaque rayon
        self.l_rayons = []                                     #Liste des rayons (300 en tout)
        self.rayon_info = {                                    #Dictionnaine stockant les informations du rayon courant
            "angle" : 0,
            "angle_rad": 0,
            "dist_x" : 0,
            "dist_y" : 0,
            "diag" : 0,
            "mur_coord_x" : 0,
            "mur_coord_y": 0,
            "case_exacte_x": 0,
            "case_exacte_y": 0

        }

    def conv_degre_en_rad(self, rot=1000):

        if rot != 1000:
            return round(rot * math.pi / 180, 2)
        else:
            return round(self.rotation * math.pi / 180, 2)

    def update_player(self):
        self.deplacer_player()
        self.lancer_les_rayons()

    #Déplace le joueur en fonction des touches du clavier + gestion des collisions
    def deplacer_player(self):
        temp_x_pixel = self.coord_x_case * self.game.map.taille_case[0]
        temp_y_pixel = self.coord_y_case * self.game.map.taille_case[1]

        # 1) Modification de la rotation
        #Si touche d => tourne à droite
        if self.game.keys[pg.K_d]:
            self.rotation -= self.v_rotation
            if self.rotation >= 360:
                self.rotation %= 360

        #Si touche q => tourne à gauche
        if self.game.keys[pg.K_q]:
            self.rotation += self.v_rotation
            if self.rotation < 0:
                self.rotation += 360

        if self.game.keys[pg.K_KP6]:
            self.rotation = 0

        if self.game.keys[pg.K_KP8]:
            self.rotation = 90

        if self.game.keys[pg.K_KP4]:
            self.rotation = 180

        if self.game.keys[pg.K_KP2]:
            self.rotation = 270

        if self.game.keys[pg.K_KP9]:
            self.rotation = 45

        if self.game.keys[pg.K_KP7]:
            self.rotation = 135

        if self.game.keys[pg.K_KP1]:
            self.rotation = 225

        if self.game.keys[pg.K_KP3]:
            self.rotation = 315

        self.rotation_rad = self.conv_degre_en_rad()

        # 2) Modification de l'avancement du joueur
        # Si touche z => joueur avance
        if self.game.keys[pg.K_z]:  #Pour pygame z= w => clavier anglais
            temp_x_pixel += self.v_avancer * math.cos(self.rotation_rad)
            temp_y_pixel -= self.v_avancer * math.sin(self.rotation_rad)
            self.flag_deplacement = True
        else:
            self.flag_deplacement = False

        if self.game.keys[pg.K_s]:
            temp_x_pixel -= self.v_avancer * math.cos(self.rotation_rad)
            temp_y_pixel += self.v_avancer * math.sin(self.rotation_rad)
            self.flag_deplacement = True
        else:
            self.flag_deplacement = False


        #3) Gestion des collisions avec un mur
        flag_collision_x = False
        flag_collision_y = False

        #3-1) Vérification en X
        temp_x_case = math.floor(temp_x_pixel / self.game.map.taille_case[0])     #Case suivante ou tjrs la même!
        temp_y_case = math.floor(self.coord_y_case)                               #Case courante
        flag_collision_x = self.detecter_mur(temp_x_case, temp_y_case)

        #Si pas de collision en X => MAJ des coords en x du joueur
        if flag_collision_x == False:
            self.coord_x_pixel = temp_x_pixel                                     #Case courante
            self.coord_x_case = temp_x_pixel / self.game.map.taille_case[0]       #Case suivante ou tjrs la même!


        #3-2) Vérification en Y
        temp_x_case = math.floor(self.coord_x_case)                               #Case courante
        temp_y_case = math.floor(temp_y_pixel / self.game.map.taille_case[1])     #Case suivante ou tjrs la même!
        flag_collision_y = self.detecter_mur(temp_x_case, temp_y_case)


        #Si pas de collision en Y => MAJ des coords en x du joueur
        if flag_collision_y == False:
            self.coord_y_pixel = temp_y_pixel
            self.coord_y_case = temp_y_pixel / self.game.map.taille_case[1]


    #----------------------------------------------------------------------------------------------------------
    #Donne l'ordre d'envoyer des rayons invisibles pour calculer les distances qui séparent le joueur des murs
    #----------------------------------------------------------------------------------------------------------
    def lancer_les_rayons(self):

        angle_courant = self.rotation + (self.angle_vue / 2)

        #Vide la liste des rayons pour la recalculer
        self.l_rayons = []
        i = 0

        while i < self.nbre_rayons:

            if angle_courant > 360:
                angle_courant %= 360

            if angle_courant < 0:
                angle_courant = 360 + angle_courant

            self.lancer_un_rayon(angle_courant)
            angle_courant -= self.pas_angulaire

            i += 1

    # -------------------------------------------------------------------------
    #Lance un rayon invisible depuis la position du joueur.
    #Permet de repérer les murs et de calculer les distances qui l'en séparent
    #--------------------------------------------------------------------------
    def lancer_un_rayon(self, angle):

        angle_rad = self.conv_degre_en_rad(angle)

        flag_mur = False      #Passe à True si on détecte un mur
        flag_fin_niv = False  #Passe à True si on arrive à l'extrémité du niveau

        P_coord_x_case = self.coord_x_case        #Récupération des cases courantes du joueur
        P_coord_y_case = self.coord_y_case

        P_coord_x = self.coord_x_pixel            #Récupération des coord courantes du joueur
        P_coord_Y = self.coord_y_pixel


        case_x_finale1 = 0                        #Case de l'intersection quand calcul sur abscisse
        case_y_finale1 = 0

        pos_exacte_sur_case_x1 = 0                #Pos exacte du lieu de l'intersection  quand calcul sur abscisses
        pos_exacte_sur_case_y1 = 0

        case_x_finale2 = 0                        #Case de l'intersection quand calcul sur ordonnées
        case_y_finale2 = 0

        pos_exacte_sur_case_x2 = 0                #Position exacte du lieu de l'intersection  quand calcul sur ordonnées
        pos_exacte_sur_case_y2 = 0

        # 1) Détermine l'angle de calcul
        if angle > 360:
            print (f"Attention!! angle= {angle}")

        if angle >= 0 and angle <= 90:
            angle_calcul = angle

        elif angle > 90 and angle <= 180:
            angle_calcul = 180 - angle

        elif angle > 180 and angle <= 270:
            angle_calcul = angle - 180

        elif angle <= 360:
            angle_calcul = 360 - angle

        angle_calcul_rad = self.conv_degre_en_rad(angle_calcul)
        tan_angle_calcul = math.tan(angle_calcul_rad)
       
        #2) Calcul de la prochaine intersection en X (intersection avec lignes verticales)
        if angle != 90 and angle != 270:
            next_case_x = self.calculer_prochaine_intersection('x', angle)
            pos_exacte_sur_case_x1 = next_case_x

            while flag_mur == False and flag_fin_niv == False:
                #2-1) Calcul de la distance entre le joueur et la case en X
                dist_P_cx = abs(next_case_x - P_coord_x_case)

                #2-2) Calcul de la hauteur en Y correspondante
                if angle > 90 and angle < 270: #Enlève 1 case => profondeur du mur!
                    dist_P_cx -= 1
                dist_P_cy = dist_P_cx * tan_angle_calcul

                # 2-3) Détermine la nouvelle case correspondante
                if angle > 0 and angle < 180:           #Le joueur monte
                    pos_exacte_sur_case_y1 = P_coord_y_case - dist_P_cy
                    next_case_y = math.floor(pos_exacte_sur_case_y1)

                elif angle == 0 or angle == 180:        #Le joueur marche parallèle à l'axe des abscisses
                    pos_exacte_sur_case_y1 = P_coord_y_case
                    next_case_y = math.floor(pos_exacte_sur_case_y1)

                else:                                   #Le joueur descend
                    pos_exacte_sur_case_y1 = P_coord_y_case + dist_P_cy
                    next_case_y = math.floor(pos_exacte_sur_case_y1)

                #2-4) vérifie s'il s'agit d'un mur:
                flag_mur = self.detecter_mur(next_case_x, next_case_y)

                #2-5) Passe à la case en x suivante:
                if flag_mur == False:
                    if angle > 270 or angle < 90:
                        next_case_x += 1
                    else:
                        next_case_x -= 1
                    pos_exacte_sur_case_x1 = next_case_x

                #2-6) Vérifie qu'on ait pas dépassé le niveau
                if next_case_x > self.game.map.nbre_max_case_x or next_case_x < 0:
                    flag_fin_niv = True

            # 2-7) Calcul de la diagonale correspondante
            diagonale_x = math.sqrt(
                ((dist_P_cx * self.game.map.taille_case[0]) * (dist_P_cx * self.game.map.taille_case[0])) + \
                ((dist_P_cy * self.game.map.taille_case[1]) * (dist_P_cy * self.game.map.taille_case[1])))
                      
            case_x_finale1 = next_case_x
            case_y_finale1 = next_case_y

        else:
            diagonale_x = 99999

        # 3) calcul de la prochaine intersection en Y (intersection avec lignes horizontales)
        flag_mur = False      #Passe à True si on détecte un mur
        flag_fin_niv = False  #Passe à True si on arrive à l'extrémité du niveau


        if angle != 0 and angle != 180 or angle == -0.0999999999998426:
            next_case_y = self.calculer_prochaine_intersection('y', angle)
            pos_exacte_sur_case_y2 = next_case_y

            while flag_mur == False and flag_fin_niv == False:
                #3-1) Calcul de la distance entre le joueur et la case en Y
                dist_P_cy = abs(next_case_y - P_coord_y_case)

                if angle > 0 and angle < 180: #Enlève 1 case => profondeur du mur!
                    dist_P_cy -= 1

                #3-2) Calcul de la longueur en X correspondante
                if (angle_calcul_rad != 0):
                    dist_P_cx = dist_P_cy / tan_angle_calcul

                else:
                    dist_P_cx = 99999

                #3-3) Détermine la nouvelle case correspondante
                if angle > 270 or angle < 90:          #Le joueur avance vers la gauche
                    pos_exacte_sur_case_x2 = dist_P_cx + P_coord_x_case
                    next_case_x = math.floor(pos_exacte_sur_case_x2)

                elif angle == 270 or angle == 90:       #Le joueur marche parallèle à l'axe des ordonnées
                    pos_exacte_sur_case_x2 = P_coord_x_case
                    next_case_x = math.floor(pos_exacte_sur_case_x2)

                else:                                   #Le joueur avance vers la droite
                    pos_exacte_sur_case_x2 = P_coord_x_case - dist_P_cx
                    next_case_x = math.floor(pos_exacte_sur_case_x2)

                #2-4) vérifie s'il s'agit d'un mur:
                flag_mur = self.detecter_mur(next_case_x, next_case_y)

                #2-5) Passe à la case en x suivante:
                if flag_mur == False:
                    if angle > 0 and angle < 180:
                        next_case_y -= 1
                    else:
                        next_case_y += 1

                    pos_exacte_sur_case_y2 = next_case_y

                #2-6) Vérifie qu'on ait pas dépassé le niveau
                if next_case_y > self.game.map.nbre_max_case_y or next_case_y < 0:
                    flag_fin_niv = True

            #2-7) Calcul de la diagonale correspondante
            if (angle_calcul_rad != 0 and flag_mur != -1):
                diagonale_y = (dist_P_cy * self.game.map.taille_case[1])  / math.sin(angle_calcul_rad)
            else:
                diagonale_y = 99999

            case_x_finale2 = next_case_x
            case_y_finale2 = next_case_y

        else:
            diagonale_y = 99999

        #Sauvegarde de la plus petite diagonale:
        self.rayon_info["angle"] = angle
        self.rayon_info["angle_rad"] = angle_rad


        if diagonale_x < diagonale_y:

            if angle > 90 and angle < 270:
                case_x_finale1 += 1
                pos_exacte_sur_case_x1 += 1

            if angle > 0 and angle < 180:
                case_y_finale1 += 1
                pos_exacte_sur_case_y1 += 1

            self.rayon_info["mur_coord_x"] = case_x_finale1
            self.rayon_info["mur_coord_y"] = case_y_finale1
            self.rayon_info["dist_x"] = math.floor( case_x_finale1 * self.game.map.taille_case[0] )
            self.rayon_info["dist_y"] = math.floor( case_y_finale1 * self.game.map.taille_case[1] )
            self.rayon_info["diag"] = diagonale_x
            self.rayon_info["case_exacte_x"] = pos_exacte_sur_case_x1
            self.rayon_info["case_exacte_y"] = pos_exacte_sur_case_y1

        else:
            if angle > 90 and angle < 270:
                case_x_finale2 += 1
                pos_exacte_sur_case_x2 += 1

            if angle > 0 and angle < 180:
                case_y_finale2 += 1
                pos_exacte_sur_case_y2 += 1

            self.rayon_info["mur_coord_x"] = case_x_finale2
            self.rayon_info["mur_coord_y"] = case_y_finale2
            self.rayon_info["dist_x"] = math.floor(case_x_finale2 * self.game.map.taille_case[0])
            self.rayon_info["dist_y"] = math.floor(case_y_finale2 * self.game.map.taille_case[1])
            self.rayon_info["diag"] = diagonale_y
            self.rayon_info["case_exacte_x"] = pos_exacte_sur_case_x2
            self.rayon_info["case_exacte_y"] = pos_exacte_sur_case_y2

        self.l_rayons.append(self.rayon_info.copy())        #Copy car on ajoute une ref du dictionnaire
                                                            #Autrement toutes les ref pointent sur la même valeur!!

    def calculer_prochaine_intersection(self, axe_rech, angle):
        if axe_rech == 'x':
            #1) Détermine les coords en x de la case suivante
            if angle > 270 or angle < 90:                   #=> Prochaine case: suivante à droite
                case_x = math.ceil(self.coord_x_case)

            elif angle == 270 or angle == 90:               #=> Prochaine case: N'existe pas!!! Case actuelle
                case_x = 99999

            else:                                           #=> Prochaine case: précédente à gauche
                case_x = math.floor(self.coord_x_case)-1

            case = case_x

        else:
            if angle > 0 and angle < 180:                   #=> Prochaine case: Case précédente en montant
                case_y = math.floor(self.coord_y_case) - 1

            elif angle == 0 or angle == 180:                #=> Prochaine case: N'existe pas!!! Case actuelle
                case_y = 99999

            else:                                           #=> Prochaine case: Case suivante en descendant
                case_y = math.ceil(self.coord_y_case)

            case = case_y

        return case


    #Indique si la case en question est un mur
    def detecter_mur(self, index_x, index_y):

        if index_y < self.game.map.nbre_max_case_y and index_y >= 0:
            ligne_courante = self.game.map.level_courant[index_y]

            if index_x < self.game.map.nbre_max_case_x and index_x >= 0:
                case_courante = ligne_courante[index_x]

                if case_courante == str(1):
                    return True
                else:
                    return False
            else:
                return -1

        else:
            return -2