

import pygame as pg
import math
import levels as lev
import constantes as const
import game as game



#Plus tard prévoir un véritable menu!
def main_menu(fenetre):
    ga = game.Game(fenetre)
    ga.start_game()


#-------------------
#Début du programme|
#-------------------
if __name__ == '__main__':
    pg.init()
    fenetre = pg.display.set_mode(const.resolution) #, pg.FULLSCREEN => Pour plein écran
    main_menu(fenetre)
