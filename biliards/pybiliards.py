import pygame
import pygame.gfxdraw
from pygame.locals import *
import math
import threading
import os
import time
import numpy
import string
import colour
#larghezza , altezza Form
(width, height) = (1024,750)
#contatore progressbar
progress=0
ball_cursor = ((16, 16), (7, 7), 
    (0, 0, 3, 192, 15, 240, 24, 248, 51, 252, 55, 252, 127, 254, 127, 254,
     127, 254, 127, 254, 63, 252, 63, 252, 31, 248, 15, 240, 3, 192, 0, 0),
    (3, 192, 15, 240, 31, 248, 63, 252, 127, 254, 127, 254, 255, 255, 255,
     255, 255, 255, 255, 255, 127, 254, 127, 254, 63, 252, 31, 248, 15, 240,
     3, 192))
#attrito del tavolo
VEL_MAX = 7
friction = VEL_MAX ** 2 / float(VEL_MAX*height)
clock = pygame.time.Clock()
turn = 1
score1 = 0
score2 = 0
msg_acchito = ("Premere 'space' per lanciare la", #help acchito
   "pallina.",
   "Vince l'acchito il giocatore che fa",
   "tornare la propria pallina piu' ",
   "vicino alla sponda D i partenza.")
msg_selectball = ("Posiziona la bilia nel",     #help select_ball
                  "rettangolo opposto all'altra bilia.",
                  "",
                  "",
                  "")
msg_game = ("Colpisc i  con la bilia avversaria", #help game
            "piu' birilli possibili.",
            "Premi e muovi il mouse all'indietro",
            "per colpire la bilia con la stecca.",
            "Vince chi arriva prima a 50 punti.")

def display_box(screen,msg,t_help):
   """Scrive il messaggio all'interno di una text_box
      #Argumet : screen = surface 
                 msg = messaggio di help
                 t_help = tipo di aiuto"""
   pygame.font.init()
   fontobject = pygame.font.Font('Font/BITSUMIS.TTF', 18)  #font
   pygame.draw.rect(screen,pygame.Color(255,255,255),
                   (width/2-96,
                    height/2 - 200,
                    230,150), 0) # rettangolo bianco textbox
   pygame.draw.rect(screen,pygame.Color(0,0,0),
                   (width/2-92,
                    height/2 - 196,
                    222,142), 2) #rettangolo interno texbox

   s=msg[0]
   b =msg[1]
   v=msg[2]
   k=msg[3]
   p=msg[4]

   pygame.font.init()
   Text = pygame.font.Font('Font/BITSUMIS.TTF', 10)
   Thelp = pygame.font.Font('Font/BITSUMIS.TTF', 18)
   help = Thelp.render(t_help, 0 ,(0,0,240))
   text1 = Text.render(s, 0, (0,0,0))
   text2 = Text.render(v,0,(0,0,0))
   text3 = Text.render(p,0,(0,0,0))
   text4 = Text.render(b,0,(0,0,0))
   text5 = Text.render(k,0,(0,0,0))
   screen.blit(text1, (width/2-80,height/2 - 154))       #                   #
   screen.blit(text4, (width/2-80,height/2 - 144))       #                   #
   screen.blit(text2, (width/2-80,height/2 - 124))       #    Blit del testo #
   screen.blit(text5, (width/2-80,height/2 - 114))       #                   #
   screen.blit(text3, (width/2-80,height/2 - 104))       #                   #
   screen.blit(help , (width/2-80,height/2 - 184))       #                   #

   pygame.display.flip() 
   
def ball_inside_castle(ball , rect):
   """Sposta la bilia se si trova all'interno del castello
   Argument : ball = lista di palline
              rect = rettangolo del castello"""
   for b in ball:
      r = pygame.Rect(b.x-b.size,b.y-b.size,2*b.size,2*b.size)
      if rect.colliderect(r) :
         if b.y > 250:
            b.y += 60
         else:
            b.y -= 60

def my_fillGradient(surface , color , gradient , center , size, forward =True) :
   """riempie le bilie con con gradiente
   Argument:
   color -> color iniziale
   gradient -> color finale
   center -> centro della bilia
   size -> raggio della bilia
   forward -> True=forward; False=reverse """  
   h = (center[1]+size) - (center[1]-size)
   if forward : a,b = color , gradient
   else: b , a = color , gradient
   rate = (
      float(b[0]-a[0])/h,
       float(b[1]-a[1])/h,
        float(b[2]-a[2])/h
   )
   fn_circle = pygame.gfxdraw.filled_circle
   cn_circle = pygame.gfxdraw.aacircle
   for col in range(0,size):
      color = (
            min(max(a[0]+(rate[0]*(col)),0),255),
             min(max(a[1]+(rate[1]*(col)),0),255),
             min(max(a[2]+(rate[2]*(col)),0),255)
         )
      fn_circle(surface, int(center[0]) , int(center[1]) , int(size-col), color) 


def reset_game(my_particles,castle):
   """Reset della partita"""
   castle = [] #castello
   c_skittle = Skittle((width/2,250) ,(255,0,0))#birillo centrale
   sx_skittle = Skittle((width/2 - 33 ,250) ,(255,255,255))#sinistro
   dx_skittle = Skittle((width/2 + 33 ,250) ,(255,255,255))#destro
   up_skittle = Skittle((width/2,250 - 33) ,(255,255,255))#alto
   down_skittle = Skittle((width/2,250 + 33) ,(255,255,255))#basso
   #aggiungo i birilli nel castello
   castle.append(c_skittle)
   castle.append(sx_skittle)
   castle.append(dx_skittle)
   castle.append(up_skittle)
   castle.append(down_skittle)   
   number_of_particles = 3 #numero di palline
   my_particles = [] #palline del tavolo
   for n in range(number_of_particles):
      size = 15
      x = 735
      y = 100
      particle = Ball((x, y), size,None)
      if n == 1 :
         particle.colour = (255, 191, 0)
         particle.x = 735
         particle.y = 390
         particle.color_id = 'yellow'
      elif n == 2:
         particle.colour = (255, 0, 0)
         particle.x = 280
         particle.y = 250
         particle.color_id = 'red'
      else:
         particle.colour = (255, 255, 255)
         particle.color_id = 'white'
      my_particles.append(particle)
   return my_particles , castle

def update_referee(lista):
   """Refresh del display quando l'arbitro conta i punti"""
   screen.fill((151,151,240))
   screen.blit(background,(0,0))  
   rettangle = Rectangle((62,60,898,385),1) #creo le sponde
   rettangle.display()   
   pygame.draw.rect(screen, (255,160,128), pygame.Rect(10,510,15,200), 4) #barra di caricamento della potenza della pallina p1
   pygame.draw.rect(screen, (255,160,128), pygame.Rect(width- 20,510,15,200), 4)#barra di caricamento della potenza della pallina p2
   cuesprite = pygame.sprite.RenderPlain()
   stick1 = Cue(screen,img)
   stick2 = Cue(screen,img1)
   player1.cue =  stick1
   player2.cue = stick2
   stick_p1 = pygame.transform.rotate(stick1.image,-90)
   stick_p2 = pygame.transform.rotate(stick2.image,90)
   cuesprite.add(stick1,stick2)
   screen.blit(stick_p2 , (580,498))
   screen.blit(stick_p1 , (10,498))   
   for i, particle in enumerate(lista):
      particle.move()
      particle.bounce()
      particle.display()
   for s in castle:
      s.display()  
   score_board()
   pygame.display.flip()  
   return lista
def update_for_freeball(move):
   """Refresh del display quando c'è il tiro libero"""
   screen.fill((151,151,240))
   screen.blit(background,(0,0))  
   rettangle = Rectangle((62,60,898,385),1) #creo le sponde
   rettangle.display()   
   pygame.draw.rect(screen, (255,160,128), pygame.Rect(10,510,15,200), 4) #barra di caricamento della potenza della pallina p1
   pygame.draw.rect(screen, (255,160,128), pygame.Rect(width- 20,510,15,200), 4)#barra di caricamento della potenza della pallina p2
   cuesprite = pygame.sprite.RenderPlain()
   stick1 = Cue(screen,img)
   stick2 = Cue(screen,img1)
   player1.cue =  stick1
   player2.cue = stick2
   stick_p1 = pygame.transform.rotate(stick1.image,-90)
   stick_p2 = pygame.transform.rotate(stick2.image,90)
   cuesprite.add(stick1,stick2)
   screen.blit(stick_p2 , (580,498))
   screen.blit(stick_p1 , (10,498))    
   for i, particle in enumerate(my_particles):
      particle.move()
      particle.bounce()
      for particle2 in my_particles[i+1:]:
         collide(particle, particle2)
      if particle == move :
         pass
      else:
         particle.display()
   for s in castle:
      s.display()   
   score_board()
   pygame.display.flip()    
def run_referee (lis,castle):
   """Arbitro della partita
                  #Argument = -lis = lista delle bilie
                              -castle = castello
                  #Return = l'eventuale fallo e/o tiro libero
                            e il punteggio totale del tiro"""
   p1,p2,p3 = lis[0],lis[1],lis[2]
   foul = False
   spot_already_striken = False # variabile per il pallino
   tot_score = 0
   collision_with_ball_adversary = False #variabile per collisione pallina avversaria
   free_ball = False #variabile tiro libero
   while ball_inMovement([p1,p2,p3]):
      update_referee(lis)
      
      if collide(p1,p2) and not foul: #bilia battente colpisce bilia avversaria
         collision_with_ball_adversary = True
      if collide_skittles([p1],castle) and not collision_with_ball_adversary: 
         #bilia battente colpisce il castello senza aver colpito la bilia avversaria
         tot_score += 2 #numero birilli
         foul = True
         free_ball = True
      if collide(p1,p3) and not collision_with_ball_adversary and not spot_already_striken:
         #bilia battente colpisce il pallino senza aver colpito la bilia avversaria
         tot_score += 4
         foul = True
         free_ball = True
         spot_already_striken = True
      if collide_skittles([p1],castle) and collision_with_ball_adversary:
         #bilia battente colpisce il castello dopo aver colpito la bilia avversaria
         tot_score += 2   #numero birilli
         foul = True
      if collide(p1,p3) and collision_with_ball_adversary and not spot_already_striken:
         #bilia battente colpisce il pallino dopo aver colpito la bilia avversaria
         tot_score += 4
         spot_already_striken = True
      if collide(p2,p3) and not spot_already_striken and collision_with_ball_adversary:
         #bilia avversaria colpisce il pallino dopo essere stata colpita dalla bilia battente
         tot_score += 3
         spot_already_striken = True
      if collide_skittles([p2],castle) and collision_with_ball_adversary:
         #bilia avversaria colpisce il castello
         tot_score += 2 #numero birilli
      if collide_skittles([p3],castle) and collision_with_ball_adversary:
         #pallino colpisce il castello
         tot_score += 2 #numero birilli
   if not foul and not collision_with_ball_adversary: #bilia battente non colpisce nulla
      tot_score = 2
      free_ball = True
      foul = True
   return free_ball,foul,tot_score
def score_board():
   """Mostra il punteggio dei giocatori"""
   pygame.font.init()
   Text = pygame.font.Font('Font/BITSUMIS.TTF', 50) #font
   text1 = Text.render('score:', 0, (255,255,255))
   text2 = Text.render('player1 : %d' % score1,0,(255,255,255))
   text3 = Text.render('player2 : %d' % score2,0,(255, 191, 0))   
   screen.blit(text1, (width/2-85,height-220))      #                               #
   screen.blit(text2, (60,height-170))              # Blit delle info della partita #
   screen.blit(text3, (width/2+135,height-170))     #                               #
   
def selectBall(move_ball,o_ball,cont,screen):
   """Thread che si occupa di posizionare la pallina per il tiro libero
      #Arguments = -move_ball bilia da posizionare
                   -o_ball pallina avversaria
                   
      #Return = la bilia il posizionata nel rettangolo opposto alla bilia avversaria"""
   run = True
   pygame.init()
   old_cursor = pygame.mouse.get_cursor()#salvo il vecchio cursore
   pygame.mouse.set_cursor(*ball_cursor)#carico il nuovo cursore
   infrect = width / 2 # rettangolo inferiore
   tmp = 0
   button = Button() # bottone di help
   screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
   pygame.display.flip() 
   if o_ball.x >= infrect: # calcolo la x massima per posizionare la bilia rispetto a quella avversaria
      max_pos = pygame.Rect(0,0,infrect,500)
   else:
      max_pos = pygame.Rect(infrect,0,width,500)
   while run :
      if cont == 0:
         if tmp < 10:
            tmp += 1
      for event in pygame.event.get():
         x , y = pygame.mouse.get_pos()
         if y > 490 : # calbio il cursore del mouse
            pygame.mouse.set_cursor(*old_cursor)
            if event.type == pygame.MOUSEBUTTONDOWN and button.pressed((x,y)): #clicco sul pulsante help
               pressed = True
               while pressed :
                  for event in pygame.event.get():
                     if event.type == pygame.MOUSEBUTTONDOWN :
                        pressed = False
                  display_box(screen,msg_selectball,"Help :   SelectBall" )
               update_referee([o_ball,my_particles[2]])
               screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
               pygame.display.flip()             
         else:
            pygame.mouse.set_cursor(*ball_cursor)
         
            if event.type == pygame.MOUSEBUTTONDOWN : # seleziono la posizione della pallina
               mouse_x , mouse_y = pygame.mouse.get_pos()
               move_ball.y = mouse_y 
                                
               if max_pos[0] == 0 and mouse_x > infrect: # guardo se la nuova posizione della pallina non supera
                  move_ball.x = infrect                  # il rettangolo dove è contenuta l'altra
               elif max_pos[0] == infrect and mouse_x < infrect:
                  move_ball.x = infrect
               else:
                  move_ball.x =mouse_x 
               run = False
               pygame.mouse.set_cursor(*old_cursor)
            
   return move_ball       
         
def acchito(queue,screen):
   """Thread che gestisce la prima fase del gioco
      chiamata acchito i giocatori lanciano le bilie
      contro la sponda conrta opposta , la bilia che si avvicina
      di più alla sponda corta di partenza tira per primo
               #Arguments : -queue coda inizialmente vuota
               # Return : la coda contente le informazioni del vincitore dell'acchito"""
   update_display()
   run = True
   pygame.init()
   first_shot = second_shot = init_acchito = False # tiro primo e secondo giocatore 
   power1 = power2 = 0 #potenza di tiro
   progress1 = progress2 = 0 #progressbar
   button = Button() # bottone help
   screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
   pygame.display.flip()
   i = 0
   while run :
      for event in pygame.event.get():
         if pygame.key.get_pressed()[K_SPACE]: # il primo giocatore ha lanciato
            first_shot = True
            i = 1
         if pygame.key.get_pressed()[K_SPACE] and second_shot: # il secondo lancia dopo il primo
            init_acchito = True 
         if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]: # esc
            pygame.quit()
         if event.type == pygame.MOUSEBUTTONDOWN :  
            if button.pressed(pygame.mouse.get_pos()) : # bottone help premuto
               pressed = True
               while pressed :
                  for event in pygame.event.get():
                     if event.type == pygame.MOUSEBUTTONDOWN :
                        pressed = False
                  display_box(screen,msg_acchito,"Help :   acchito") #finestra di aiuto
               update_for_freeball(None)
               screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
               pygame.display.flip()
         if i < 1 : #aiuto iniziale
            display_box(screen,msg_acchito,"Help :   acchito")
         elif i == 1 : 
            i += 1
            update_for_freeball(None)
            screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
            pygame.display.flip()            
               
      if not first_shot : # primo giocatore tira
         if progress1 > 1: #fine progress bar
            progress1 = 0
            pygame.draw.rect(screen, (178,255,255), pygame.Rect(13,513,10,196))
            pygame.display.update((13,513,10,196))
         pygame.draw.rect(screen, ((255*progress1*100)/100,(255*(100-progress1*100))/100,24), pygame.Rect(13,513,10,196*progress1))
         progress1 += 0.001
         pygame.display.update((13,513,10,196*progress1))
      else:
         power1 =  progress1 * VEL_MAX # potenza di tiro
         if not init_acchito:
            second_shot = True
         else: 
            second_shot = False
            
      if second_shot : #secondo giocatore tira
         if progress2 > 1: #fine progress bar
            progress2 = 0
            pygame.draw.rect(screen, (178,255,255), pygame.Rect(width- 17,513,10,196))
            pygame.display.update((width- 17,513,10,196))            
         pygame.draw.rect(screen, ((255*progress2*100)/100,(255*(100-progress2*100))/100,24), pygame.Rect(width- 17,513,10,196*progress2))
         progress2 += 0.001
         pygame.display.update((width- 17,513,10,196*progress2))
      elif init_acchito :
         power2 = progress2 * VEL_MAX
         run = False
   queue.append((True,power1,power2)) #viene aggiunto alla coda un valore di verità e le potenze di tiro
   
def player_turn(player1,player2,turn):
   
   """Setta il turno del giocatore in base
      a chi ha tirato per ultimo
          #Arguments : -player1 giocatore numero 1
                       -player2 giocatore numero 2
                       -turn contatore turno
          #Return : il giocatore del turno corrente e la pallina avversaria"""
   if turn % 2 == 1:
      return player1 , player2.ball , player2
   return player2 , player1.ball , player1
def collision_guideline(x,y,ball):
   """Linea guida per il tiro,
      controlla se la pallina andrà a sbattere
      contro un altra pallina
          #Arguments : -x,y coordinata della linea guida
                       -ball palline con cui può avvenire una collisione
          #Return : True se è avvenuta una collisione,False altrimenti"""
   for b in ball:
      dx = b.x - x
      dy = b.y - y
      dist = math.hypot(dx, dy) #distanza euclide
      r12 = b.size + 15
      if dist < r12:
         return True
   return False
def determinate_guideline(x,y,angle,ball):
   """Linea guida per il tiro,
      controlla se la pallina andrà a sbattere
      contro una sponda o un altra pallina
          #Arguments : -x,y coordinata della linea guida
                       -angle angolodi orientazione della stecca
                       -ball palline con cui può avvenire una collisione
          #Return : coordinata per disegnare la linea guida   """
   dist = 0
   touch_object = False
   while not touch_object: #aumento la distanza della linea guida fin quando non tocca un oggetto
      x,y = convert_polar_coordinates_to_cartesian(x,y,angle,dist)
      if x > rettangle.x+17 and x < rettangle.width+45 and y > rettangle.y+17 and y < rettangle.height+44 and not collision_guideline(x,y,ball):
         dist += 0.001
      else: touch_object = True
   return x,y
def set_myskittle(castle,c,d,s,u,dw):
   """Setta il castello
          #Arguments : -castle castello
                       -c,d,s,u,dw birilli che costituiscono il castello"""
   if c not in castle:
      castle.append(c)
   if d not in castle:
      castle.append(d)
   if s not in castle:
      castle.append(s)
   if u not in castle:
      castle.append(u)
   if dw not in castle:
      castle.append(dw)

def collide_skittles(my_particles , castle):
   """Gestisce la collisione con i birilli del castello
      rimuovendo dal castello i birilli che sono cascati
          #Arguments : -my_particle palline sul tavolo
                       -castle castello"""
   for s in castle:
      for p1 in my_particles:
         dx = p1.x - s.x
         dy = p1.y - s.y
         dist = math.hypot(dx, dy) #distanza euclidea
         r12 = p1.size + s.size
         if dist <= r12:
            castle.remove(s)
            return True
   return False
def update_display():
   """Update del display """
   for particle in my_particles:
      particle.display()
   for skittle in castle:
      skittle.display()
   rettangle.display()
   if turn % 2 == 1:
      pygame.draw.rect(screen, ((255*progress*100)/100,(255*(100-progress*100))/100,24), pygame.Rect(13,513,10,196*progress))
   else:
      pygame.draw.rect(screen, ((255*progress*100)/100,(255*(100-progress*100))/100,24), pygame.Rect(width-17,513,10,196*progress))   
   score_board()
   pygame.display.flip()

def hit_ball(cue_ball , angle ,power ):
   """Setta la velocita della pallina da colpire
          #Arguments : -cue_ball pallina da colpire
                       -angle angolo di direzione
                       -power potenza di tiro"""
   cue_ball.speed[0] = power * math.cos(math.radians(angle))
   cue_ball.speed[1] = power * math.sin(math.radians(angle))

def get_angle(object1_x, object1_y, object2_x, object2_y):
   """Angolo tra due oggetti
          #Arguments : -object1_x,object1_y primo ogetto
                       -object2_x,object2_y secondo ogetto
          #Return : angolo in gradi   """
   difference_of_x = object1_x - object2_x
   difference_of_y = object1_y - object2_y
   radians = math.atan2(difference_of_y, difference_of_x) #arcotangente dy/dx
   radians %= 2*math.pi
   angle = math.degrees(radians)
   return angle
def convert_polar_coordinates_to_cartesian(x, y, angle, length):
   """Converte un punto in coordinate polari P (x,y)
      in un punto in coordinate cartesiane
          #Arguments : -x,y coordinata polare di P
                       -angle angolo in gradi
                       -length lunghezza dal centro della coordinata polare
          #Return : coordinata cartesiana x,y"""
   x += length * math.cos(math.radians(angle))
   y += length * math.sin(math.radians(angle))
   return x, y
def ball_inMovement(balls):
   """Controlla se ci sono palline in movimento
                #Arguments : balls palline sul tavolo
                #Return : True se ci sono palline in movimento
                          False altrimenti"""
   for ball in balls:
      if ball.speed != [0,0]:
         return True
   return False
def collide(p1, p2):
   """Gestisce la collisione tra due palline
          #Arguments : -p1 pallina 1
                       -p2 pallina 2"""
   dx = p1.x - p2.x
   dy = p1.y - p2.y
   dist = math.hypot(dx, dy) #distanza euclidea
   r12 = p1.size + p2.size
   if dist < r12: #collisione avvenuta
      pygame.mixer.init()
      sound = pygame.mixer.Sound('images/collide.ogg')
      sound.play()      
      speed2 = [- (dx / dist) ,  - (dy/dist) ] #vettore direzione
      vr1 =  numpy.dot(p1.speed , speed2) # prodotto per scalare
      vr2 = numpy.dot(p2.speed , speed2)
      drv = vr2 - vr1
      p2.speed = [p2.speed[0] - drv * speed2[0] , p2.speed[1] - drv * speed2[1]] #nuova velocita
      p1.speed = [p1.speed[0] + drv * speed2[0] , p1.speed[1] + drv * speed2[1]]
      p1.move()
      p2.move()
      return True
   return False

class Cue(pygame.sprite.Sprite):
   """Classe Sprite che implementa la stecca da biliardo"""
   def __init__(self, board,img):
      """Costuttore stecca
             #Arguments : -board surface sul quale disegnare"""
      pygame.sprite.Sprite.__init__(self)
      self.board = board
      self.image = img
      self.rect = self.image.get_rect()
      self.CUE_WIDTH = self.rect.width
      self.CUE_LENGTH = self.rect.height
      self.originalcopy = pygame.transform.scale(self.image, (self.CUE_WIDTH, self.CUE_LENGTH))#immagine scalata
      self.cuestop = pygame.transform.rotate(self.image,90) #stecca in stallo
      
   def update(self,dest_mouse,src,key_pressed,dist):
      """Aggiorna la posizionde della stecca
                  #Argument : -self stecca
                              -dest_mouse coordinata x,y del mouse
                              -src coordinata x,y pallina da colpire
                              -key_pressed variabile booleana per il controllo della tastiera
                              -dist distanza dalla stecca al centro della pallina
                  #Return : True se la pallina è stata colpita ,
                            False altrimenti"""
      if not key_pressed :
         mouse_x , mouse_y = dest_mouse
         mouse_degs = get_angle(mouse_x,mouse_y,src[0],src[1])#angolo tra la pallina e il mouse
         dest = convert_polar_coordinates_to_cartesian(src[0] , src[1] ,mouse_degs , dist)#converto in coordinate cartesiane
         dest_minus_src = (dest[0]-src[0],dest[1]-src[1])
         angle = math.atan2(dest_minus_src[0], dest_minus_src[1])#angolo delle distanze
         c, s = math.cos(angle), math.sin(angle) #sin e cos angolo
         angle = 180.0/math.pi*angle

         t = self.CUE_WIDTH/2.0 
         l = self.CUE_LENGTH/2.0

         self.image = pygame.transform.rotate(self.originalcopy, angle)#ruota l'immagine di angle gradi

         irect = self.image.get_rect()#ricostruzione del rettangolo dell'immagine
         left,top = dest
         self.rect.width = irect.width
         self.rect.height = irect.height
         #ruoto il rettangolo dell'immagine in base all'angolo
         if 0<=angle<=90:
            top -= t*s
            left -= t*c
         elif 90<=angle<=180:
            top -= irect.height
            top += t*s
            left += t*c
         elif -90<=angle<0:
            left -= irect.width
            top += t*s
            left += t*c
         else:
            top -= irect.height
            left -= irect.width
            top -= t*s
            left -= t*c
         self.rect.topleft = left,top
         return False
      else: #tiro
         while dist > 15: # colpisco la pallina
            dist -= 5
            cuesprite.clear(screen,background) 
            self.update(dest_mouse,src,False,dist)
            cuesprite.draw(screen)
            pygame.time.delay(5)
            update_display()
         pygame.mixer.init()
         sound = pygame.mixer.Sound('images/nutfall.ogg')
         sound.play()
         return True
class Rectangle:
   """Classe che implementa le sponde del tavolo"""
   def __init__(self,(x,y,width,height),thickness):
      """Costruttore sponde
                   #Arguments : -self sponde
                                -x,y,width,height posizione e area sponde
                                -thickness spessore"""
      self.x = x
      self.y = y
      self.width = width
      self.height = height
      self.colour = (0,110,59)
      self.thickness = thickness

   def display(self):
      """Disegna le sponde del tavolo"""
      pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width,self.height), self.thickness)

class Ball():
   """Classe che implementa le palline del gioco"""
   def __init__(self, (x, y), size,color):
      """Costruttore della pallina
            #Arguments : -self pallina
                         -(x,y) coordinata del centro della pallina
                         -size raggio
                         -color colore della pallina"""
      self.x = x
      self.y = y
      self.size = size
      self.colour = (0,0, 255)
      self.thickness = 0
      self.speed = [0,0]  #velocità
      self.color_id = color #colore (stringa)
      self.pos = [x,y]
      self.bounce_acchito = False #variabile che controlla se è stata toccata la sponda durante l'acchito
      self.shadow = (0,0,0)
   def display(self):
      """Disegna la pallina"""
      s_x , s_y , r = self.add_lights() #cerchio di centro (s_x,s_y) e raggio r
      pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.size, self.colour)
      pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.size,self.colour)
      my_fillGradient(screen,(255,255,255),self.colour,(s_x,s_y),r,forward=False)  # gradiente cerchio colpito dalla luce
   def move(self):
      """Muove la pallina in base alla sua velocità"""
      self.x += self.speed[0]
      self.y += self.speed[1]
      self.pos = [self.x,self.y]
      V1 = math.hypot(self.speed[0], self.speed[1]) #modulo del vettore velocità
      if V1 < friction:
         self.speed = [0,0]
      else:
         self.speed[0] = self.speed[0] - friction * self.speed[0] / V1  # forza di attrito
         self.speed[1] = self.speed[1] - friction * self.speed[1] / V1  # attrito nella direzione opposta

   def bounce(self):
      """Controlla le collisioni della pallina contro le sponde del tavolo"""
      if self.x  > rettangle.width + 3*self.size +1: #sponda destra
         self.x = 2*(rettangle.width + 3*self.size +1) - self.x
         self.speed[0] *= -1 #flip coordinata x del vettore velocita
      elif self.x < rettangle.x + self.size + 1 : #sponda sinistra
         self.x = 2*(rettangle.x + self.size +1) - self.x
         self.bounce_acchito = True
         self.speed[0] *= -1 #flip coordinata x del vettore velocita
      if self.y > rettangle.height + 3*self.size : #sponda bassa
         self.y = 2*(rettangle.height + 3*self.size ) - self.y
         self.speed[1] *= -1 #flip coordinata y del vettore velocita
      elif self.y < rettangle.y + self.size +1: #sponda alta
         self.y = 2*(rettangle.y + self.size +1) - self.y
         self.speed[1] *= -1 #flip coordinata y del vettore velocita
         
   def add_lights(self) :
      """Aggiunge le luci alla pallina
         Esegue un interpolazione per vedere dove cade la luca"""
      delta_x = float(self.x - self.size - rettangle.x) / float(rettangle.width - rettangle.x) #(p_x - raggio - sponda a sx) / (lunghezza)
      delta_y = float(self.y - self.size - rettangle.y) / float(rettangle.height - rettangle.y)#(p_y - raggio - sponda top) / (altezza)
      dist = float(math.hypot(self.x - width/2 , self.y - 250)) #distanza dal centro della luce
      dist_max = float(math.hypot(rettangle.x - width / 2 , rettangle.y - 250)) # massimo valore di luminosità
      delta_r = float (dist / dist_max) # distanza dal centro della luce diviso il massimo valore di luminosità
      radius = (1.0-delta_r)*(self.size)+delta_r*(8.0) #raggio del fascio di luce
      return ((1.0-delta_x)*(self.x+6)+delta_x*(self.x-6) ,(1.0-delta_y)*(self.y+3)+delta_y*(self.y-3)  , int(radius)) #interpolazione lineare
      
      
class Skittle():
   """Classe che implementa i birilli del castello"""
   def __init__(self,(x,y),color):
      """Costruttore del birillo
             #Arguments : -self birillo
                          -(x,y) coordinata del birillo
                          -color colore birillo"""
      self.x = x
      self.y = y
      self.pos = [x,y]
      self.size = 3 #raggio
      self.color = color

   def display(self):
      """Disegna il birillo"""
      pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, 0)

class Player():
   """Classe che implementa i giocatori"""
   def __init__(self,name,ball,cue):
      """Costruttore del giocatore
              #Arguments : -self il giocatore
                           -name nome del giocatore
                           -ball pallina del giocatore
                           -cue stecca del giocatore"""
      self.name = name
      self.ball = ball
      self.cue = cue
      self.score = 0

   def set_score(self,score):
      """Setta il punteggio del giocatore
            #Arguments : -score punteggio da aggiungere"""
      self.score += score
class Button():
   """Classe che implementa i pulsanti del gioco"""
   def create(self,screen,color,x,y,length,height,width,text,text_color,color_rect = (190,190,190)):
      """Inizializzazione del bottone"""
      screen =  self.draw(screen,color, length, height, x, y, width,color_rect)
      screen = self.write_text(screen, text, text_color, length, height, x, y)
      self.rect = pygame.Rect(x,y, length, height)
      return screen
   def write_text(self, surface, text, text_color, length, height, x, y):
      """Inserimento del testo"""
      pygame.font.init()
      font_size = int(length//len(text))
      myFont = pygame.font.Font('Font/button.ttf', font_size)
      myText = myFont.render(text, 1, text_color)
      surface.blit(myText, ((x+length/2) - myText.get_width()/2, (y+height/2) - myText.get_height()/2))
      return surface   
   
   def draw(self, surface, color, length, height, x, y, width,color_rect ): 
      """Disegno del bottone"""
      for i in range(1,10):
         s = pygame.Surface((length+(i*2),height+(i*2)))
         s.fill(color)
         alpha = (255/(i+2))
         if alpha <= 0:
            alpha = 1
         s.set_alpha(alpha)
         pygame.draw.rect(s, color, (x-i,y-i,length+i,height+i), width)
         surface.blit(s, (x-i,y-i))
      pygame.draw.rect(surface, color, (x,y,length,height), 0)
      pygame.draw.rect(surface, color_rect, (x,y,length,height), 1)  
      return surface   
   def pressed(self, mouse):
      """Evento mouse_Pressed"""
      if mouse[0] > self.rect.topleft[0]:
         if mouse[1] > self.rect.topleft[1]:
            if mouse[0] < self.rect.bottomright[0]:
               if mouse[1] < self.rect.bottomright[1]:
                  return True
               else: return False
            else: return False
         else: return False
      else: return False   
pygame.init()
screen = pygame.display.set_mode((width, height),pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.SRCALPHA,32) #Form
pygame.display.set_caption('Biliardo italiana')
background = pygame.image.load('images/pool.bmp') #carico l'immagine del tavolo
img = pygame.image.load('images/stick.bmp').convert_alpha() #carico l'immagine della stecca
img1 = pygame.image.load('images/stick2.bmp').convert_alpha()
menu = pygame.image.load('images/menu.bmp').convert(24)
number_of_particles = 3 #numero di palline
castle = [] #castello
c_skittle = Skittle((width/2,250) ,(255,0,0))#birillo centrale
sx_skittle = Skittle((width/2 - 33 ,250) ,(255,255,255))#sinistro
dx_skittle = Skittle((width/2 + 33 ,250) ,(255,255,255))#destro
up_skittle = Skittle((width/2,250 - 33) ,(255,255,255))#alto
down_skittle = Skittle((width/2,250 + 33) ,(255,255,255))#basso
castle_rect = pygame.Rect(width/2-33,250-33,66,66)
#aggiungo i birilli nel castello
castle.append(c_skittle)
castle.append(sx_skittle)
castle.append(dx_skittle)
castle.append(up_skittle)
castle.append(down_skittle)
my_particles = [] #palline del tavolo
for n in range(number_of_particles):
   size = 15
   x = 735
   y = 100
   particle = Ball((x, y), size,None)
   if n == 1 :
      particle.colour = (237,185,0)
      particle.shadow = (104,81,0)
      particle.x = 735
      particle.y = 390
      particle.color_id = 'yellow'
   elif n == 2:
      particle.colour = (204 , 8 , 8)
      particle.shadow = (109,4,4)
      particle.x = 280
      particle.y = 250
      particle.color_id = 'red'
   else:
      particle.colour = (170,170,170)
      particle.shadow = (109,109,109)
      particle.color_id = 'white'
   my_particles.append(particle)

player1 = Player('id_1',my_particles[0],None) #creazione player1 (pallina bianca)
player2 = Player('id_2',my_particles[1],None) #creazione player2 (pallina gialla)
running = True
lunch_ball = False #pallina lanciata ?
acchito_init = True #acchito iniziale
shot_with_cue = False #tiro con la stecca
select_ball = False #pallina selezionata
move_ball = o_ball = None 
ball_free = False #tiro libero
menu_init = False
reset = False
dragstart = False
start_cursor = None
cont = 0
player_win = ""
help_button = Button() #bottone di aiuto
while running: #while infinito
   for event in pygame.event.get(): #eventi
      if event.type == pygame.QUIT or not running: #chiudo la finestra con il mouse
         running = False
         break
      if pygame.key.get_pressed()[K_ESCAPE] : #chiudo la finestra con 'Esc'
         running = False
      if event.type == pygame.MOUSEBUTTONUP and dragstart : #lancio della pallina
         lunch_ball = True
         dragstart = False
      if event.type == pygame.MOUSEBUTTONDOWN and not help_button.pressed(pygame.mouse.get_pos()): #mouse_down
         dragstart = True
         start_cursor = pygame.mouse.get_pos()
      if event.type == pygame.MOUSEBUTTONDOWN and help_button.pressed(pygame.mouse.get_pos()) : #bottone help premuto
         pressed = True
         while pressed :
            for event in pygame.event.get():
               if event.type == pygame.MOUSEBUTTONDOWN :
                  pressed = False
            display_box(screen,msg_game,"Help : ") #finestra di aiuto
         update_for_freeball(None)
         screen = button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0)) 
         pygame.display.flip()         
      if select_ball and not ball_inMovement([player1.ball,player2.ball]): #posiziono la pallina dopo acchito
         if (player1.ball.bounce_acchito and player2.ball.bounce_acchito) or (not player1.ball.bounce_acchito and not player2.ball.bounce_acchito):
            if player1.ball.x > player2.ball.x :
               player2.ball.x , player2.ball.y = player2.ball.pos = (156 , 250)
               o_ball = player2.ball
               move_ball = player1.ball
            else:
               player1.ball.x , player1.ball.y = player1.ball.pos = (156 , 250)           
               move_ball = player2.ball
               o_ball = player1.ball
               turn = 0
         elif player1.ball.bounce_acchito and not player2.ball.bounce_acchito:
            player2.ball.x , player2.ball.y = player2.ball.pos = (156 , 250)
            o_ball = player2.ball
            move_ball = player1.ball
         else:
            player1.ball.x , player1.ball.y = player1.ball.pos = (156 , 250)           
            move_ball = player2.ball
            o_ball = player1.ball
            turn = 0   
         ball_free = True
      if not menu_init : #menu iniziale
         while not menu_init:
            screen.blit(menu,(0,0))
            button = Button()
            screen = button.create(screen,(255,255,255),800,550,150,50,150,"Playgame",(0,0,0))
            pygame.display.flip()            
            for event in pygame.event.get():
               if event.type == pygame.QUIT or pygame.key.get_pressed() [K_ESCAPE]:
                  menu_init = True
                  running = False
                  pygame.quit()
               elif event.type == MOUSEBUTTONDOWN:
                  if button.pressed(pygame.mouse.get_pos()):            
                     menu_init = True
      if reset: #fine partita
         while reset :
            screen.blit(menu,(0,0))
            button = Button()
            screen = button.create(screen,(255,255,255),800,550,150,50,150,"PlayAgain",(0,0,0))
            pygame.font.init()
            pygame.mixer.init()
            sound = pygame.mixer.Sound('images/winner.ogg')
            sound.play()                
            Text = pygame.font.Font('Font/BITSUMIS.TTF', 150)
            text1 = Text.render(player_win+" Win", 0, (255,255,255))  
            screen.blit(text1, (10,height-620))
            pygame.display.flip()
            for event in pygame.event.get():
               if event.type == pygame.QUIT:
                  reset = False
                  running = False
                  pygame.quit()
               elif event.type == MOUSEBUTTONDOWN:
                  if button.pressed(pygame.mouse.get_pos()):    
                     lunch_ball = False #pallina lanciata 
                     acchito_init = True #acchito iniziale
                     shot_with_cue = False #tiro con la stecca
                     select_ball = False #pallina selezionata
                     move_ball = o_ball = None 
                     ball_free = False #tiro libero
                     reset = False
                     turn = 1
                     player1.score = player2.score = score1 = score2= 0
                     my_particles , castle = reset_game(my_particles,castle)
                     player1.ball = my_particles[0]
                     player2.ball = my_particles[1]                     
                     cont = 0   
                     
   if running:            
      screen.fill((151,151,240))#sfondo della finestra
      screen.blit(background,(0,0))#blit del tavolo
      rettangle = Rectangle((62,60,898,385),1) #creo le sponde
      rettangle.display()  
      screen = help_button.create(screen,(151,151,240),width/2-85,height-100,150,50,150,"Help",(0,0,0),color_rect=(0,0,0))  
      pygame.draw.rect(screen, (255,160,128), pygame.Rect(10,510,15,200), 4) #barra di caricamento della potenza della pallina p1
      pygame.draw.rect(screen, (255,160,128), pygame.Rect(width- 20,510,15,200), 4)#barra di caricamento della potenza della pallina p2
      cuesprite = pygame.sprite.RenderPlain() #sprite delle stecche
      stick1 = Cue(screen,img)#creazione stecche
      stick2 = Cue(screen,img1)
      player1.cue =  stick1
      player2.cue = stick2
      stick_p1 = pygame.transform.rotate(stick1.image,-90)
      stick_p2 = pygame.transform.rotate(stick2.image,90)
      cuesprite.add(stick1,stick2)
      if acchito_init and not shot_with_cue: #stecche in stallo
         screen.blit(stick_p2 , (580,498))
         screen.blit(stick_p1 , (10,498))
      elif ball_inMovement(my_particles) or select_ball: #stecche in stallo
         screen.blit(stick_p2 , (580,498))
         screen.blit(stick_p1 , (10,498))         
      elif turn % 2 == 1 : #stecca del secondo giocatore in stallo
         screen.blit(stick_p2 , (580,498))
      else: #stecca del primo giocatore in stallo
         screen.blit(stick_p1 , (10,498)) 
         
      if shot_with_cue and not select_ball : #posso tirare solo se non ci sono bilie da posizionare
         
         if ball_inMovement(my_particles) == False : #le palline sono ferme
            dist_for_cue = 30 #distanza minima dalla stecca alla pallina
            
            current_player , o_ball , avversary= player_turn(player1,player2,turn) #controllo di chi è il turno
            if len(castle) < 5: #controllo che ci siano tutti i birilli altrimenti li rimetto nel castello
               set_myskittle(castle,c_skittle,dx_skittle,sx_skittle,up_skittle,down_skittle)
            cue_b = [current_player.ball.x , current_player.ball.y] #pallina da colpire
            other_ball = [o_ball,my_particles[2]] #palline rimaste
            ball_inside_castle(my_particles,castle_rect) #sposto le eventuali palline rimaste dentro il castello
            if turn % 2 == 1 : # stecca del secondo giocatore in stallo
               cuesprite.remove(stick2)
            else: # stecca del primo giocatore in stallo
               cuesprite.remove(stick1) 
            if dragstart: # mouse_down
               if pygame.mouse.get_pos() != start_cursor :
                  #massima distanza in valore assoluto tra la posizione del mouse e la pallina
                  max_distance = max(abs(cue_b[1]-pygame.mouse.get_pos()[1]),abs(cue_b[0]-pygame.mouse.get_pos()[0])) 
                  dist_for_cue = max_distance + 30
                  if dist_for_cue > 120 : # raggiunto la distanza massima
                     dist_for_cue = 120
               cue_dist = dist_for_cue
            cue_collision = current_player.cue.update( pygame.mouse.get_pos(), cue_b,lunch_ball,dist_for_cue) #aggiorno la posizione della stecca         
            cuesprite.draw(screen) #draw della stecca da mouvere
            mouse_x , mouse_y = pygame.mouse.get_pos() #posizione mouse
            angle_guideline = get_angle(cue_b[0],cue_b[1],mouse_x,mouse_y) #angolo per la linea guida
            #converto in coordinate polari il centro della linea guida
            dist_guideline_x , dist_guideline_y = convert_polar_coordinates_to_cartesian(cue_b[0],cue_b[1],angle_guideline,15) 
            l_x , l_y = determinate_guideline(dist_guideline_x,dist_guideline_y,angle_guideline,other_ball)
            pygame.draw.circle(screen,(255,255,255),(int(l_x),int(l_y)),15,2) #linea guida
            if cue_collision :#pallina colpita
               turn += 1 #cambio turno
               mouse_x , mouse_y = pygame.mouse.get_pos()
               angle = get_angle(cue_b[0],cue_b[1],mouse_x,mouse_y)
               hit_ball(current_player.ball,angle,float(cue_dist/120.0)* VEL_MAX) # lancio la pallina
               lunch_ball = False
               l = ([current_player.ball,o_ball,my_particles[2]])
               free,foul,tot_score = run_referee(l,castle) #controllo dei punti e eventuali falli
               if not foul : #non si sono verificati falli
                  current_player.set_score(tot_score) 
               else: 
                  avversary.set_score(tot_score)
               if free: #tiro libero causato da un fallo
                  move_ball = avversary.ball
                  o_ball = current_player.ball
                  ball_free = True
               if (turn-1) % 2 == 1:
                  score1 = current_player.score
                  score2 = avversary.score
               else:
                  score1 = avversary.score
                  score2 = current_player.score
               if player1.score > 50 : #partita finita il giocatore 1 ha raggiunto il punteggio massimo
                  reset = True
                  player_win = "Player1"
               elif player2.score > 50 :
                  reset = True
                  player_win = "Player2"
               
      elif not shot_with_cue and acchito_init:#fase di acchito         
         queue = []
         thred_acchito = threading.Thread(target=acchito,args=[queue,screen])
         thred_acchito.start()
         thred_acchito.join() 
         shot_with_cue,pw1,pw2 = queue.pop()
         hit_ball(player1.ball,0,-pw1)
         hit_ball(player2.ball,0,-pw2)
         select_ball = True
      #animazione della partita
      if not reset:
         for i, particle in enumerate(my_particles):
            particle.move()
            particle.bounce()
            for particle2 in my_particles[i+1:]:
               collide(particle, particle2)
            if ball_free and particle == move_ball :
               pass
            else:
               particle.display()
         for s in castle:
            s.display()
         score_board()
         pygame.display.flip()
         if ball_free : #tiro libero
            update_for_freeball(move_ball)
            thred_ball_free = threading.Thread(target=selectBall,args=[move_ball,o_ball,cont,screen])
            cont = 1
            thred_ball_free.start()  
            thred_ball_free.join()
            shot_with_cue = True
            select_ball = False
            ball_free = False
         pygame.display.flip()
         clock.tick(240)
pygame.quit()