import pygame
import random
import math
import os

pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()

screen=pygame.display.set_mode((800,600))
pygame.display.set_caption("Battle Arena")
clock=pygame.time.Clock()

WIDTH=screen.get_width()
HEIGHT=screen.get_height()
font=pygame.font.Font(None,36)
big_font=pygame.font.Font(None,80)
small_font=pygame.font.Font(None,28)

base=os.path.dirname(os.path.abspath(__file__))

walk_sound=pygame.mixer.Sound(os.path.join(base,"Walk.ogg"))
shoot_sound=pygame.mixer.Sound(os.path.join(base,"Shoot.ogg"))
pygame.mixer.music.load(os.path.join(base,"Background.ogg"))
pygame.mixer.music.set_volume(0.6)

scene="start"
character=None

start_button=pygame.Rect(WIDTH//2-120,HEIGHT//2-40,240,80)
boy_button=pygame.Rect(WIDTH//2-180,HEIGHT//2-20,150,70)
girl_button=pygame.Rect(WIDTH//2+30,HEIGHT//2-20,150,70)

player_x=WIDTH//2
player_y=HEIGHT//2
player_size=40
player_speed=5
health=100
score=0
facing_x=1
facing_y=0

bullets=[]
enemies=[]
spawn_timer=0
shoot_timer=0
apple=None
apple_size=18
apple_health_limit=40

joystick_center=(100,HEIGHT-100)
joystick_radius=65
stick_radius=30
stick_x=joystick_center[0]
stick_y=joystick_center[1]
joystick_finger=None
fire_finger=None

fire=pygame.Rect(WIDTH-150,HEIGHT-130,120,80)

obstacles=[
    pygame.Rect(300,150,160,35),
    pygame.Rect(180,300,35,150),
    pygame.Rect(570,250,35,150)
]

game_over=False
running=True

pygame.mixer.music.play(-1)

while running:
    moving=False

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.FINGERDOWN:
            x=event.x*WIDTH
            y=event.y*HEIGHT

            if scene=="start":
                if start_button.collidepoint(x,y):
                    scene="choose"

            elif scene=="choose":
                if boy_button.collidepoint(x,y):
                    character="boy"
                    scene="game"
                    pygame.mixer.music.stop()
                elif girl_button.collidepoint(x,y):
                    character="girl"
                    scene="game"
                    pygame.mixer.music.stop()

            elif scene=="game":
                if game_over:
                    player_x=WIDTH//2
                    player_y=HEIGHT//2
                    health=100
                    score=0
                    bullets.clear()
                    enemies.clear()
                    apple=None
                    joystick_finger=None
                    fire_finger=None
                    stick_x=joystick_center[0]
                    stick_y=joystick_center[1]
                    facing_x=1
                    facing_y=0
                    game_over=False

                elif math.hypot(x-joystick_center[0],y-joystick_center[1])<=joystick_radius and joystick_finger is None:
                    joystick_finger=event.finger_id

                elif fire.collidepoint(x,y):
                    if fire_finger is None:
                        fire_finger=event.finger_id

        if event.type==pygame.FINGERMOTION:
            if event.finger_id==joystick_finger:
                x=event.x*WIDTH
                y=event.y*HEIGHT
                dx=x-joystick_center[0]
                dy=y-joystick_center[1]
                distance=math.hypot(dx,dy)

                if distance>joystick_radius:
                    stick_x=joystick_center[0]+dx/distance*joystick_radius
                    stick_y=joystick_center[1]+dy/distance*joystick_radius
                else:
                    stick_x=x
                    stick_y=y

        if event.type==pygame.FINGERUP:
            if event.finger_id==joystick_finger:
                joystick_finger=None
                stick_x=joystick_center[0]
                stick_y=joystick_center[1]

            if event.finger_id==fire_finger:
                fire_finger=None

    if scene=="game" and not game_over:
        move_x=0
        move_y=0

        if joystick_finger is not None:
            dx=stick_x-joystick_center[0]
            dy=stick_y-joystick_center[1]
            distance=math.hypot(dx,dy)

            if distance>5:
                move_x=dx/joystick_radius
                move_y=dy/joystick_radius
                facing_x=dx/distance
                facing_y=dy/distance
                moving=True

        player_x+=move_x*player_speed
        player_y+=move_y*player_speed

        player_x=max(0,min(player_x,WIDTH-player_size))
        player_y=max(0,min(player_y,HEIGHT-player_size))

        player_rect=pygame.Rect(player_x,player_y,player_size,player_size)

        if moving:
            if not pygame.mixer.get_busy():
                walk_sound.play(-1)
        else:
            walk_sound.stop()

        if health<=apple_health_limit and apple is None:
            for attempt in range(100):
                apple_x=random.randint(30,WIDTH-30)
                apple_y=random.randint(30,HEIGHT-30)
                apple_rect=pygame.Rect(apple_x-apple_size,apple_y-apple_size,apple_size*2,apple_size*2)
                safe=True

                for obstacle in obstacles:
                    if apple_rect.colliderect(obstacle):
                        safe=False
                        break

                if apple_rect.colliderect(player_rect):
                    safe=False

                if safe:
                    apple=[apple_x,apple_y]
                    break

        if apple is not None:
            apple_rect=pygame.Rect(apple[0]-apple_size,apple[1]-apple_size,apple_size*2,apple_size*2)

            if player_rect.colliderect(apple_rect):
                health=100
                apple=None

        spawn_timer+=1

        if spawn_timer>70:
            spawn_timer=0
            side=random.randint(0,3)

            if side==0:
                ex=random.randint(0,WIDTH)
                ey=-30
            elif side==1:
                ex=random.randint(0,WIDTH)
                ey=HEIGHT+30
            elif side==2:
                ex=-30
                ey=random.randint(0,HEIGHT)
            else:
                ex=WIDTH+30
                ey=random.randint(0,HEIGHT)

            enemies.append([ex,ey])

        shoot_timer+=1

        if fire_finger is not None and shoot_timer>15:
            shoot_timer=0

            bullet_x=player_x+player_size/2+facing_x*20
            bullet_y=player_y+player_size/2+facing_y*20

            bullets.append([bullet_x,bullet_y,facing_x,facing_y])
            shoot_sound.play()

        for bullet in bullets[:]:
            bullet[0]+=bullet[2]*12
            bullet[1]+=bullet[3]*12

            if bullet[0]<0 or bullet[0]>WIDTH or bullet[1]<0 or bullet[1]>HEIGHT:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            dx=player_x-enemy[0]
            dy=player_y-enemy[1]
            distance=math.hypot(dx,dy)

            if distance!=0:
                enemy[0]+=dx/distance*1.5
                enemy[1]+=dy/distance*1.5

            enemy_rect=pygame.Rect(enemy[0]-20,enemy[1]-20,40,40)

            if enemy_rect.colliderect(player_rect):
                health-=1

                if health<=0:
                    health=0
                    game_over=True
                    walk_sound.stop()

        for bullet in bullets[:]:
            bullet_rect=pygame.Rect(bullet[0]-5,bullet[1]-5,10,10)

            for enemy in enemies[:]:
                enemy_rect=pygame.Rect(enemy[0]-20,enemy[1]-20,40,40)

                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy)

                    if bullet in bullets:
                        bullets.remove(bullet)

                    score+=10
                    break

    if scene=="start":
        screen.fill((25,35,65))

        title=big_font.render("BATTLE ARENA",True,(255,220,50))
        screen.blit(title,(WIDTH//2-title.get_width()//2,100))

        pygame.draw.rect(screen,(40,170,80),start_button,border_radius=20)

        text=font.render("START",True,(255,255,255))
        screen.blit(text,(start_button.centerx-text.get_width()//2,start_button.centery-text.get_height()//2))

        info=small_font.render("Enter the arena and fight!",True,(220,220,220))
        screen.blit(info,(WIDTH//2-info.get_width()//2,HEIGHT-100))

    elif scene=="choose":
        screen.fill((35,45,70))

        title=big_font.render("CHOOSE CHARACTER",True,(255,220,50))
        screen.blit(title,(WIDTH//2-title.get_width()//2,80))

        pygame.draw.rect(screen,(50,100,200),boy_button,border_radius=20)
        pygame.draw.rect(screen,(210,70,130),girl_button,border_radius=20)

        boy_text=font.render("BOY",True,(255,255,255))
        girl_text=font.render("GIRL",True,(255,255,255))

        screen.blit(boy_text,(boy_button.centerx-boy_text.get_width()//2,boy_button.centery-boy_text.get_height()//2))
        screen.blit(girl_text,(girl_button.centerx-girl_text.get_width()//2,girl_button.centery-girl_text.get_height()//2))

    elif scene=="game":
        if not game_over:
            screen.fill((25,120,35))

            for obstacle in obstacles:
                pygame.draw.rect(screen,(80,80,80),obstacle,border_radius=8)

            if apple is not None:
                ax=int(apple[0])
                ay=int(apple[1])

                pygame.draw.circle(screen,(220,30,30),(ax,ay),apple_size)
                pygame.draw.circle(screen,(255,100,100),(ax-6,ay-6),4)
                pygame.draw.ellipse(screen,(30,160,50),(ax+5,ay-18,12,7))
                pygame.draw.line(screen,(70,40,20),(ax,ay-15),(ax+3,ay-22),3)

            center_x=int(player_x+player_size/2)
            center_y=int(player_y+player_size/2)

            if character=="girl":
                body_color=(70,100,220)
            else:
                body_color=(50,150,210)

            pygame.draw.rect(screen,body_color,(center_x-14,center_y-2,28,25),border_radius=8)

            head_x=int(center_x+facing_x*8)
            head_y=int(center_y-15+facing_y*8)

            pygame.draw.circle(screen,(255,210,170),(head_x,head_y),12)

            if character=="girl":
                pygame.draw.circle(screen,(60,30,20),(head_x-int(facing_x*5),head_y-7),10)
            else:
                pygame.draw.circle(screen,(35,25,20),(head_x-int(facing_x*4),head_y-8),9)

            face_x=int(head_x+facing_x*10)
            face_y=int(head_y+facing_y*10)

            pygame.draw.circle(screen,(30,30,30),(face_x,face_y),3)

            gun_start_x=int(center_x+facing_x*12)
            gun_start_y=int(center_y+facing_y*12)
            gun_end_x=int(center_x+facing_x*27)
            gun_end_y=int(center_y+facing_y*27)

            pygame.draw.line(screen,(40,40,40),(gun_start_x,gun_start_y),(gun_end_x,gun_end_y),6)

            for enemy in enemies:
                pygame.draw.circle(screen,(180,30,30),(int(enemy[0]),int(enemy[1])),20)

            for bullet in bullets:
                pygame.draw.circle(screen,(255,230,50),(int(bullet[0]),int(bullet[1])),6)

            pygame.draw.circle(screen,(70,70,70),joystick_center,joystick_radius)
            pygame.draw.circle(screen,(160,160,160),(int(stick_x),int(stick_y)),stick_radius)

            pygame.draw.rect(screen,(170,40,40),fire,border_radius=25)

            fire_text=font.render("FIRE",True,(255,255,255))
            screen.blit(fire_text,(fire.centerx-fire_text.get_width()//2,fire.centery-fire_text.get_height()//2))

            score_text=font.render("Score: "+str(score),True,(255,255,255))
            screen.blit(score_text,(20,20))

            pygame.draw.rect(screen,(60,60,60),(20,60,200,25),border_radius=10)
            pygame.draw.rect(screen,(30,220,60),(20,60,health*2,25),border_radius=10)

        else:
            screen.fill((20,20,20))

            text=big_font.render("GAME OVER",True,(255,60,60))
            screen.blit(text,(WIDTH//2-text.get_width()//2,HEIGHT//2-80))

            score_text=font.render("Score: "+str(score),True,(255,255,255))
            screen.blit(score_text,(WIDTH//2-score_text.get_width()//2,HEIGHT//2))

            restart=font.render("Tap anywhere to restart",True,(255,255,255))
            screen.blit(restart,(WIDTH//2-restart.get_width()//2,HEIGHT//2+60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
