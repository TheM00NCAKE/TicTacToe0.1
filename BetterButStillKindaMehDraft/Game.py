import math
from Interface import Interface
from Players import Player, Item
from State import State

class Game : 
    def __init__(self):
        """This constructor will init the most important elements of the game : 
        -board_matrix represents the current state of the board, each
        position being a cell of the board, and each position having a distinct value : 0=empty, 1=player O, 2=player X, 
        10=reserved cell by O, 20 : reserved cell by X.
        -cells_img_id represents items that is currently active on the board, the corresponding cells can display the item image, which 
        has an id to identify it.
        -protected_cells is a list containing all cells under the use of item 3 (protect_cell)
        -coords and inventory coords each store the center of each cell respectively corresponding to the board and the inventory. 
        Is used to display images to the center.
        -remaining_turns is only related to the fourth item (forbid_use_item) that initially is valuable for 4 turns in total.
        The rest is pretty self-explainatory.
        """
        self.state=State.NOT_STARTED  
        self.turn_count=1   
        self.score_o=0
        self.score_x=0
        self.board_matrix=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]    
        self.cell_img_id=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.protected_cells=[]
        self.coords=[[[(r-25),i-50] for i in range (100,1300,100)] for r in range (50,700,50)]   
        self.inventory_coords=[[i,50]for i in range (55, 560,110)] 
        self.remaining_turn=0
        self.clic_origin=State.BOARD
        self.ui=Interface(self)            

    def start_game(self,board_color,inventory_color,player_o,player_x):
        """Method to start the game by initializing all elements needed for the game through game_process"""
        if self.state==State.NOT_STARTED or self.state==State.PLAYING:      
            self.ui.game_process(player_o,player_x,inventory_color,board_color) #you decide here who starts first : game_process(player1,player2,...,...)
    
    def set_state(self,state):
        """unique setter that will be used to update what is happening in-game """
        self.state=state
    
    @staticmethod
    def check_index(val1,val2):
        """check if the values is superior to the board index or not (11, 11 because the board is a 12x12)"""
        return 0<=val1<=11 and 0<=val2<=11

    def victory(self,player,row_num,col_num):
        """Verifies if the player has won. It takes the coordinates of the last checked cell and 
        verifies around it (horizontally, vertically and diagonally) if 5 cells in a row have been redeemed
        by the same player (by checking the value of each cell in the matrix_board).
        Doesn't return anything, but will update the score if a victory occured. """
        verif_verticale=any(all(self.board_matrix[i+r][col_num]==player.cell_value for i in range (5)) for r in range (8)) 
        verif_horizontale=any(all(self.board_matrix[row_num][i+r]==player.cell_value for i in range (5)) for r in range (8))
        verif_diag_droit=any(all(Game.check_index(row_num+i+r,col_num+i+r) and 
            self.board_matrix[row_num+i+r][col_num+i+r]==player.cell_value for i in range(-4,1)) for r in range (8))
        verif_diag_gauche=any(all(Game.check_index(row_num+i+r,col_num-i-r) and 
            self.board_matrix[row_num+i+r][col_num-i-r]==player.cell_value for i in range(-4,1)) for r in range (8))
        if verif_verticale or verif_horizontale or verif_diag_droit or verif_diag_gauche:
            self.turn_count=0      #the turn_count goes back to 0 because the game ended
            if player.cursor=='circle':
                self.set_state(State.O_WIN)
                self.score_o+=1
            else :
                self.set_state(State.X_WIN)
                self.score_x+=1
            self.ui.canvas_score.itemconfig(self.ui.texte_score,text=f"Score of player O : {self.score_o}      Score of player X : {self.score_x}",font=("Segoe UI",15,"bold"))
    
    def change_cursor(self,icone):
        self.ui.window.config(cursor=icone) 

    def check_remaining_turns(self):
        """made specifically to check if the item 4 is still active or not"""
        if self.remaining_turn>=1:
            self.remaining_turn-=1
            if self.remaining_turn==0 : 
                self.set_state(State.PLAYING)

    def update_board(self,player,image,x,y):
        """Update the board matrices depending on the player's action"""
        if self.cell_img_id[y][x]!=0 and self.protected_cells.count([y,x])==0:
            self.ui.board_ui.delete(self.cell_img_id[y][x])
        image_id=self.ui.board_ui.create_image(self.coords[y][x][1],self.coords[y][x][0], image = image,anchor="center")
        self.cell_img_id[y][x]=image_id
        self.board_matrix[y][x]=player
    
    def define_cells_coords(self,x,y):
        """Transforms clicking coords to indexes that will be used to have access to the correct matrix cell"""
        if self.clic_origin in (State.BOARD,State.RECLICK,State.OVERLAY_ITEM) :
            if self.clic_origin==State.OVERLAY_ITEM:
                """overlay indexes"""
                x-=20
                y-=20
            x = math.floor(x/100)            
            y = math.floor(y/50) if y<600 else 11 
        else:
            """inventory indexes"""
            x = math.floor(x/110)
            y = 50
        return x,y
    
    def on_board_action(self,current_player,x,y,next_player):
        """Manages actions made by the current player on the board, doesn't return anything but updates the board interface and the board matrices"""
        #if the player's clicking on a cell reserved by them, or not redeemed yet 
        if self.board_matrix[y][x] in (0,current_player.reserve_val):
            if self.state in (State.PLAYING, State.CANT_PLAY_ITEM):                          
                self.update_board(current_player.cell_value,current_player.symbol,x,y)
                current_player.can_draw=True
            elif self.state==State.PLAY_ITEM and current_player.play_item_pos is not None :
                current_player.use_item(current_player.play_item_pos,self,x,y,self.turn_count)
                current_player.can_draw=True
            if self.state!=State.RECLICK:
                self.ui.update_inventory_display(next_player)
                self.change_cursor(next_player.cursor)
        #if the player's using an item
        elif self.state==State.PLAY_ITEM and current_player.play_item_pos is not None :
            if current_player.own_inventory[current_player.play_item_pos]==1:   
                current_player.use_item(current_player.play_item_pos,self,x,y,self.turn_count) 
                if self.state!=State.RECLICK:
                    self.ui.update_inventory_display(next_player)
                    self.change_cursor(next_player.cursor)
            elif current_player.own_inventory[current_player.play_item_pos] in (0,2):   
                current_player.use_item(current_player.play_item_pos,self,x,y,self.turn_count)
        #clicked on a redeemed cell, reset its turn 
        else : 
            self.turn_count-=1              
        self.victory(current_player,y,x) 
        self.check_remaining_turns()  

    def process_player_action(self,eventorigin,current_player,next_player):
        """Méthode qui gère la succession des actions du jeu (calcul des coordonnées des cases cliqués, maj du plateau et de l'inventaire,
        gestion de l'utilisation des items etc)"""
        try : 
            if self.clic_origin==State.DRAWING:
                self.turn_count+=1
                self.ui.update_inventory_display(next_player)
                self.change_cursor(next_player.cursor) 
                self.check_remaining_turns()
            elif 1<=self.turn_count<=144 or self.state in (State.PLAYING,State.RECLICK) :
                x,y=self.define_cells_coords(eventorigin.x,eventorigin.y)
                if self.state==State.RECLICK:
                    current_player.use_item(current_player.play_item_pos,self,x,y,self.turn_count)
                    self.turn_count+=1
                    if self.turn_count!=current_player.active_turn:
                        self.ui.update_inventory_display(next_player)
                        self.change_cursor(next_player.cursor)
                        self.victory(current_player,y,x)
                elif self.clic_origin==State.OVERLAY_ITEM:
                    Item.destroy_cells(current_player,self,x,y,current_player.play_item_pos,self.turn_count)
                    self.ui.update_inventory_display(next_player)
                elif self.clic_origin==State.BOARD:
                    self.on_board_action(current_player,x,y,next_player)
                    if not(any(0 in ligne for ligne in self.board_matrix)) and self.state in (State.PLAYING,State.CANT_PLAY_ITEM,State.PLAY_ITEM):
                        self.set_state(State.GAME_DRAW)
                        self.turn_count=0
                    self.turn_count+=1
                else: 
                    Player.gestion_gameplay_item(current_player,self,x)    
                    self.ui.update_inventory_display(current_player) 
                if self.state in (State.O_WIN,State.X_WIN,State.GAME_DRAW): 
                    self.ui.player_1.own_inventory.clear()
                    self.ui.player_1.inventory_item_id.clear()
                    self.ui.player_2.own_inventory.clear()
                    self.ui.player_2.inventory_item_id.clear()
                    self.protected_cells.clear()
                    self.ui.endscreen()   
        except Exception as e:
            print (f'An error occured in the process_player_action method : {e}')  

new_game=Game()
player_o=Player('circle',"#199E86","images/cercle.png","images/barricade.png","images/item2.png","images/bouclier_cercle.png","images/item4.png","images/BombePortable.png","images/VolDeData2.png","#B9E1F4","#907EBD")
player_x=Player('X_cursor',"#1D1C70",'images/croix.png',"images/barricade.png","images/item2.png","images/bouclier_croix.png","images/item4.png","images/BombePortable.png","images/VolDeData2.png","#B9E1F4","#907EBD")
new_game.start_game("#B9E1F4","#907EBD",player_o,player_x)