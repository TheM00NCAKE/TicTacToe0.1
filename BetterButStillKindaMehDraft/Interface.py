from PIL import Image, ImageTk
from State import State
from Players import Player
import tkinter as tk
class Interface():
    def __init__(self,game):
        """Initialize the interface window, and the Game instance used to play the game"""
        self.window=tk.Tk()
        self.game=game
    
    def create_button(self,nom_frame,width_button,height_button,bg_color,bg_highlight_color,evenement,x,y,texte,rel_x,rel_y,val):
        """Returns a button created with the params above"""
        button=tk.Canvas(nom_frame,width=width_button,height=height_button,bg=bg_color,highlightbackground=bg_highlight_color)
        button.bind("<Button-1>",lambda event:evenement())
        button.create_text(x,y, text=texte,font=("Segoe UI",20,"bold"),fill="white")
        if self.game.state==State.NOT_STARTED or val==1 :
            button.place(relx=rel_x, rely=rel_y, anchor="center")
        return button

    def setup_gui(self,player,inventory_color,board_color):
        """Initialize all the Tkinter elements that will be used in the ui"""
        self.window.geometry("1500x1000")
        try : 
            image_test = Image.open("images/bg.png")
        except :
            raise Exception ('Background image not found')
        image_test = image_test.resize((1500, 1000), Image.Resampling.LANCZOS)  #Pour que l'image remplisse la fenêtre
        self.bg_img = ImageTk.PhotoImage(image_test) 
        self.frame_for_titlescreen=tk.Frame(self.window,width=1500,height=1000)
        self.content_for_titlescreen=tk.Canvas(self.frame_for_titlescreen,width=1500,height=1000)
        self.board_frame=tk.Frame(self.window,width=1500,height=1000)
        self.board_frame_content=tk.Canvas(self.board_frame,width=1500,height=1000)
        self.canvas_comment=tk.Canvas(self.board_frame_content,width=100,height=300,bg=player.color)
        self.canvas_for_inventory=tk.Canvas(self.board_frame_content,width=1200,height=100,bg="royalblue",highlightbackground="white")
        self.frame_for_inventory=tk.Frame(self.canvas_for_inventory,width=1200,height=100,bg='royalblue',highlightbackground="white")
        self.inventory=tk.Canvas(self.frame_for_inventory,width=546,height=100, bg=inventory_color,highlightbackground='white')
        self.inventory_buttons=tk.Frame(self.frame_for_inventory,width=600,height=100, bg="royalblue")
        self.draw_item_button=tk.Canvas(self.inventory_buttons,width=100,height=50,bg="dodgerblue1",highlightbackground="dodgerblue2")
        self.cancel_button=tk.Canvas(self.inventory_buttons,width=100,height=50,bg="indianred1",highlightbackground="indianred2")
        self.canvas_score=tk.Canvas(self.board_frame_content,width=1200,height=60,bg="cornflowerblue",highlightbackground="cornflowerblue")
        self.texte_score=self.canvas_score.create_text(600,30,text=f"Score of player O : {self.game.score_o}      Score of player X : {self.game.score_x}",font=("Segoe UI",20), fill="white")
        self.board_ui=tk.Canvas(self.board_frame_content,width=1200,height=600,bg=board_color,highlightbackground="royalblue4")
        self.frame_end=tk.Frame(self.window,width=1500,height=1000)
        self.contenu_frame_end=tk.Canvas(self.frame_end,width=1500,height=1000)

    def write_comment(self,texte):
        """Displays a comment if the player does something wrong on the purple canvas to the right"""
        self.canvas_comment.create_text(50,150,text=texte,font=('Segoe UI',10),width=90)
        self.canvas_comment.after(1000, lambda:self.canvas_comment.delete('all'))

    def qui_joue(self,event):
        """Execute the process_player_action method and determine who's the actual and next player"""
        if event==None:
            self.game.clic_origin=State.DRAWING
        elif self.game.clic_origin==State.NOT_DEFINED:
            self.game.clic_origin=State.BOARD
            next_player=self.player_2 if self.game.turn_count%2!=0 else self.player_1
            self.game.turn_count+=1
            self.game.change_cursor(next_player.cursor)
            return
        else : 
            if event.widget==self.board_ui:
                canvas=event.widget 
                item=canvas.find_closest(event.x, event.y)
                tags=canvas.gettags(item)
                if 'overlay' in tags:
                    self.game.clic_origin=State.OVERLAY_ITEM
                else :
                    self.game.clic_origin=State.BOARD
            elif event.widget == self.inventory :
                self.game.clic_origin=State.INVENTORY
        current_player=self.player_1 if self.game.turn_count%2!=0 else self.player_2
        next_player=self.player_2 if self.game.turn_count%2!=0 else self.player_1
        self.game.process_player_action(event,current_player,next_player)

    def pack_board(self, event=None):
        """Fait la transition entre le menu de début et le plateau sur la même fenêtre en détruisant les éléments du title screen."""
        try :
            if self.game.state==State.NOT_STARTED:
                self.frame_for_titlescreen.destroy()
                self.game.set_state(State.PLAYING)
            self.canvas_comment.place(x=1370,y=225)
            self.canvas_for_inventory.pack(side=tk.BOTTOM,pady=(0,5))
            self.frame_for_inventory.pack()
            self.inventory.bind("<Button-1>", self.qui_joue)
            self.inventory.pack(side=tk.LEFT,padx=(0,15))
            self.inventory_buttons.pack(side=tk.LEFT,padx=15)
            self.draw_item_button.bind('<Button-1>',lambda event : self.player_1.draw(self.game) if self.game.turn_count%2!=0 else self.player_2.draw(self.game))
            self.draw_item_button.pack(side=tk.LEFT,padx=(0,11))
            self.cancel_button.bind('<Button-1>', lambda event : Player.cancel_item(self.player_1, self.game) if self.game.turn_count%2!=0 else Player.cancel_item(self.player_2, self.game))
            self.canvas_score.pack(pady=(5,0))
            self.board_ui.bind("<Button-1>", self.qui_joue)
            self.board_ui.pack(side=tk.BOTTOM,pady=5,padx=150)
            self.board_frame_content.pack()
            self.board_frame.pack()
        except Exception as e:
            print (f'An error occured in the pack_board method : {e}')  

    def update_inventory_display(self,player):
        """update the interface to display correctly the current inventory after an event related to it"""
        self.inventory.delete("inventory_text")
        for i, item in enumerate (player.own_inventory):
            x,y=self.game.inventory_coords[i]
            self.game.ui.inventory.create_image(x,y,image=player.liste[item],tags="inventory_text")
        self.game.ui.canvas_comment.config(bg=player.color)
    
    def settings_menu(self):
        """Template for the settings, has nothing yet :)"""
        self.frame_for_titlescreen.pack_forget()
        frame_for_settings=tk.Frame(self.window,width=1500,height=1000)
        frame_for_settings.pack()
        can=tk.Canvas(frame_for_settings,width=1500,height=1000)
        can.pack()
        can.create_image(0, 0, image=self.bg_img, anchor="nw")
        settings_content=tk.Canvas(frame_for_settings,width=1000,height=750,bg="grey")
        can.create_window(750, 400, window=settings_content, anchor="center")
        self.create_button(settings_content,80,80,"red","deepskyblue4",lambda:[frame_for_settings.destroy(),self.frame_for_titlescreen.pack()],42,40,"X",0.95,0.065,1)

    def titlescreen(self):
        """Builds and displays the titlescreen. Also builds the board, but shows it only when the player clicks on "play", in that case the method calls packboard"""
        try :
            self.content_for_titlescreen.create_image(0, 0, image=self.bg_img, anchor="nw")
            self.content_for_titlescreen.create_text(750,20, text="Made by NotA_M00NCAKE (no one cares because LOOK AT THIS SHITTY INTERFACE DAMMIT)",font=("Segoe UI",10,"bold"))
            self.content_for_titlescreen.create_text(750, 270,text="Welcome to this stupid game : \n\n\n\n The TicTacToe 5x with an item system (I still have no idea on how to call my game)", font=("Segoe UI",20,"bold"),justify="center")
            self.content_for_titlescreen.create_text(750, 500,text="(3rd draft before coding in Java)", font=("Segoe UI",10),)
            ###########"esthétique du plateau après avoir lancé Start boutton###########
            self.board_frame_content.create_image(0, 0, image=self.bg_img, anchor="nw")
            for i in range (110,660,110):
                self.inventory.create_line(i,0,i,100,fill="black")
            self.draw_item_button.create_text(50,25,text="Draw item", font=('Segoe UI',10,'bold'))
            self.cancel_button.create_text(50,25,text="Cancel", font=('Segoe UI',10,'bold'))
            for i in range (50,600,50):
                self.board_ui.create_line(0,i,1200,i,fill="dodgerblue4")
            for i in range (100,1200,100):
                self.board_ui.create_line(i,0,i,1200,fill="dodgerblue4")
            rayon = 10 
            for i in range(50, 600, 50):    
                for j in range(100, 1200, 100): 
                    self.board_ui.create_oval(j-rayon,i-rayon,j+rayon,i+rayon,fill="red", tags='overlay')
            self.board_ui.tag_bind('overlay',"<Button-1>",self.qui_joue)
            self.board_ui.itemconfigure("overlay", state="hidden")
            self.window.config(cursor=self.player_1.cursor) 
            self.button_start=self.create_button(self.frame_for_titlescreen,200,50,"deepskyblue3","deepskyblue4",self.pack_board,100,25,"Start",0.5,0.85,0)
            self.button_quit=self.create_button(self.frame_for_titlescreen,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit",0.7,0.85,0)
            self.button_params=self.create_button(self.frame_for_titlescreen,200,50,"blue","purple",self.settings_menu,100,25,"Settings",0.3,0.85,0)
            ##################################################################
            if self.game.state==State.NOT_STARTED:
                self.content_for_titlescreen.pack()
                self.frame_for_titlescreen.pack()
                self.window.mainloop()
            else:
                self.pack_board()
        except Exception as e:
            print (f'An error occured in the titlescreen method : {e}')  

    def endscreen(self):
        """Displays the endscreen when the game is over, has multiple options such as quit, replay and titlescreen"""
        try :
            self.board_frame.destroy()
            self.contenu_frame_end.create_image(0, 0, image=self.bg_img, anchor="nw")
            message=('Match nul, dommage...' if self.game.state==State.GAME_DRAW else f'The player {"O" if self.game.state==State.O_WIN else "X"} won !')
            self.contenu_frame_end.create_text(750,300, text=message, font=("Segoe UI",30,"bold"),justify="center")
            self.contenu_frame_end.pack()
            self.button_replay=self.create_button(self.frame_end,200,50,"deepskyblue3","deepskyblue4",lambda:[self.game.set_state(State.PLAYING),self.frame_end.destroy(),self.game.start_game(board_color="#B9E1F4",inventory_color="#907EBD")],100,25,"Replay",0.5,0.65,1)
            self.button_quit=self.create_button(self.frame_end,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit",0.7,0.65,1)
            self.button_ts=self.create_button(self.frame_end,200,50,"seagreen1","seagreen3",lambda:[self.game.set_state(State.NOT_STARTED),self.frame_end.destroy(),self.game.start_game(board_color="#B9E1F4",inventory_color="#907EBD")],100,25,"Title screen",0.3,0.65,1)
            self.frame_end.pack()
        except Exception as e:
            print (f'An error occured in the endscreen method  : {e}')  
        
    def game_process(self,player1,player2,inventory_color,board_color):
        #initialize each player to its corresponding turn positions, and its cell value stored into board_matrix
        self.player_1=player1
        self.player_2=player2
        self.player_1.update_val_player(1)
        self.player_2.update_val_player(2)
        #This part is executed only when the programs launches
        self.setup_gui(player1,inventory_color,board_color) 
        self.game.board_matrix=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.game.cell_img_id=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.titlescreen()