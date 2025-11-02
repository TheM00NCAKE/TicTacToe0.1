import random
from PIL import Image, ImageTk,ImageOps,ImageColor
import tkinter as tk
from State import State

class Player:
    def __init__(self,cursor,color,file,item1,item2,item3,item4,item5,item6,board_color,inventory_color):
        self.cell_value=0
        self.reserve_val=0
        self.cursor=cursor
        self.own_inventory=[]
        self.inventory_item_id=[]
        self.can_draw=False
        self.active_turn=0
        self.play_item_pos=None
        self.color=color
        self.symbol = self.change_img_color(file,board_color,True)
        self.barricade=self.change_img_color(item1,board_color,True)
        self.item2=self.change_img_color(item2,inventory_color,False)
        self.item3=self.change_img_color(item3,board_color,True)
        self.item4=self.change_img_color(item4,inventory_color,False)
        self.item5=self.change_img_color(item5,inventory_color,False)
        self.item6=self.change_img_color(item6,inventory_color,False)
        self.liste=[self.barricade,self.item2,self.item3,self.item4,self.item5,self.item6]

    def update_val_player(self,value):
        self.cell_value=value
        self.reserve_val=self.cell_value*10

    def draw_item_id(self,game):
        """Randomly returns the item drawn by the player, and the display position if the item in the interface inventory"""
        index=random.randint(0,5)
        self.own_inventory.append(index)
        x,y=game.inventory_coords[len(self.own_inventory)-1]
        return self.liste[index],x,y
    
    def change_img_color(self,file,board_color,state):
        """Change the colors of the item images """
        rgb_bg=ImageColor.getrgb(board_color)
        if state==True:
            rgb_clr=ImageColor.getrgb(self.color)
            img=Image.open(file).convert("L")  #Luminosity, the image's in black and white 
            clr_img=ImageOps.colorize(img, black=rgb_clr, white=rgb_bg)
        else : 
            clr_img=Image.open(file)
            pixels=list(clr_img.getdata())
            modified_pxl=[rgb_bg+(a,) if (r,g,b)==(255,255,255) else(r,g,b,a)  for(r,g,b,a) in pixels]
            clr_img.putdata(modified_pxl)
        clr_img=clr_img.resize((clr_img.width//2, clr_img.height//2), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(clr_img)

    @staticmethod
    def end_item_turn(player, game, position,chosen_state):
        """Execute process after an item is used : delete item from inventory, state reset"""
        player.own_inventory.pop(position)
        player.play_item_pos=None
        game.set_state(chosen_state)
    
    @staticmethod
    def cancel_item(player, game):
        """Change the overlay and interface back to regular state"""
        game.ui.cancel_button.pack_forget()
        if game.ui.board_ui.itemcget('overlay','state')=='normal':
            game.ui.board_ui.itemconfigure('overlay',state='hidden')
            game.ui.board_ui.bind("<Button-1>",game.ui.qui_joue)
        player.play_item_pos=None
        player.active_turn=-1
        game.set_state(State.PLAYING)

    @staticmethod
    def gestion_gameplay_item(player,game,x):
        """NEEDS TO BE REORGANIZED"""
        if player.active_turn==game.turn_count:
            game.ui.write_comment('One item per turn !')
            player.play_item_pos=None
        elif game.state==State.PLAYING:
            if len(player.own_inventory)>=x+1:
                player.play_item_pos=x
                game.set_state(State.PLAY_ITEM)
                if player.own_inventory[player.play_item_pos]>2:
                    x_cell,y_cell=game.inventory_coords[player.play_item_pos]
                    player.use_item(x,game,x_cell,y_cell,game.turn_count)
                else : 
                    game.ui.cancel_button.pack(side=tk.LEFT,padx=11)
            else:
                game.ui.write_comment('Cell has no item')
        elif game.state==State.CANT_PLAY_ITEM : 
            game.ui.write_comment(f"Forbidden to use any item for the remaining {game.remaining_turn} turn(s)")

    def draw(self,game):
        """Responsible of the drawing process"""
        if self.can_draw:
            if len(self.own_inventory)<5:
                chosen_item,x,y=self.draw_item_id(game)
                id_item=game.ui.inventory.create_image(x,y,image=chosen_item,tags="inventory_text")
                self.inventory_item_id.append(id_item)
                game.ui.window.after(500, lambda : game.ui.qui_joue(None))
                self.can_draw=False
            else:
                game.ui.write_comment('Inventory is full !')
        else : 
            game.ui.write_comment('Cannot play items in 2 consecutive rows ')
    
    def use_item(self,position,game,x,y,turn):
        """Use match case to execute corresponding method of the item used"""
        assert isinstance(position, int) and 0<=position<len(self.own_inventory), "The item doesn't exist in your inventory"
        match self.own_inventory[position]:
            case 0 :
                Item.cell_reservation(self,game, x, y,position,turn)
            case 1 : 
                Item.steal_cell(self,game,self.symbol,x,y,position,turn)
            case 2 :
                Item.protect_cell(self,game,x,y,position,turn) 
            case 3 : 
                Item.forbid_use_item(self,game,position,turn)
            case 4 : 
                Item.destroy_cells(self,game,x,y,position,turn) 
            case 5 :
                Item.steal_item(self,game,game.ui.player_2 if self.cell_value==1 else game.ui.player_1,position,turn)

class Item():
    @staticmethod
    def item_4_not_active(game):
        """Returns a boolean if the item4 has been used or is still active"""
        return game.state != State.CANT_PLAY_ITEM
    
    @staticmethod
    def cell_protected(game,x,y):
        return [y,x] in game.protected_cells
    
    @staticmethod
    def cell_reservation(player,game,x,y,position,turn): 
        """Item 1 : reserve a cell for current player, the turn ends after using this"""
        if Item.item_4_not_active(game):
            player.active_turn=turn
            if game.board_matrix[y][x]==0:
                game.update_board(player.cell_value,player.barricade,x,y)
                game.board_matrix[y][x]=player.reserve_val
                game.ui.cancel_button.pack_forget()
                Player.end_item_turn(player, game, position,State.PLAYING)
            else :
                game.ui.write_comment('Choose an empty cell')
                game.set_state(State.RECLICK)
                game.turn_count-=1
    
    @staticmethod
    def steal_cell(player,game,image,x,y,position,turn): 
        """Item 2 : transforms the cell of the other player to theirs, the turn ends after using this"""
        if Item.item_4_not_active(game):
            player.active_turn=turn
            if game.board_matrix[y][x] in (0, player.cell_value, 10,20) or Item.cell_protected(game,x,y):
                game.ui.write_comment('Click on a redeemed non-protected cell that belongs to your opponent !')
                game.set_state(State.RECLICK)
                game.turn_count-=1
            else :
                game.ui.cancel_button.pack_forget()
                game.update_board(player.cell_value,image,x,y)
                game.change_cursor(player.cursor)
                Player.end_item_turn(player, game, position,State.PLAYING)
        
    @staticmethod
    def protect_cell(player,game,x,y,position,turn):
        """Item 3 : protects one of your cell from your opponent, the turn continues after using this"""
        if Item.item_4_not_active(game):
            player.active_turn=turn
            if game.board_matrix[y][x]!=player.cell_value or game.protected_cells.count([y,x])>0 :
                game.ui.write_comment("Protect a reedemed cell that belongs to you !")
                game.set_state(State.RECLICK)
            else : 
                game.ui.cancel_button.pack_forget()
                game.protected_cells.append([y,x])
                game.update_board(player.cell_value,player.item3,x,y)
                Player.end_item_turn(player, game, position,State.PLAYING)
                game.ui.update_inventory_display(player)
            game.turn_count-=1

    def forbid_use_item(player,game,position,turn):
        """Item 4 : forbid everyone to play any items for 4 turns in total, the turn continues after using this"""
        if Item.item_4_not_active(game):
            player.active_turn=turn
            game.remaining_turn=4
            Player.end_item_turn(player, game, position,State.CANT_PLAY_ITEM)

    @staticmethod
    def destroy_cells(player,game,x,y,position,turn):
        """Item 5 : Destroys all cells in a 2x2 radius in chosen position, the turn ends after using this"""
        if Item.item_4_not_active(game):
            game.ui.cancel_button.pack(side=tk.LEFT,padx=11)
            if player.active_turn!=turn:
                game.ui.board_ui.unbind("<Button-1>")
                game.ui.board_ui.itemconfigure("overlay", state="normal")
                player.active_turn=turn
            else :
                game.ui.cancel_button.pack_forget()
                for i in range(x,x+2):
                    for j in range(y,y+2):
                        if not Item.cell_protected(game,i,j):
                            game.ui.board_ui.delete(game.cell_img_id[j][i])
                            game.board_matrix[j][i]=0
                game.clic_origin=State.NOT_DEFINED
                game.ui.board_ui.bind("<Button-1>",game.ui.qui_joue)
                Player.end_item_turn(player, game, position,State.PLAYING)
                game.ui.board_ui.itemconfigure("overlay", state="hidden")
        
    @staticmethod
    def steal_item(player,game,stolen_player,position,turn): 
        """Item 6 : steal an item from the opponent, the turn continues after using this"""
        if Item.item_4_not_active(game):
            if len(player.own_inventory)==5:
                game.ui.write_comment("Inventory already full, cannot store another item")
                game.set_state(State.PLAYING)
            elif len(stolen_player.own_inventory)==0:
                game.ui.write_comment("Inventory of opponent empty...")
                game.set_state(State.PLAYING)
            else : 
                player.active_turn=turn
                stolen_item=random.randint(0,len(stolen_player.own_inventory)-1)
                player.own_inventory.append(stolen_player.own_inventory[stolen_item])
                stolen_player.own_inventory.pop(stolen_item)
                Player.end_item_turn(player, game, position,State.PLAYING)