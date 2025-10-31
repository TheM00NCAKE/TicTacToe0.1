import tkinter as tk
import math
from PIL import Image, ImageTk,ImageOps,ImageColor
from enum import Enum
import random

class Etat(Enum):
    """Permet à attribuer des valeurs à Jeu.etat de façon plus lisible"""
    NON_LANCEE=0
    PARTIE_LANCEE=1
    ITEM_JOUER=2
    PAS_JOUER_ITEM=3 
    RECLIQUE=4
    O_GAGNE=5
    X_GAGNE=6
    MATCH_NUL=7

class Item():
    @staticmethod
    def item_jouable_ou_pas(jeu):
        """Retourne un booléen en fonction de si l'item qui interdit l'usage d'item sur 2 tour a été utilisé et est actif"""
        return jeu.etat != Etat.PAS_JOUER_ITEM
    
    @staticmethod
    def case_protege_ou_pas(jeu,x,y):
        return [y,x] in jeu.liste_case_proteges
    
    @staticmethod
    def case_reserve_action(joueur,jeu,x,y,position,tour): 
        """Réserve une case pour le joueur actif (l'autre ne peut pas poser son symbole dessus)"""
        if Item.item_jouable_ou_pas(jeu):
            joueur.tour_actuel=tour
            if jeu.matrice_plateau[y][x]==0:
                jeu.maj_plateau(joueur.valeur_case,joueur.barricade,x,y)
                jeu.matrice_plateau[y][x]=joueur.reserve_val
                jeu.ui.cancel_button.pack_forget()
                Joueur.terminer_item(joueur, jeu, position,Etat.PARTIE_LANCEE)
            else :
                jeu.ui.ecrire_commentaire('Choisir une case vide')
                jeu.etat=Etat.RECLIQUE
                jeu.compteur_tour-=1
    
    @staticmethod
    def trans_case_action(joueur,jeu,image,x,y,position,tour): 
        """transforme une case adverse en la sienne"""
        if Item.item_jouable_ou_pas(jeu):
            joueur.tour_actuel=tour
            if jeu.matrice_plateau[y][x] in (0, joueur.valeur_case, 10,20) or Item.case_protege_ou_pas(jeu,x,y):
                jeu.ui.ecrire_commentaire('Clique sur une case déjà cliquée et non protégé appartenant à ton adversaire !')
                jeu.etat=Etat.RECLIQUE
                jeu.compteur_tour-=1
            else :
                jeu.ui.cancel_button.pack_forget()
                jeu.maj_plateau(joueur.valeur_case,image,x,y)
                jeu.maj_icone(joueur.curseur)
                Joueur.terminer_item(joueur, jeu, position,Etat.PARTIE_LANCEE)
        
    @staticmethod
    def proteger_case_action(joueur,jeu,x,y,position,tour):
        """Méthode pour choisir une case à protéger des items. Peut jouer après avoir utiliser l"item."""
        if Item.item_jouable_ou_pas(jeu):
            joueur.tour_actuel=tour
            if jeu.matrice_plateau[y][x]!=joueur.valeur_case or jeu.liste_case_proteges.count([y,x])>0 :
                jeu.ui.ecrire_commentaire("Protège une case qui t'appartiens et qui est déjà posée")
                jeu.etat=Etat.RECLIQUE
            else : 
                jeu.ui.cancel_button.pack_forget()
                jeu.liste_case_proteges.append([y,x])
                jeu.maj_plateau(joueur.valeur_case,joueur.item3,x,y)
                Joueur.terminer_item(joueur, jeu, position,Etat.PARTIE_LANCEE)
                jeu.ui.maj_inventaire_affiche(joueur)
            jeu.compteur_tour-=1

    def interdiction_item_action(joueur,jeu,position,tour):
        """Interdire de jouer quelconque item sur 2 tour de joueur (4 tours en tout)"""
        if Item.item_jouable_ou_pas(jeu):
            joueur.tour_actuel=tour
            jeu.tour_restant=4
            Joueur.terminer_item(joueur, jeu, position,Etat.PAS_JOUER_ITEM)

    @staticmethod
    def detruire_cases_action(joueur,jeu,x,y,position,tour):
        """Item pour détruire les cases avec une range de 2x2, ne peut pas poser une case après avoir joué l'item"""
        if Item.item_jouable_ou_pas(jeu):
            jeu.ui.cancel_button.pack(side=tk.LEFT,padx=11)
            if joueur.tour_actuel!=tour:
                jeu.ui.ui_plateau.unbind("<Button-1>")
                jeu.ui.ui_plateau.itemconfigure("overlay", state="normal")
                joueur.tour_actuel=tour
            else :
                jeu.ui.cancel_button.pack_forget()
                for i in range(x,x+2):
                    for j in range(y,y+2):
                        if not Item.case_protege_ou_pas(jeu,i,j):
                            jeu.ui.ui_plateau.delete(jeu.id_img_plateau[j][i])
                            jeu.matrice_plateau[j][i]=0
                jeu.clic_origine=''
                jeu.ui.ui_plateau.bind("<Button-1>",jeu.ui.qui_joue)
                Joueur.terminer_item(joueur, jeu, position,Etat.PARTIE_LANCEE)
                jeu.ui.ui_plateau.itemconfigure("overlay", state="hidden")
        
    @staticmethod
    def vole_item_action(joueur,jeu,joueur_a_voler,position,tour): 
        """Vole un item au hasard à l'autre joueur"""
        if Item.item_jouable_ou_pas(jeu):
            if len(joueur.inventaire)==5:
                jeu.ui.ecrire_commentaire("Inventaire déjà plein... L'item ne peut pas être utilisé")
                jeu.etat=Etat.PARTIE_LANCEE
            elif len(joueur_a_voler.inventaire)==0:
                jeu.ui.ecrire_commentaire("Inventaire de l'adversaire vide... L'item ne peut pas être utilisé")
                jeu.etat=Etat.PARTIE_LANCEE
            else : 
                joueur.tour_actuel=tour
                item_voler=random.randint(0,len(joueur_a_voler.inventaire)-1)
                joueur.inventaire.append(joueur_a_voler.inventaire[item_voler])
                joueur_a_voler.inventaire.pop(item_voler)
                Joueur.terminer_item(joueur, jeu, position,Etat.PARTIE_LANCEE)

class Joueur:

    def __init__(self,curseur,couleur,fichier,img_barricade,item2,item3,item4,item5,item6,couleur_plateau,couleur_inventaire):
        self.valeur_case=0
        self.reserve_val=self.valeur_case*10
        self.curseur=curseur
        self.inventaire=[]
        self.inventaire_item_id=[]
        self.peut_piocher=False
        self.tour_actuel=0
        self.item_jouer_pos=None
        self.couleur=couleur
        self.symbole = self.changer_clr_img(fichier,couleur_plateau,True)
        self.barricade=self.changer_clr_img(img_barricade,couleur_plateau,True)
        self.item2=self.changer_clr_img(item2,couleur_inventaire,False)
        self.item3=self.changer_clr_img(item3,couleur_plateau,True)
        self.item4=self.changer_clr_img(item4,couleur_inventaire,False)
        self.item5=self.changer_clr_img(item5,couleur_inventaire,False)
        self.item6=self.changer_clr_img(item6,couleur_inventaire,False)
        self.liste=[self.barricade,self.item2,self.item3,self.item4,self.item5,self.item6]

    def update_val_joueur(self,valeur):
        self.valeur_case=valeur

    def liste_items(self,jeu):
        """A changer le nom de la méthode : retourne un indice au hasard qui correspond à un item"""
        indice=random.randint(0,5)
        self.inventaire.append(indice)
        x,y=jeu.inventaire_cords[len(self.inventaire)-1]
        return self.liste[indice],x,y
    
    def changer_clr_img(self,fichier,couleur_plateau,state):
        """Changer les couleurs d'une img png et le redimensioner (à changer, parce que des png c moche quand même)"""
        rgb_bg=ImageColor.getrgb(couleur_plateau)
        if state==True:
            rgb_clr=ImageColor.getrgb(self.couleur)
            img=Image.open(fichier).convert("L")  #la luminosité, donc de noir à blanc (l'img est en noir et blanc)
            clr_img=ImageOps.colorize(img, black=rgb_clr, white=rgb_bg)
        else : 
            clr_img=Image.open(fichier)
            pixels=list(clr_img.getdata())
            px_modifie=[rgb_bg+(a,) if (r,g,b)==(255,255,255) else(r,g,b,a)  for(r,g,b,a) in pixels]
            clr_img.putdata(px_modifie)
        clr_img=clr_img.resize((clr_img.width//2, clr_img.height//2), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(clr_img)

    @staticmethod
    def terminer_item(joueur, jeu, position,etat_choisi):
        """effectue les dernières actions après avoir joué un item (supprimer l'item de l'inventaire, et reset la pos)"""
        joueur.inventaire.pop(position)
        joueur.item_jouer_pos=None
        jeu.etat=etat_choisi
    
    @staticmethod
    def annuler_item(joueur, jeu):
        """s'execute quand cancel est appuyé : reset l'état du joueur, et annule l'usage de l'item"""
        jeu.ui.cancel_button.pack_forget()
        if jeu.ui.ui_plateau.itemcget('overlay','state')=='normal':
            jeu.ui.ui_plateau.itemconfigure('overlay',state='hidden')
            jeu.ui.ui_plateau.bind("<Button-1>",jeu.ui.qui_joue)
        joueur.item_jouer_pos=None
        joueur.tour_actuel=-1
        jeu.etat=Etat.PARTIE_LANCEE

    @staticmethod
    def gestion_gameplay_item(joueur,jeu,x):
        """A renforcer parce que ça pue la merde pour l'instant, but gere les items (certains, for some reasons) OUI OK A CHANGER"""
        if joueur.tour_actuel==jeu.compteur_tour:
            jeu.ui.ecrire_commentaire('1 item par tour !')
            joueur.item_jouer_pos=None
        elif jeu.etat==Etat.PARTIE_LANCEE:
            if len(joueur.inventaire)>=x+1:
                joueur.item_jouer_pos=x
                jeu.etat=Etat.ITEM_JOUER
                if joueur.inventaire[joueur.item_jouer_pos]>2:
                    case_x,case_y=jeu.inventaire_cords[joueur.item_jouer_pos]
                    joueur.jouer_item(x,jeu,case_x,case_y,jeu.compteur_tour)
                else : 
                    jeu.ui.cancel_button.pack(side=tk.LEFT,padx=11)
            else:
                jeu.ui.ecrire_commentaire('Case sans objet')
        elif jeu.etat==Etat.PAS_JOUER_ITEM : 
            jeu.ui.ecrire_commentaire(f"Interdiction d'utiliser quelconque item pour encore {jeu.tour_restant} tour(s)")

    def pioche(self,jeu):
        """Gere l'action piocher du jeu"""
        if self.peut_piocher:
            if len(self.inventaire)<5:
                item_choisi,x,y=self.liste_items(jeu)
                id_item=jeu.ui.inventaire_jeu.create_image(x,y,image=item_choisi,tags="texte_inventaire")
                self.inventaire_item_id.append(id_item)
                jeu.ui.window.after(500, lambda : jeu.ui.qui_joue(None))
                self.peut_piocher=False
            else:
                jeu.ui.ecrire_commentaire('Inventaire déjà plein !')
        else : 
            jeu.ui.ecrire_commentaire('Peux uniquement piocher après avoir posé un symbole')
    
    def jouer_item(self,position,jeu,x,y,tour):
        """utilise match case pour gérer l'actionnement des items"""
        assert isinstance(position, int) and 0<=position<len(self.inventaire), "Item non existant dans l'inventaire"
        if tour!=self.tour_actuel:
            match self.inventaire[position]:
                case 0 :
                    Item.case_reserve_action(self,jeu, x, y,position,tour)
                case 1 : 
                    Item.trans_case_action(self,jeu,self.symbole,x,y,position,tour)
                case 2 :
                    Item.proteger_case_action(self,jeu,x,y,position,tour) 
                case 3 : 
                    Item.interdiction_item_action(self,jeu,position,tour)
                case 4 : 
                    Item.detruire_cases_action(self,jeu,x,y,position,tour) 
                case 5 :
                    Item.vole_item_action(self,jeu,jeu.ui.joueur_2 if self.valeur_case==1 else jeu.ui.joueur_1,position,tour)

class Jeu : 
    def __init__(self):
        """Constructeur qui va initier les attributs essentiels. matrice_plateau évolue en fonction de l'état de la partie, 
        chaque liste représentant une ligne et chaque élément une case : 0=case vide, 1=joueur O a coché la case, 2=joueur X"""
        self.etat=Etat.NON_LANCEE  
        self.compteur_tour=1   
        self.score_o=0
        self.score_x=0
        self.matrice_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]    
        self.id_img_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.liste_case_proteges=[]
        self.cords=[[[(r-25),i-50] for i in range (100,1300,100)] for r in range (50,700,50)]   
        self.inventaire_cords=[[i,50]for i in range (55, 560,110)] 
        self.tour_restant=0
        self.clic_origine='plateau'
        self.ui=Graphiques(self)            

    def jeu(self):
        """Méthode qui fait démarrer le jeu"""
        if self.etat==Etat.NON_LANCEE or self.etat==Etat.PARTIE_LANCEE:      
            self.ui.process_jeu(joueur_x,joueur_o) #ici on décide de qui commence le premier 
    
    def changer_etat(self,etat):
        """pas encore utilisé, pretty useless so far parce que je le fais en dur dans le code..."""
        self.etat=etat
    
    @staticmethod
    def verif(val1,val2):
        """vérifie si le calcul dépasse l'indice de plateau ou non"""
        return 0<=val1<=11 and 0<=val2<=11

    def cond_victoire(self,joueur,num_ligne,num_colonne):
        """Vérifie si un joueur a réuni les conditions de victoire ou non. Elle récupère les coordonnées de la dernière case
        cochée et vérifie autour de cette case (horizontalement, verticalement et diagonalement) si 5 cases à la suite ont les 
        mêmes valeurs (1 ou 2 selon le joueur) et va permettre de générer un message indiquant que {joueur} a gagné"""
        verif_verticale=any(all(self.matrice_plateau[i+r][num_colonne]==joueur.valeur_case for i in range (5)) for r in range (8)) 
        verif_horizontale=any(all(self.matrice_plateau[num_ligne][i+r]==joueur.valeur_case for i in range (5)) for r in range (8))
        verif_diag_droit=any(all(Jeu.verif(num_ligne+i+r,num_colonne+i+r) and 
            self.matrice_plateau[num_ligne+i+r][num_colonne+i+r]==joueur.valeur_case for i in range(-4,1)) for r in range (8))
        verif_diag_gauche=any(all(Jeu.verif(num_ligne+i+r,num_colonne-i-r) and 
            self.matrice_plateau[num_ligne+i+r][num_colonne-i-r]==joueur.valeur_case for i in range(-4,1)) for r in range (8))
        if verif_verticale or verif_horizontale or verif_diag_droit or verif_diag_gauche:
            self.compteur_tour=0      #le compteur de cases rempli se remet à 0 (+1) car la partie est terminée (se prépare en cas de nouvelle partie)
            if joueur.curseur=='circle':
                self.etat=Etat.O_GAGNE
                self.score_o+=1
            else :
                self.etat=Etat.X_GAGNE
                self.score_x+=1
            self.ui.canvas_score.itemconfig(self.ui.texte_score,text=f"Score du joueur O : {self.score_o}      Score du joueur X : {self.score_x}",font=("Segoe UI",15,"bold"))
    
    def maj_icone(self,icone):
        self.ui.window.config(cursor=icone) 

    def verif_tour_restant(self):
        """spécifique à l'item 4 et compte le nombre de tour restant interdisant l'usage d'item"""
        if self.tour_restant>=1:
            self.tour_restant-=1
            if self.tour_restant==0 : 
                self.etat=Etat.PARTIE_LANCEE 

    def maj_plateau(self,joueur,image,x,y):
        """Méthode qui met à jour le plateau (à la fois l'ui et la matrice) en fonction de la case coché"""
        if self.id_img_plateau[y][x]!=0 and self.liste_case_proteges.count([y,x])==0:
            self.ui.ui_plateau.delete(self.id_img_plateau[y][x])
        image_id=self.ui.ui_plateau.create_image(self.cords[y][x][1],self.cords[y][x][0], image = image,anchor="center")
        self.id_img_plateau[y][x]=image_id
        self.matrice_plateau[y][x]=joueur
    
    def calcul_coords_case(self,x,y):
        """Permet de retourner les coordonnées où il faut poser le symbole sur le plateau à partir des coords du clic"""
        if self.clic_origine in ("plateau","reclique","overlay_item") :
            if self.clic_origine=="overlay_item":
                x-=20
                y-=20
            x = math.floor(x/100)            
            y = math.floor(y/50) if y<600 else 11 
        else:
            x = math.floor(x/110)
            y = 50
        return x,y
    
    def action_poser_case(self,joueur_actuel,x,y,joueur_suivant):
        """gère l'action du joueur lorsqu'il interragit avec le plateau : soit il pose un symbole, soit un joue un item sur le plateau,
        soit il a missclick et on cancel son action"""
        if self.matrice_plateau[y][x] in (0,joueur_actuel.reserve_val):
            if self.etat in (Etat.PARTIE_LANCEE, Etat.PAS_JOUER_ITEM):                          
                self.maj_plateau(joueur_actuel.valeur_case,joueur_actuel.symbole,x,y)
                joueur_actuel.peut_piocher=True
            elif self.etat==Etat.ITEM_JOUER and joueur_actuel.item_jouer_pos is not None :
                joueur_actuel.jouer_item(joueur_actuel.item_jouer_pos,self,x,y,self.compteur_tour)
                joueur_actuel.peut_piocher=True
            if self.etat!=Etat.RECLIQUE:
                self.ui.maj_inventaire_affiche(joueur_suivant)
                self.maj_icone(joueur_suivant.curseur)
        elif self.etat==Etat.ITEM_JOUER and joueur_actuel.item_jouer_pos is not None :
            if joueur_actuel.inventaire[joueur_actuel.item_jouer_pos]==1:   
                joueur_actuel.jouer_item(joueur_actuel.item_jouer_pos,self,x,y,self.compteur_tour) 
                if self.etat!=Etat.RECLIQUE:
                    self.ui.maj_inventaire_affiche(joueur_suivant)
                    self.maj_icone(joueur_suivant.curseur)
            elif joueur_actuel.inventaire[joueur_actuel.item_jouer_pos] in (0,2):   
                joueur_actuel.jouer_item(joueur_actuel.item_jouer_pos,self,x,y,self.compteur_tour) 
        else : 
            self.compteur_tour-=1             #clic sur une case déjà utilisée
        self.cond_victoire(joueur_actuel,y,x) 
        self.verif_tour_restant()  

    def action(self,eventorigin,joueur_actuel,joueur_suivant):
        """Méthode qui gère la succession des actions du jeu (calcul des coordonnées des cases cliqués, maj du plateau et de l'inventaire,
        gestion de l'utilisation des items etc)"""
        try : 
            if self.clic_origine=='pioche':
                self.compteur_tour+=1
                self.ui.maj_inventaire_affiche(joueur_suivant)
                self.maj_icone(joueur_suivant.curseur) 
                self.verif_tour_restant()
            elif 1<=self.compteur_tour<=144 or self.etat in (Etat.PARTIE_LANCEE,Etat.RECLIQUE) :
                x,y=self.calcul_coords_case(eventorigin.x,eventorigin.y)
                if self.etat==Etat.RECLIQUE:
                    if joueur_actuel.inventaire[joueur_actuel.item_jouer_pos]==0:
                        Item.case_reserve_action(joueur_actuel,self,x,y,joueur_actuel.item_jouer_pos,self.compteur_tour)
                    elif joueur_actuel.inventaire[joueur_actuel.item_jouer_pos]==1:
                        Item.trans_case_action(joueur_actuel,self,joueur_actuel.symbole,x,y,joueur_actuel.item_jouer_pos,self.compteur_tour)
                    else :
                        Item.proteger_case_action(joueur_actuel,self,x,y,joueur_actuel.item_jouer_pos,self.compteur_tour)
                    self.compteur_tour+=1
                    if self.compteur_tour!=joueur_actuel.tour_actuel:
                        self.ui.maj_inventaire_affiche(joueur_suivant)
                        self.maj_icone(joueur_suivant.curseur)
                        self.cond_victoire(joueur_actuel,y,x)
                elif self.clic_origine=='overlay_item':
                    Item.detruire_cases_action(joueur_actuel,self,x,y,joueur_actuel.item_jouer_pos,self.compteur_tour)
                    self.ui.maj_inventaire_affiche(joueur_suivant)
                elif self.clic_origine=="plateau":
                    self.action_poser_case(joueur_actuel,x,y,joueur_suivant)
                    if not(any(0 in ligne for ligne in self.matrice_plateau)) and self.etat in (Etat.PARTIE_LANCEE,Etat.PAS_JOUER_ITEM,Etat.ITEM_JOUER):
                        self.etat=Etat.MATCH_NUL
                        self.compteur_tour=0
                    self.compteur_tour+=1
                else: #si clic_origine='inventaire'
                    Joueur.gestion_gameplay_item(joueur_actuel,self,x)    
                    self.ui.maj_inventaire_affiche(joueur_actuel) 
                if self.etat in (Etat.O_GAGNE,Etat.X_GAGNE,Etat.MATCH_NUL): 
                    self.ui.joueur_1.inventaire.clear()
                    self.ui.joueur_1.inventaire_item_id.clear()
                    self.ui.joueur_2.inventaire.clear()
                    self.ui.joueur_2.inventaire_item_id.clear()
                    self.liste_case_proteges.clear()
                    self.ui.ecran_fin()   
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode action : {e}')  

class Graphiques():
    def __init__(self,jeu):
        """Initialise les éléments à utiliser qui ne vont jamais changer d'état, ni disparaître tant que le jeu n'est pas fermé"""
        self.window=tk.Tk()
        self.jeu=jeu
    
    def creer_bouton(self,nom_frame,width_bouton,height_bouton,bg_couleur,bg_highlight_couleur,evenement,x,y,texte,rel_x,rel_y,val):
        """créer un bouton (merci captain obvious)"""
        bouton=tk.Canvas(nom_frame,width=width_bouton,height=height_bouton,bg=bg_couleur,highlightbackground=bg_highlight_couleur)
        bouton.bind("<Button-1>",lambda event:evenement())
        bouton.create_text(x,y, text=texte,font=("Segoe UI",20,"bold"),fill="white")
        if self.jeu.etat==Etat.NON_LANCEE or val==1 :
            bouton.place(relx=rel_x, rely=rel_y, anchor="center")
        return bouton

    def setup_gui(self,joueur,couleur_inventaire):
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
        self.canvas_commentaire=tk.Canvas(self.contenu_frame_plateau,width=100,height=300,bg=joueur.couleur)
        self.bg_menu_joueur_jeu=tk.Canvas(self.contenu_frame_plateau,width=1200,height=100,bg="royalblue",highlightbackground="white")
        self.frame_menu_joueur_jeu=tk.Frame(self.bg_menu_joueur_jeu,width=1200,height=100,bg='royalblue',highlightbackground="white")
        self.inventaire_jeu=tk.Canvas(self.frame_menu_joueur_jeu,width=546,height=100, bg=couleur_inventaire,highlightbackground='white')
        self.inventaire_jeu_bouttons=tk.Frame(self.frame_menu_joueur_jeu,width=600,height=100, bg="royalblue")
        self.draw_item_button=tk.Canvas(self.inventaire_jeu_bouttons,width=100,height=50,bg="dodgerblue1",highlightbackground="dodgerblue2")
        self.cancel_button=tk.Canvas(self.inventaire_jeu_bouttons,width=100,height=50,bg="indianred1",highlightbackground="indianred2")
        self.canvas_score=tk.Canvas(self.contenu_frame_plateau,width=1200,height=60,bg="cornflowerblue",highlightbackground="cornflowerblue")
        self.texte_score=self.canvas_score.create_text(600,30,text=f"Score du joueur O : {self.jeu.score_o}      Score du joueur X : {self.jeu.score_x}",font=("Segoe UI",20), fill="white")
        self.ui_plateau=tk.Canvas(self.contenu_frame_plateau,width=1200,height=600,bg=couleur_plateau,highlightbackground="royalblue4")
        self.frame_end=tk.Frame(self.window,width=1500,height=1000)
        self.contenu_frame_end=tk.Canvas(self.frame_end,width=1500,height=1000)

    def ecrire_commentaire(self,texte):
        """écris un commentaire sur le canvas à droite (moche)"""
        self.canvas_commentaire.create_text(50,150,text=texte,font=('Segoe UI',10),width=90)
        self.canvas_commentaire.after(1000, lambda:self.canvas_commentaire.delete('all'))

    def qui_joue(self,event):
        """détermine qui joue, et exécute la méthode action en fonction de ça"""
        if event==None:
            self.jeu.clic_origine='pioche'
        elif self.jeu.clic_origine=='':
            self.jeu.clic_origine='plateau'
            joueur_suivant=self.joueur_2 if self.jeu.compteur_tour%2!=0 else self.joueur_1
            self.jeu.compteur_tour+=1
            self.jeu.maj_icone(joueur_suivant.curseur)
            return
        else : 
            if event.widget == self.ui_plateau:
                canvas = event.widget 
                item = canvas.find_closest(event.x, event.y)
                tags = canvas.gettags(item)
                if 'overlay' in tags:
                    self.jeu.clic_origine='overlay_item'
                else :
                    self.jeu.clic_origine='plateau'
            elif event.widget == self.inventaire_jeu :
                self.jeu.clic_origine='inventaire_jeu'
        joueur_actuel=self.joueur_1 if self.jeu.compteur_tour%2!=0 else self.joueur_2
        joueur_suivant=self.joueur_2 if self.jeu.compteur_tour%2!=0 else self.joueur_1
        self.jeu.action(event,joueur_actuel,joueur_suivant)

    def pack_board(self, event=None):
        """Fait la transition entre le menu de début et le plateau sur la même fenêtre en détruisant les éléments du title screen."""
        try :
            if self.jeu.etat==Etat.NON_LANCEE:
                self.frame_debut.destroy()
                self.jeu.etat=Etat.PARTIE_LANCEE
            self.canvas_commentaire.place(x=1370,y=225)
            self.bg_menu_joueur_jeu.pack(side=tk.BOTTOM,pady=(0,5))
            self.frame_menu_joueur_jeu.pack()
            self.inventaire_jeu.bind("<Button-1>", self.qui_joue)
            self.inventaire_jeu.pack(side=tk.LEFT,padx=(0,15))
            self.inventaire_jeu_bouttons.pack(side=tk.LEFT,padx=15)
            self.draw_item_button.bind('<Button-1>',lambda event : self.joueur_1.pioche(self.jeu) if self.jeu.compteur_tour%2!=0 else self.joueur_2.pioche(self.jeu))
            self.draw_item_button.pack(side=tk.LEFT,padx=(0,11))
            self.cancel_button.bind('<Button-1>', lambda event : Joueur.annuler_item(self.joueur_1, self.jeu) if self.jeu.compteur_tour%2!=0 else Joueur.annuler_item(self.joueur_2, self.jeu))
            self.canvas_score.pack(pady=(5,0))
            self.ui_plateau.bind("<Button-1>", self.qui_joue)
            self.ui_plateau.pack(side=tk.BOTTOM,pady=5,padx=150)
            self.contenu_frame_plateau.pack()
            self.frame_plateau.pack()
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode pack_board : {e}')  

    def maj_inventaire_affiche(self,joueur):
        """met à jour le canvas inventaire pour actualiser l'inventaire lorsqu'un objet apparait ou est utilisé (à enlever)"""
        self.inventaire_jeu.delete("texte_inventaire")
        for i, item in enumerate (joueur.inventaire):
            x,y=self.jeu.inventaire_cords[i]
            self.jeu.ui.inventaire_jeu.create_image(x,y,image=joueur.liste[item],tags="texte_inventaire")
        self.jeu.ui.canvas_commentaire.config(bg=joueur.couleur)
    
    def menu_params(self):
        """template pour le menu, à ajouter des trucs parce que c très moche + changer les noms des variables"""
        self.frame_debut.pack_forget()
        contenu_global=tk.Frame(self.window,width=1500,height=1000)
        contenu_global.pack()
        can=tk.Canvas(contenu_global,width=1500,height=1000)
        can.pack()
        can.create_image(0, 0, image=self.bg_img, anchor="nw")
        params_contenu=tk.Canvas(contenu_global,width=1000,height=750,bg="grey")
        can.create_window(750, 400, window=params_contenu, anchor="center")
        bouton_quitter=self.creer_bouton(params_contenu,80,80,"red","deepskyblue4",lambda:[contenu_global.destroy(),self.frame_debut.pack()],42,40,"X",0.9,0.02,1)

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
            for i in range (110,660,110):
                self.inventaire_jeu.create_line(i,0,i,100,fill="black")
            self.draw_item_button.create_text(50,25,text="Draw item", font=('Segoe UI',10,'bold'))
            self.cancel_button.create_text(50,25,text="Annuler", font=('Segoe UI',10,'bold'))
            for i in range (50,600,50):
                self.ui_plateau.create_line(0,i,1200,i,fill="dodgerblue4")
            for i in range (100,1200,100):
                self.ui_plateau.create_line(i,0,i,1200,fill="dodgerblue4")
            rayon = 10 
            for i in range(50, 600, 50):    
                for j in range(100, 1200, 100): 
                    self.ui_plateau.create_oval(j-rayon,i-rayon,j+rayon,i+rayon,fill="red", tags='overlay')
            self.ui_plateau.tag_bind('overlay',"<Button-1>",self.qui_joue)
            self.ui_plateau.itemconfigure("overlay", state="hidden")
            self.window.config(cursor=self.joueur_1.curseur) 
            self.bouton_start=self.creer_bouton(self.frame_debut,200,50,"deepskyblue3","deepskyblue4",self.pack_board,100,25,"Start",0.5,0.85,0)
            self.bouton_quit=self.creer_bouton(self.frame_debut,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit",0.7,0.85,0)
            self.bouton_params=self.creer_bouton(self.frame_debut,200,50,"blue","purple",self.menu_params,100,25,"Paramètres",0.3,0.85,0)
            ##################################################################
            if self.jeu.etat==Etat.NON_LANCEE:
                self.contenu_frame_debut.pack()
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
            self.contenu_frame_end.create_image(0, 0, image=self.bg_img, anchor="nw")
            message=('Match nul, dommage...' if self.jeu.etat==Etat.MATCH_NUL else f'Victoire du joueur {"O" if self.jeu.etat==Etat.O_GAGNE else "X"}')
            self.contenu_frame_end.create_text(750,300, text=message, font=("Segoe UI",30,"bold"),justify="center")
            self.contenu_frame_end.pack()
            self.bouton_replay=self.creer_bouton(self.frame_end,200,50,"deepskyblue3","deepskyblue4",lambda:[self.jeu.changer_etat(Etat.PARTIE_LANCEE),self.frame_end.destroy(),self.jeu.jeu()],100,25,"Replay",0.5,0.65,1)
            self.bouton_quit=self.creer_bouton(self.frame_end,200,50,"royalblue3","royalblue4",self.window.destroy,100,25,"Quit",0.7,0.65,1)
            self.bouton_menu=self.creer_bouton(self.frame_end,200,50,"seagreen1","seagreen3",lambda:[self.jeu.changer_etat(Etat.NON_LANCEE),self.frame_end.destroy(),self.jeu.jeu()],100,25,"Menu",0.3,0.65,1)
            self.frame_end.pack()
        except Exception as e:
            print (f'Une erreur est survenue dans la méthode ecran_fin : {e}')  
        
    def process_jeu(self,joueur1,joueur2):
        """pretty straightforward right ?"""
        self.joueur_1=joueur1
        self.joueur_2=joueur2
        self.joueur_1.update_val_joueur(1)
        self.joueur_2.update_val_joueur(2)
        """S'occupe d'éxecuter les méthodes nécessaire pour lancer le jeu une première fois"""
        self.setup_gui(joueur1,couleur_inventaire) 
        self.jeu.matrice_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.jeu.id_img_plateau=[[0,0,0,0,0,0,0,0,0,0,0,0] for s in range (0,12)]
        self.ecran_debut()

couleur_plateau="#B9E1F4"
couleur_inventaire="#907EBD"
game=Jeu()
joueur_o=Joueur('circle',"#199E86","cercle.png","barricade.png","item2.png","bouclier_cercle.png","item4.png","BombePortable.png","VolDeData2.png",couleur_plateau,couleur_inventaire)
joueur_x=Joueur('X_cursor',"#1D1C70",'croix.png',"barricade.png","item2.png","bouclier_croix.png","item4.png","BombePortable.png","VolDeData2.png",couleur_plateau,couleur_inventaire)
game.jeu()