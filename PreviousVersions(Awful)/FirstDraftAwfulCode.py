import tkinter as tk
import math
#les states servent à communiquer les différentes phases au cours du jeu
state=0     #state 0 : le jeu ne se lance pas
compteur=1   #nombre de tour par défaut, c'est à dire 1. Le maximum est 9
scoreO=0
scoreX=0
#Ma fenêtre qui va servir à tout afficher
window=tk.Tk()                            
window.geometry("900x800")
def jeu():
    global state, compteur
    if state==1 or state==0:        #state 1 : le jeu peut commencer si le joueur a choisi de vouloir jouer
        plateau()
    else:
        raise Exception("what ??????")
    return state

def plateau():
    global state, compteur
    board_=[[0,0,0],[0,0,0],[0,0,0]]    #au début de partie, le tableau est encore vide, donc les cases n'ont aucune valeur
    def cond_victoire(joueur):
        global state,compteur,scoreO,scoreX
        if (any(all(board_[i][j] == joueur for j in range(3)) for i in range(3)) or any(all(board_[i][j] == joueur for i in range(3)) for j in range(3)) or all(board_[i][i] == joueur for i in range(3)) or all(board_[i][2 - i] == joueur for i in range(3))):  
            compteur=0      #le compteur de cases rempli se remet à 0 car la partie est terminée (se prépare en cas de nouvelle partie)
            if joueur==1:
                state="O_win"  
                scoreO+=1
            else :
                state="X_win"
                scoreX+=1
            score.itemconfig(TexteScore,text=f"Score du joueur O : {scoreO}      Score du joueur X : {scoreX}",font=("Arial", 15))

    def action(eventorigin):
        global state,compteur,scoreO,scoreX
        if 1<=compteur<=9 or state==1:
            cords=[[[145,100],[145,300],[145,500]],[[450,100],[450,300],[450,500]],[[750,100],[750,300],[750,500]]]  #coordonnées des centres des cases, ce sera pour placer les images de cercles et de croix
            image1 = tk.PhotoImage(file="images/cercle.png")  #icone affiché sur le morpion : img1 représente le joueur O et img2 le joueur X
            image2 = tk.PhotoImage(file="images/croix.png")
            x = math.floor(eventorigin.x/300)  #x et y se calcule en fonction de la position de la souris, les valeurs sont arrondis au dessous          
            y = math.floor(eventorigin.y/200)  #et vont déterminer les cases à cocher sur le plateau
            if compteur%2!=0 and board_[x][y]==0 and state==1:   #quand la partie est fini, state n'est plus égal à 1 donc aucun autre tour ne doit être joué en plus
                window.config(cursor="cross")  #le curseur devient une croix quand c'est le tour du joueur X
                board.create_image(cords[x][y][0],cords[x][y][1], image = image1,anchor="center")
                board_[x][y]=1
                cond_victoire(1)
            elif compteur%2==0 and board_[x][y]==0 and state==1:
                window.config(cursor="circle")
                board.create_image(cords[x][y][0],cords[x][y][1], image = image2,anchor="center")
                board_[x][y]=2
                cond_victoire(2)
            else:
                compteur-=1             #si le mec clique n'importe comment sur une case déjà cliqué, ça passe pas son tour yk ?
            if compteur==9 and state==1:
                state="Match_nul"
                compteur=0
            compteur+=1
            if state!=1: #state ne peut pas être à 0, donc si state!=1, la partie est terminée (match_nul, O_win ou X_win)
                TheBoard.destroy()
                zone_end=tk.Frame(window,width=600,height=400,bg="purple")
                #highlightbackground c'est pour les marges entre les canvas qui sont blanches :)
                test=tk.Canvas(zone_end,width=600,height=200,bg="purple",highlightbackground="purple")
                message=('Match nul, dommage...' if state=='Match_nul' else f'Victoire du joueur {"O" if state=="O_win" else "X"}')
                test.create_text(300,100, text=message, font=("Arial",30),justify="center")
                bstart=tk.Canvas(zone_end,width=200, height=50,bg="green", highlightbackground="purple")
                bstart.bind("<Button-1>",lambda event:[zone_end.destroy(),jeu()])
                bstart.create_text(100,25, text="Replay",font=("Arial", 20))
                bend=tk.Canvas(zone_end,width=200,height=50,bg="red", highlightbackground="purple")
                bend.create_text(100,25,text="Quit",justify="center",font=("Arial",20))
                bend.bind("<Button-1>",lambda event: window.destroy())
                test.pack()
                bstart.pack(side=tk.BOTTOM)
                bend.pack(side=tk.BOTTOM)
                zone_end.pack(pady=200)
                #On revient sur la state de début de partie, mais les scores sont pris en compte
                state=1
            window.mainloop()

    def PackBoard(x, event=None):
        global state
        if x==1:
            zone_debut.destroy()
        state=1
        etat.pack(side=tk.TOP)
        score.pack()
        board.bind("<Button-1>", action)
        board.pack(side=tk.BOTTOM,pady=10)
        TheBoard.pack()
    zone_debut=tk.Frame(window,width=900,height=800)
    debut=tk.Canvas(zone_debut,width=900,height=500, bg='light grey')
    debut.create_text(450, 250,text="Bienvenue sur ce jeu de con", font=("Arial",30),justify="center")
    #esthétique du plateau après avoir lancé Start boutton
    TheBoard=tk.Frame(window,width=900,height=600)
    etat=tk.Canvas(TheBoard,width=900,height=100,bg="dim gray")
    score=tk.Canvas(TheBoard,width=900,height=60,bg="light gray")
    etat.create_text(450,50,text="Le morpion standard",font=("Arial", 30), justify="center",fill="white")
    TexteScore=score.create_text(450,30,text=f"Score du joueur O : {scoreO}      Score du joueur X : {scoreX}",font=("Arial", 15))
    board=tk.Canvas(TheBoard,width=900,height=600,bg="grey")
    board.create_line(0,200,900,200,fill="black")
    board.create_line(0,400,900,400,fill="black")
    board.create_line(300,0,300,900,fill="black")
    board.create_line(600,0,600,900,fill="black")
    window.config(cursor="circle") #le curseur a une forme de cercle
    bstart=tk.Canvas(zone_debut,width=200, height=50,bg="green")
    bstart.bind("<Button-1>",lambda event: PackBoard(1))
    bstart.create_text(100,25, text="Start",font=("Arial", 20))
    bend=tk.Canvas(zone_debut,width=200,height=50,bg="red")
    bend.create_text(100,25,text="Quit",justify="center",font=("Arial",20))
    bend.bind("<Button-1>",lambda event: window.destroy())
    if state==0:
        debut.pack(pady=50)
        bstart.pack(side=tk.BOTTOM)
        bend.pack(side=tk.BOTTOM)
        zone_debut.pack()
        window.mainloop()
    else:
        PackBoard(0)
jeu()