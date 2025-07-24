import tkinter as tk
import math
import time
#les states servent à communiquer les différentes phases au cours du jeu
state=0      #state 0 : le jeu ne se lance pas
compteur=1   #nombre de tour par défaut, c'est à dire 1. Le maximum est 9
scoreO=0
scoreX=0
def jeu():
    global state, compteur
    if state!=1 :       #signifie que le jeu a été activé pour la première fois
        introduction()
    if state==1:        #state 1 : le jeu peut commencer si le joueur a choisi de vouloir jouer
        plateau()
    return state
     
def introduction():
    global state
    intro=input("Bonjour, ceci est un jeu de morpion standard qui n'est pas censé voir le jour, ceci est simplement un exercice pour remettre à jour les vieilles connaissances (et aussi parce que je m'ennuie mdr), peut importe... Veux tu commencer une partie ? \nOui : 1\nNon : 2 \nréponse : ")
    if intro=="2":
        print("Très bien, au revoir !")
        state=0    
    elif intro!="2" and intro !="1":
        a=input("Il n'y a que 2 options, comment as-tu fais pour te tromper ? Aller, réassaye encore...  \nOui : 1 \nNon : 2 \nréponse : ")
        if a!="1" and a!="2":
            print ("Puisque c'est comme ça, au revoir.")
        elif a=="2":
            print("Très bien, à bientôt j'espère.")
        else:
            introduction()     #redonne une chance au joueur de refaire un choix de début
    else:
        print("D'accord ! Une fenêtre va apparaitre sur la barre des tâches.")
        state=1                  #state=1 signifie que le joueur veut jouer
    return state
        
def replay():
    global state
    s=input("veux tu rejouer ? \nOui : 1\nNon : n'importe quel autre touche\nréponse : ")
    if s=="1" :
        state=1
        jeu()
    else:
        print("Ok, j'espère que cela vous a plu, au revoir!")
    return state

def plateau():
    board_=[[0,0,0],[0,0,0],[0,0,0]]    #au début de partie, le tableau est encore vide, donc les cases n'ont aucune valeur
    def cond_victoire(joueur):
        global state,compteur,scoreO,scoreX
        if (any(all(board_[i][j] == joueur for j in range(3)) for i in range(3)) or any(all(board_[i][j] == joueur for i in range(3)) for j in range(3)) or all(board_[i][i] == joueur for i in range(3)) or all(board_[i][2 - i] == joueur for i in range(3))):  
            etat.itemconfig(texte,text=f"   Victoire du joueur {'O' if joueur==1 else 'X'}! \nLa fenêtre va se fermer dans 3s", font=("Arial",30))
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
            image1 = tk.PhotoImage(file="cercle.png")  #icone affiché sur le morpion : img1 représente le joueur O et img2 le joueur X
            image2 = tk.PhotoImage(file="croix.png")
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
                etat.itemconfig(texte,text="Match nul, dommage... \nLa fenêtre va se fermer dans 3s", font=("Arial",30))
                state="Match_nul"
            compteur+=1
            if state!=1:
                window.after(3000, lambda: [window.destroy(), replay()])
            window.mainloop()
            
    window=tk.Tk()                            #mon plateau morpion et mon canvas avec les grilles
    window.geometry("900x800")
    etat=tk.Canvas(window,width=900,height=100,bg="dim gray")
    score=tk.Canvas(window,width=900,height=60,bg="light gray")
    etat.pack(side=tk.TOP)
    score.pack()
    texte=etat.create_text(450,50,text="Le morpion standard",font=("Arial", 30), justify="center")
    TexteScore=score.create_text(450,30,text=f"Score du joueur O : {scoreO}      Score du joueur X : {scoreX}",font=("Arial", 15))
    board=tk.Canvas(window,width=900,height=600,bg="grey")
    board.create_line(0,200,900,200,fill="black")
    board.create_line(0,400,900,400,fill="black")
    board.create_line(300,0,300,900,fill="black")
    board.create_line(600,0,600,900,fill="black")
    board.bind("<Button-1>", action)
    board.pack(side=tk.BOTTOM,pady=10)
    window.config(cursor="circle") #le curseur a une forme de cercle
    window.mainloop()
jeu()