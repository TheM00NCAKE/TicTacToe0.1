import tkinter as tk
import math
from PIL import Image, ImageTk
from enum import Enum

class State(Enum):
    """Permet à attribuer des valeurs à Jeu.state de façon plus lisible"""
    NON_LANCEE=0
    PARTIE_LANCEE=1
    O_GAGNE=2
    X_GAGNE=3
    MATCH_NUL=4

class Jeu : 
    def __init__(self):
        """Constructeur qui va initier les attributs essentiels. matrice_plateau évolue en fonction de l'état de la partie, 
        chaque liste représentant une ligne et chaque élément une case : 0=case vide, 1=joueur O a coché la case, 2=joueur X"""
        self.state=State.NON_LANCEE  
        self.compteur_tour=1   
        self.score_o=0
        self.score_x=0
        self.matrice_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]    
        self.cords=[[[(r-25),i-50] for i in range (100,1300,100)] for r in range (50,700,50)]   
        self.ui=Graphiques(self)            

    def jeu(self):
        """Méthode qui fait démarrer le jeu"""
        if self.state==State.NON_LANCEE or self.state==State.PARTIE_LANCEE:      
            self.ui.process_jeu()
        else :
            print (f"what ??????")   
    
    @staticmethod
    def verif(val1,val2):
        """vérifie si le calcul dépasse l'indice de plateau ou non"""
        return 0<=val1<=11 and 0<=val2<=11

    def cond_victoire(self,joueur,num_ligne,num_colonne):
        """Vérifie si un joueur a réuni les conditions de victoire ou non. Elle récupère les coordonnées de la dernière case
        cochée et vérifie autour de cette case (horizontalement, verticalement et diagonalement) si 5 cases à la suite ont les 
        mêmes valeurs (1 ou 2 selon le joueur) et va permettre de générer un message indiquant que {joueur} a gagné"""
        verif_verticale=any(all(self.matrice_plateau[i+r][num_colonne]==joueur for i in range (5)) for r in range (8)) 
        verif_horizontale=any(all(self.matrice_plateau[num_ligne][i+r]==joueur for i in range (5)) for r in range (8))
        verif_diag_droit=any(all(Jeu.verif(num_ligne+i+r,num_colonne+i+r) and 
            self.matrice_plateau[num_ligne+i+r][num_colonne+i+r]==joueur for i in range(-4,1)) for r in range (8))
        verif_diag_gauche=any(all(Jeu.verif(num_ligne+i+r,num_colonne-i-r) and 
            self.matrice_plateau[num_ligne+i+r][num_colonne-i-r]==joueur for i in range(-4,1)) for r in range (8))
        if verif_verticale or verif_horizontale or verif_diag_droit or verif_diag_gauche:
            self.compteur_tour=0      #le compteur de cases rempli se remet à 0 car la partie est terminée (se prépare en cas de nouvelle partie)
            if joueur==1:
                self.state=State.O_GAGNE
                self.score_o+=1
            else :
                self.state=State.X_GAGNE
                self.score_x+=1
            self.ui.canvas_score.itemconfig(self.ui.texte_score,text=f"Score du joueur O : {self.score_o}      Score du joueur X : {self.score_x}",font=("Segoe UI",15,"bold"))
    
    def maj_plateau(self,joueur,image,x,y,icone):
        """Méthode qui met à jour le plateau (à la fois l'ui et la matrice) en fonction de la case coché"""
        self.ui.window.config(cursor=icone) 
        self.ui.ui_plateau.create_image(self.cords[y][x][1],self.cords[y][x][0], image = image,anchor="center")
        self.matrice_plateau[y][x]=joueur
    
    @staticmethod
    def calcul_coords_case(x,y):
        """Permet de retourner les coordonnées où il faut poser le symbole sur le plateau à partir des coords du clic"""
        x = math.floor(x/100)            
        y = math.floor(y/50) if y<600 else 11 
        return x,y

    def action(self,eventorigin):
        """Fonction qui gère lorsqu'une case est cliquée : 
        Le clic est détecté par eventorigin et avec les coordonnées enregistrés, le symbole correspondant va être coché sur la 
        case cliqué. Elle gère l'alternance des tours entre les 2 joueurs et contient la fenêtre de fin de partie."""
        try : 
            if 1<=self.compteur_tour<=144 or self.state==State.PARTIE_LANCEE:
                x,y=Jeu.calcul_coords_case(eventorigin.x,eventorigin.y)
                if self.compteur_tour%2!=0 and self.matrice_plateau[y][x]==0 and self.state==State.PARTIE_LANCEE:   #quand la partie est fini, state n'est plus égal à 1 donc aucun autre tour ne doit être joué en plus
                    self.maj_plateau(1,self.ui.image_1,x,y,"cross")
                    self.cond_victoire(1,y,x)
                elif self.compteur_tour%2==0 and self.matrice_plateau[y][x]==0 and self.state==State.PARTIE_LANCEE:
                    self.maj_plateau(2,self.ui.image_2,x,y,"circle")
                    self.cond_victoire(2,y,x)
                else:
                    self.compteur_tour-=1             #si le mec clique n'importe comment sur une case déjà cliqué, ça passe pas son tour yk ?
                if self.compteur_tour==144 and self.state==State.PARTIE_LANCEE:
                    self.state=State.MATCH_NUL
                    self.compteur_tour=0
                self.compteur_tour+=1
                if self.state!=State.PARTIE_LANCEE: #La partie a été lancé donc state!=0, si state!=1 alors la partie est terminée (match_nul, O_win ou X_win)
                    self.ui.ecran_fin()
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode action : {e}')  

class Graphiques():
    def __init__(self,jeu):
        """Initialise les éléments à utiliser qui ne vont jamais changer d'état, ni disparaître tant que le jeu n'est pas fermé"""
        self.window=tk.Tk()
        self.jeu=jeu
        try : 
            self.image_1 = tk.PhotoImage(file="cercle.png").subsample(2,2)  
            self.image_2 = tk.PhotoImage(file="croix.png").subsample(2,2)
        except :
            print ('Image de symboles non trouvée')
    
    def creer_bouton(self,nom_frame,width_bouton,height_bouton,bg_couleur,bg_highlight_couleur,evenement,x,y,texte):
        bouton=tk.Canvas(nom_frame,width=width_bouton,height=height_bouton,bg=bg_couleur,highlightbackground=bg_highlight_couleur)
        bouton.bind("<Button-1>",lambda event:evenement())
        bouton.create_text(x,y, text=texte,font=("Segoe UI",20,"bold"),fill="white")
        return bouton

    def setup_gui(self):
        """Initialise tous les éléments à utiliser sur Tkinter : fenêtre, Canvas, Frames et image de fond."""
        self.window.geometry("1500x1000")
        try : 
            image_test = Image.open("bg.png")
        except :
            raise Exception ('image de fond non trouvée')
        image_test = image_test.resize((1500, 1000), Image.Resampling.LANCZOS)  #Pour que l'image remplisse la fenêtre
        self.bg_img = ImageTk.PhotoImage(image_test) 
        self.frame_debut=tk.Frame(self.window,width=1500,height=1000)
        self.contenu_frame_debut=tk.Canvas(self.frame_debut,width=1500,height=1000)
        self.frame_plateau=tk.Frame(self.window,width=1500,height=1000)
        self.contenu_frame_plateau=tk.Canvas(self.frame_plateau,width=1500,height=1000)
        self.titre_jeu=tk.Canvas(self.contenu_frame_plateau,width=1200,height=100,bg="royalblue",highlightbackground="royalblue")
        self.canvas_score=tk.Canvas(self.contenu_frame_plateau,width=1200,height=60,bg="cornflowerblue",highlightbackground="cornflowerblue")
        self.texte_score=self.canvas_score.create_text(600,30,text=f"Score du joueur O : {self.jeu.score_o}      Score du joueur X : {self.jeu.score_x}",font=("Segoe UI",20), fill="white")
        self.ui_plateau=tk.Canvas(self.contenu_frame_plateau,width=1200,height=600,bg="lightsteelblue3",highlightbackground="royalblue4")
        self.frame_end=tk.Frame(self.window,width=1500,height=1000)
        self.contenu_frame_end=tk.Canvas(self.frame_end,width=1500,height=1000)

    def pack_board(self, event=None):
        """Fait la transition entre le menu de début et le plateau sur la même fenêtre en détruisant les éléments du title screen."""
        try :
            if self.jeu.state==State.NON_LANCEE:
                self.frame_debut.destroy()
                self.jeu.state=State.PARTIE_LANCEE
            self.titre_jeu.pack(side=tk.TOP,pady=(10,0))
            self.canvas_score.pack()
            self.ui_plateau.bind("<Button-1>", self.jeu.action)
            self.ui_plateau.pack(side=tk.BOTTOM,pady=5,padx=150)
            self.contenu_frame_plateau.pack()
            self.frame_plateau.pack()
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode pack_board : {e}')  

    def ecran_debut(self):
        """Construit l'écran de début lorsque le jeu est lancé, fais donc office de title screen. Initialise aussi les éléments
        du plateau mais ne les affiche pas encore (comme une commande préparée mais pas encore envoyée)"""
        try :
            self.contenu_frame_debut.create_image(0, 0, image=self.bg_img, anchor="nw")
            self.contenu_frame_debut.create_text(750,20, text="fait par TheM00NCAKE (on s'en fou je sais)",font=("Segoe UI",10,"bold"))
            self.contenu_frame_debut.create_text(750, 270,text="Bienvenue sur ce jeu de con : \n\n\n\n Le Morpion X5", font=("Segoe UI",40,"bold"),justify="center")
            self.contenu_frame_debut.create_text(750, 500,text="(version très bêta)", font=("Segoe UI",10),)
            ###########"esthétique du plateau après avoir lancé Start boutton###########
            self.contenu_frame_plateau.create_image(0, 0, image=self.bg_img, anchor="nw")
            self.titre_jeu.create_text(600,50,text="Le morpion X5",font=("Segoe UI",30,"bold"), justify="center",fill="white")
            for i in range (50,600,50):
                self.ui_plateau.create_line(0,i,1200,i,fill="dodgerblue4")
            for i in range (100,1200,100):
                self.ui_plateau.create_line(i,0,i,1200,fill="dodgerblue4")
            self.window.config(cursor="circle") #le curseur a une forme de cercle
            self.bouton_start=self.creer_bouton(self.frame_debut,200,50,"deepskyblue3","deepskyblue4",self.pack_board,100,25,"Start")
            self.bouton_quit=self.creer_bouton(self.frame_debut,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit")
            ##################################################################
            if self.jeu.state==State.NON_LANCEE:
                self.contenu_frame_debut.pack()
                self.bouton_start.place(relx=0.4, rely=0.85, anchor="center")
                self.bouton_quit.place(relx=0.6, rely=0.85, anchor="center")
                self.frame_debut.pack()
                self.window.mainloop()
            else:
                self.pack_board()
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode ecran_debut : {e}')  

    def ecran_fin(self):
        """Fais office d'écran de fin d'une partie avec un message qui désigne le gagnant, ou si c'est un match nul"""
        try :
            self.frame_plateau.destroy()
            #nb pour moi : highlightbackground c'est pour les marges entre les canvas qui sont blanches :)
            self.contenu_frame_end.create_image(0, 0, image=self.bg_img, anchor="nw")
            message=('Match nul, dommage...' if self.jeu.state==State.MATCH_NUL else f'Victoire du joueur {"O" if self.jeu.state==State.O_GAGNE else "X"}')
            self.contenu_frame_end.create_text(750,300, text=message, font=("Segoe UI",30,"bold"),justify="center")
            self.contenu_frame_end.pack()
            self.bouton_replay=self.creer_bouton(self.frame_end,200,50,"deepskyblue3","deepskyblue4",lambda:[self.frame_end.destroy(),self.jeu.jeu()],100,25,"Replay")
            self.bouton_quit=self.creer_bouton(self.frame_end,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit")
            self.bouton_replay.place(relx=0.4, rely=0.65, anchor="center")
            self.bouton_quit.place(relx=0.6, rely=0.65, anchor="center")
            self.frame_end.pack()
            self.jeu.state=State.PARTIE_LANCEE
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode ecran_fin : {e}')  
        
    def process_jeu(self):
        """S'occupe d'éxecuter les méthodes nécessaire pour lancer le jeu une première fois"""
        self.setup_gui()
        self.jeu.matrice_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.ecran_debut()

game=Jeu()
game.jeu()