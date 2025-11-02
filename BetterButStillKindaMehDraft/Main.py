from Game import Game
from Players import Player

if __name__=="__main__":
    new_game=Game()
    player_o=Player('circle',"#199E86","images/cercle.png","images/barricade.png","images/item2.png","images/bouclier_cercle.png","images/item4.png","images/BombePortable.png","images/VolDeData2.png","#B9E1F4","#907EBD")
    player_x=Player('X_cursor',"#1D1C70",'images/croix.png',"images/barricade.png","images/item2.png","images/bouclier_croix.png","images/item4.png","images/BombePortable.png","images/VolDeData2.png","#B9E1F4","#907EBD")
    new_game.start_game("#B9E1F4","#907EBD",player_o,player_x)