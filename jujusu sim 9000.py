import pygame as pyg
#import sys
from pygame.locals import QUIT
import os
import math
import time
import random

pyg.init()
pyg.mixer.init()
game = pyg.display.set_mode((1200, 800))
pyg.display.set_caption('jujustu kaisan')

try:
    os.chdir('jjk')
except:
    pass

'''
todo list:
blue (done)
infinity (done)
domian (done)
red (done)
purple (done)
jogo does a ranged attack (done)
toji does a special attack 
sounds (maybe lost motivation)
info menu (redundent?)
draw an image for the attacks (lost motivation)
sukuna (lost motivation)
blood particles (redundent)
'''

friendlyfire =True
debug=False
lastdebug = 0
#showhitboxes=  False

ops = []
hitboxes = []
other=[] #non important stuff that needs to be drawn but no calculations needed
texts = []

gojopos = [600,400]
gojorot = 0

cursedenergy=1000
gojohealth = 1000

gojoscale = 7
gojoimg = pyg.image.load(os.path.join('gojo.webp'))
gojoimg = pyg.transform.scale(gojoimg,[75,75]) #[gojoimg.get_width()/gojoscale,gojoimg.get_height()/gojoscale]
#gojo size is radius of cirlce hitbox
gojosize=30

domainimg = pyg.image.load(os.path.join('domain.jpg'))
domainimg= pyg.transform.scale(domainimg,[1200,800])

shibuyaimg = pyg.image.load(os.path.join('shibuya.jpg'))
shibuyaimg= pyg.transform.scale(shibuyaimg,[1200,800])
tojiimg = pyg.image.load(os.path.join('toji.webp'))
tojiimg= pyg.transform.scale(tojiimg,[75,75])
tojisize=30

jogoimg = pyg.image.load(os.path.join('jogo.webp'))
jogoimg = pyg.transform.scale(jogoimg,[75,75])
jogosize=30

# sukunaimg = pyg.image.load(os.path.join('sukuna.webp'))
# sukunaimg = pyg.transform.scale(sukunaimg,[75,75])
# sukunasize=30


wave = 0


#[cursed energy cost,when it was last used, cooldown, decay,size, projectile speed]
cursedtech = {
    'infinity': {
        'cost':4,
        'enabled':False,
        'force':.75, #this force will go up by the power of 4 so moving towards it will be easy until suddenly it doesnt get easy
        'distance':150,
        'friction':.25
    }, #achilles tortoise
    'infinite void': 
        {
        'cost': 800,
        'last used': 0,
        'cooldown': 30,
        'decay': 10,
        'enabled':False
        }, #domain expansion
    'red': {
        'cooldown':3.5,
        'cost': 200,
        'damage':80,
        'width':10,
        'force': 55,
        'decay':.25,
        'last used':0
    }, # diverge[200,0,10]
    'blue': {
        'damage':.5,
        'cost' : 100,
        'size':20,
        'force':1.5, #force to enemy
        'effect rad':250, #the effect radius will inverse square law
        'cooldown':8.5,
        'decay':8,
        'speed':1.25, #redundent
        'last used':0,
        'enabled':False

    }, # converge[100,0,7]
    'purple': {
        'size':15,
        'force':15,
        'cost':400,
        'decay':8,
        'damage': 4,
        'born': 0,
        'exist': False,
        'speed': 50,
        'song':False,
        'songborn':0,
        'songtime':30
    }, #imaginary
    'basic': {
        'damage': 7,
        'cost':20, 
        'last used':0,
        'size': 30,
        'dampen':.1,
        'cooldown': 0.15,
        'decay': 0.1,
        'speed': 15
    }, 
    'teleport': {
        'cost':1,
        'cooldown':3.5,
        'last used':0
    }, #touch papers
    'rct': {
        'cost':2,
        'enabled':False,
        'health':1,
    }, # multiple by itself to produce positive cursed energy
    'gravity':{
        'cost':.005,
        'enabled':False,
        'force':2.5/721
    }#this isnt even canon lol
}
#wasd movement
speed = 3.5
movement = [False,False,False,False]

# def inbounds(pos):
#     if pos[0]<0 or 1200<pos[0]:
#         return False
#     if pos[1]<0 or 800<pos[1]:
#         return Falses
#     return True

def nextpos(pos,vel):
    return [pos[0]+vel[0],pos[1]+vel[1]]

def vel2force(vel):
    return (vel[0]**2+vel[1]**2)**1/2

def lerp(p1,p2,v):
    return (1 - (v))*p1 + (v)*p2

def dist(point1,point2):
    return((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**(1/2)

def tojiattack(self,attack):
    tojirot = math.degrees(math.atan2((gojopos[0]-self.pos[0]),(gojopos[1]-self.pos[1])))+90
    if attack=='gun' and (time.time()-self.movesets['gun']['last used'])>self.movesets['gun']['cooldown']:
        tech = self.movesets['gun']
        tech['last used']=time.time()
        new_vel = [
            -1*(math.cos(math.radians(tojirot))*tech['speed']),
            math.sin(math.radians(tojirot))*tech['speed']]
        hitboxes.append(Hitbox(self.pos.copy(),tech['size'],['Gun',self,time.time()],velocity=new_vel,affected=[],col=tech['color'],width=1))
    if attack=='slash': #and (time.time()-self.movesets['slash']['last used'])>self.movesets['slash']['cooldown']:
        tech = self.movesets['slash']
        tech['last used']=time.time()
        for side in range(tech['conseq']):
            tech['angle adjust']+=tech['adjust factor']
            tech['angle adjust']=tech['angle adjust']%360
            #stolen code from polygon project
            inner_angle = (360/tech['conseq'])*side+(tech['angle adjust'])
            inner_end = [
                self.pos[0]+math.cos(math.radians(inner_angle))*self.size*2,
                self.pos[1]+math.sin(math.radians(inner_angle))*-self.size*2
            ]
            
            new_vel=[
                math.cos(math.radians(inner_angle))*tech['speed']*2,
                math.sin(math.radians(inner_angle))*-tech['speed']*2
            ]

            hitboxes.append(Hitbox(inner_end,tech['size'],['Slash',self,time.time()],velocity=new_vel,affected=[],col=tech['color'],width=1))
            # tojirot = math.degrees(math.atan2((gojopos[0]-inner_end[0]),(gojopos[1]-inner_end[1])))+90
            # new_vel = [
            # -1*(math.cos(math.radians(tojirot))*tech['speed']),
            # math.sin(math.radians(tojirot))*tech['speed']]



def jogoattack(self,attack):
    jogorot = math.degrees(math.atan2((gojopos[0]-self.pos[0]),(gojopos[1]-self.pos[1])))+90
    
    if attack=='fireball' and (time.time()-self.movesets['fireball']['last used'])>self.movesets['fireball']['cooldown']:
        #fireball
        self.movesets['fireball']['last used']=time.time()
        for side in range(self.movesets['fireball']['conseq']):
            #stolen code from polygon project
            inner_angle = (360/self.movesets['fireball']['conseq'])*side
            inner_end = [
                self.pos[0]+math.cos(math.radians(inner_angle))*self.size*2,
                self.pos[1]+math.sin(math.radians(inner_angle))*-self.size*2
            ]

            jogorot = math.degrees(math.atan2((gojopos[0]-inner_end[0]),(gojopos[1]-inner_end[1])))+90

            new_vel = [
            -1*(math.cos(math.radians(jogorot))*self.movesets['fireball']['speed']),
            math.sin(math.radians(jogorot))*self.movesets['fireball']['speed']]

            hitboxes.append(Hitbox(inner_end,self.movesets['fireball']['size'],['Fireball',self,time.time()],velocity=new_vel,affected=[],col=self.movesets['fireball']['color'],width=50))
    if attack=='maximum' and (time.time()-self.movesets['maximum']['last used'])>self.movesets['maximum']['cooldown']:
        tech=self.movesets['maximum']
        tech['last used']=time.time()
        new_vel = [
            -1*(math.cos(math.radians(jogorot))*tech['speed']),
            math.sin(math.radians(jogorot))*tech['speed']]
        hitboxes.append(Hitbox(self.pos.copy(),tech['size'],['Maximum',self,time.time()],velocity=new_vel,affected=[],col=tech['color'],width=50))
    
    if attack=='laser':
        tech=self.movesets['laser']
        new_vel = [
        -1*(math.cos(math.radians(jogorot))*tech['speed']),
        math.sin(math.radians(jogorot))*tech['speed']]
        hitboxes.append(Hitbox(self.pos.copy(),tech['size'],['Laser',self,time.time()],velocity=new_vel,affected=[],col=tech['color'],width=50))

def tojimovement(self):
    if self.pos[0] > gojopos[0]:
        self.pos[0]-=self.speed
    if self.pos[0] < gojopos[0]:
        self.pos[0] +=self.speed
    if self.pos[1] < gojopos[1]:
        self.pos[1] +=self.speed
    if self.pos[1] > gojopos[1]:
        self.pos[1] -=self.speed
     
def jogomovement(self):
    if self.pos[0] > gojopos[0] and 0<(self.pos[0]+self.speed)<1200:
        self.pos[0]+=self.speed
    if self.pos[0] < gojopos[0] and 0<(self.pos[0]-self.speed)<1200:
        self.pos[0] -=self.speed
    if self.pos[1] < gojopos[1] and 0<(self.pos[1]-self.speed)<800:
        self.pos[1] -=self.speed
    if self.pos[1] > gojopos[1] and 0<(self.pos[1]+self.speed)<800:
        self.pos[1] +=self.speed

def animate_velocity(pos,vel,friction=0.1,dampen = .12 ,velthres = 15, dmgmulti=.5,owner=None):
    # if ((-1*friction*20)<vel[0]) and (vel[0]<friction*20):
    #     vel[0]=0
    #dampen is the bounceback
    if (owner and hasattr(owner,'owner') and isinstance(owner.owner,list) and owner.blue_affect) and (cursedtech['blue']['enabled']==False):
        owner.blue_affect=False
    
    if owner and hasattr(owner,'owner') and isinstance(owner.owner,list) and owner.owner[0]=='Gun' and vel2force(vel)==0:
        try:
            hitboxes.remove(owner)
        except:
            pass
    if not cursedtech['infinite void']['enabled'] or (hasattr(owner,'owner') and owner.owner[1]=='Gojo') or (not isinstance(owner,Hitbox)):
        #regular
        if not cursedtech['gravity']['enabled'] and not (owner and hasattr(owner,'owner') and isinstance(owner.owner,list) and owner.blue_affect):
            #grav enabled, blue affected, no friction
            #grav enabled, not blue affected, no friction
            #grav disabled, blue affected, no friction
            #grav disabled, not blue affected, friction
            if vel[0]>.25:
                vel[0]-=friction*abs(vel[0])
            elif vel[0]<-.25:
                vel[0]+=friction*abs(vel[0])
            else:
                vel[0]=0
            if vel[1]>.25:
                vel[1]-=friction*abs(vel[1])
            elif vel[1]<-.25:
                vel[1]+=friction*abs(vel[1])
            else:
                vel[1]=0

        if 0<(pos[0]+vel[0]) and (pos[0]+vel[0])<1200:
            pos[0]+=vel[0]
        else:
            #bounce
            vel[0]=-vel[0]*dampen
            if owner and hasattr(owner,'health') and abs(owner.velocity[0]) >=velthres:
                owner.health-=dmgmulti*abs(owner.velocity[0])
            #resets immunity
            if owner and hasattr(owner,'affected') and isinstance(owner.owner,list):
                owner.affected.clear()
                if owner.owner[0]=='Laser' or owner.owner[0]=='Gun':
                    try:
                        hitboxes.remove(owner)
                    except:
                        pass

        if 0<(pos[1]+vel[1]) and (pos[1]+vel[1])<800:
            pos[1]+=vel[1]
        else:
            #bounce
            vel[1]=-vel[1]*dampen
            if owner and hasattr(owner,'health') and abs(owner.velocity[1]) >=velthres:
                owner.health-=dmgmulti*abs(owner.velocity[1])
            #resets immunity
            if owner and hasattr(owner,'affected') and isinstance(owner.owner,list):
                owner.affected.clear()
                if owner.owner[0]=='Laser' or owner.owner[0]=='Gun':
                    try:
                        hitboxes.remove(owner)
                    except:
                        pass
        #i was gonna make nemies bounce off eachother but thats not possible with the way i move enimeis
        # for op in ops:
        #     if op!=owner and owner and not hasattr(owner,'owner') and dist(op.pos,owner.pos)<op.size+owner.size:
        #         print(op,owner)

        

def manage_health(self):
    if self.health<=0:
        ops.remove(self)
        for hitbox in hitboxes:
            if hitbox.owner not in ops and hitbox.owner!=True and not isinstance(hitbox.owner,list):
                hitboxes.remove(hitbox)


class Line:
    def __init__(self,point1,point2,owner,width=1,col=[255,0,0],vel=[0,0]):
        self.point1=point1
        self.point2=point2
        self.vel=vel
        self.width=width
        self.owner= owner
        self.col=col
    def draw(self):
        pyg.draw.line(game,self.col,self.point1,self.point2,self.width)
    def animate(self):
        #only doing this to bypass draw_ops handler
        animate_velocity(self.point1,self.vel)
        animate_velocity(self.point2,self.vel)



# Heres how hitboxes will work, we will have the hitboxes
#gojo body hitbox is true
#any attacks makes hitbox owner a list

class Hitbox:
    def __init__ (self,pos,rad,owner,col=[255,0,0],width=1,velocity=[0,0],affected=[],friction=0,blue_affect=False):
        self.col = col
        self.affected = affected
        self.pos = pos
        self.rad = rad
        self.velocity = velocity
        self.width=width
        self.owner = owner
        self.friction = friction

        self.blue_affect=blue_affect
    def draw(self):
        pyg.draw.circle(game,self.col,self.pos,self.rad,self.width)
        if not isinstance(self.owner,list) and self.owner!=True and self.owner.health>=0:
            self.col=[int((255/-100)*self.owner.health)+255,int((self.owner.health/100)*255),0]
    def animate(self):
        if isinstance(self.owner,list) and not self.owner[0]=='Purple':
            animate_velocity(self.pos,self.velocity,self.friction,owner=self)
        

class Toji:
    def __init__ (self,pos,cooldown=0,speed=1.5,velocity=[0,0],health=100,friction=0.01):
        self.pos = pos
        self.speed = speed
        self.velocity = velocity
        self.cooldown= cooldown
        self.size=30
        self.delay=0.25
        self.randfactor = random.randint(69,420)
        self.health = health
        self.friction = friction
        self.movesets ={
            'basic':{
                'damage':1
            },
            'gun':{
                'damage':25,
                'speed':20,
                'color':[255,0,0],#[125,125,125],
                'cooldown':8,
                'last used':0,
                'decay':20,
                'size':2
            }, #high speed
            'slash':{
                #'last used':0,
                'conseq':2,
                'damage':2,
                #'cooldown':5,
                'decay':4,
                'speed':4,
                'size':10,
                'color':[255,0,0],
                'angle adjust':5,
                'adjust factor':10
            }# aoe
        }

    def draw(self):
        toji_rot = pyg.transform.rotate(tojiimg,0)
        toji_rect = toji_rot.get_rect(center=self.pos)
        game.blit(toji_rot,toji_rect)
    def animate(self):
        animate_velocity(self.pos,self.velocity,friction=self.friction,owner=self)
        manage_health(self)
        tojimovement(self)
        if int(time.time())%8==0 or int(time.time()+self.randfactor)%5 ==0:
            tojiattack(self,'slash')
        if dist(gojopos,self.pos)>60:
            tojiattack(self,'gun')

class Jogo:
    def __init__ (self,pos,speed=.75,velocity=[0,0],health=100,friction=0.01):
        self.pos = pos
        self.speed = speed
        self.velocity = velocity
        self.friction = friction
        self.health = health
        self.size=30
        self.randfactor = random.randint(69,420)
        self.movesets = {
        'fireball':{
            'color': [255,75,0],
            'speed':12,
            'size':7,
            'last used':0,
            'cooldown':1.5,
            'damage':.25, #damage is multipleid by velocity
            'decay':5,
            'conseq':3
            },
        'maximum':{
            'color': [255,0,0],
            'damage':75,
            'decay':8,
            'size':30,
            'cooldown':15,
            'last used':time.time()+15,#cooldown 15
            'speed':5
        },
        'laser':{
            'color': [255,35,0],
            'damage':2,
            'cooldown':7,
            'size':10,
            'speed':15,
            'decay':15,
        }
        }
    def draw(self):
        jogo_rot = pyg.transform.rotate(jogoimg,0)
        jogo_rect = jogo_rot.get_rect(center=self.pos)
        game.blit(jogo_rot,jogo_rect)
    def animate(self):
        animate_velocity(self.pos,self.velocity,friction=self.friction,owner=self)
        manage_health(self)
        distance = dist(self.pos,gojopos)
        jogoattack(self,'fireball')
        if int(time.time()+self.randfactor)%self.movesets['laser']['cooldown']==0 or int(time.time())+self.randfactor %self.movesets['laser']['cooldown']==2:
            jogoattack(self,'laser')
        if distance>500:
            tojimovement(self)
            #far away
        elif 475<distance:
            #good dist
            jogoattack(self,'maximum')
        else:
            #towards you
            jogomovement(self)

class Text:
    #everything in this game needs to be comic sans 
    def __init__ (self,pos,text,color,size,font = "Comic Sans MS"):
        self.pos = pos
        self.text = text
        self.color = color
        self.size = size
        self.font = font
    def draw(self):
        game.blit(pyg.font.SysFont(self.font,self.size).render(self.text,True,self.color),self.pos)


def draw_gojo():
    global gojohealth
    #if gojohealth<=0:
    global gojoimg
    gojo_rotated = pyg.transform.rotate(gojoimg,gojorot)
    gojo_rect = gojo_rotated.get_rect(center=gojopos)
    game.blit(gojo_rotated, gojo_rect)
    #we could multiply by delta time but nah
    if movement[0] and ((gojopos[1]-speed) > 0 and (gojopos[1]-speed) < 800):
        gojopos[1]-=speed
    if movement[1] and ((gojopos[0]-speed) > 0 and (gojopos[1]-speed) < 1200):
        gojopos[0]-=speed
    if movement[2] and ((gojopos[1]+speed) > 0 and (gojopos[1]+speed) < 800):
        gojopos[1]+=speed
    if movement[3] and ((gojopos[0]+speed) > 0 and (gojopos[0]+speed) < 1200):
        gojopos[0]+=speed

def draw_enemies():
    for op in ops:
        op.draw()
        op.animate()


col = [255,0,0]
cur=0
def display_stats():
    texts.clear()
    global cur
    if wave==0:
        increment = 15 #make 255 divisble by increment pls
        forward = (cur+1)%3
        cur=cur%3
        if col[cur]>=col[forward] and col[forward]+increment<=255:
            col[forward]+=increment
        elif col[cur]<=col[forward]:
            if col[cur]-increment>=0:
                col[cur]-=increment
            else:
                cur+=1
        
        txts=['welcome to JJK simulator 9000 WIP (successor of goku simulator 9000)', 'omg i forgot to save the code from friday so this is thursdays snapshot (every bug is now considerd feature)', 'stuff undone: health and cursed energy cap, also sounds', 'g is blue attack will attract r is red will repel', 'q is infity will repel from u', 'e is heal but health doesnt work :(','f teleport to mouse', 'h is domain expansion ', 'make purple by reding the blue very cool', 't will make gravity happen', 'rpess space to go to next wave and yes everythign is comic sans (dont even try changing it)']
        for i,txt in enumerate(txts):
            texts.append(Text([600-len(txt)*5,100+i*20],txt,col,20))
        
    else:
        texts.append(Text([0,0],f'Health: {gojohealth}',[255,0,0],20))
        texts.append(Text([0,20],f'Cursed Energy: {cursedenergy}',[255,0,255],20))
        texts.append(Text([0,40],f'Infinity: {cursedtech["infinity"]["enabled"]}',[0,125,255],20))
        texts.append(Text([150,0],f'RCT: {cursedtech["rct"]["enabled"]}',[255,0,0],20))
        texts.append(Text([150,40],f'Gravity: {cursedtech["gravity"]["enabled"]}',[0,255,0],20))

    for text in texts:
        text.draw()
        #ignore this >:)
        
        if text.font!="Comic Sans MS" and int(time.time())%10==0:
            new_op = Jogo([random.randint(0,1200),random.randint(0,800)])
            ops.append(new_op)
            hitboxes.append(Hitbox(new_op.pos,30,new_op))

            new_op = Toji([random.randint(0,1200),random.randint(0,800)])
            ops.append(new_op)
            hitboxes.append(Hitbox(new_op.pos,30,new_op))


def decaybox(hitbox,tech,remove=hitboxes):
    # hitboxes owner [attack,owner,when it was born]
    if (time.time()-hitbox.owner[2])>tech['decay']:
        try:
            remove.remove(hitbox)
        except:
            pass
        if tech==cursedtech['blue']:
            tech['enabled']=False

#im bad at gernealizing
def decaybox2(hitbox,move,remove=hitboxes):
    if (time.time()-hitbox.owner[2])>hitbox.owner[1].movesets[move]['decay']:
        try:
            remove.remove(hitbox)
        except:
            pass

def draw_others():
    #draw non important
    for obj in other:
        if hasattr(obj,'owner') and obj.owner[0]=='Red':
            decaybox(obj,cursedtech['red'],other)
        obj.draw()

def regen_cursed():
    global gojohealth
    global cursedenergy
    if cursedenergy<1600:
        cursedenergy+=1
    if cursedtech['infinity']['enabled']:
        cursedenergy-=cursedtech['infinity']['cost']
        for op in ops:
            distance = dist(nextpos(op.pos,op.velocity),gojopos)
            if distance<cursedtech['infinity']['distance'] and distance!=0:
                new_angle=(math.atan2(gojopos[0]-op.pos[0], gojopos[1]-op.pos[1]))-90
                #the force will go up by the power fo 4 depending on distance so it starts slow but goes fast
                op.velocity=[
                op.velocity[0]+(math.cos(new_angle)*cursedtech['infinity']['force']*-1*(100**4/(distance**4))),
                op.velocity[1]+(math.sin(new_angle)*cursedtech['infinity']['force'])*(100**4/(distance**4))]

    if cursedtech['rct']['enabled'] and gojohealth<1000:
        cursedenergy-=cursedtech['rct']['cost']
        gojohealth+=cursedtech['rct']['health']

def purple():
    tech = cursedtech['purple']
    if tech['exist']:
        # damage handler
        for hitbox in hitboxes:
            if isinstance(hitbox.owner,list) and hitbox.owner[1] == 'Gojo' and hitbox.owner[0]=='Purple':
                hitbox.rad = (time.time()-tech['born'])*tech['speed']
                for op in ops:
                    if dist(op.pos,hitbox.pos)<hitbox.rad:
                        op.health-=tech['damage']
                for other in hitboxes:
                    if dist(other.pos,hitbox.pos)<hitbox.rad and other!=hitbox and isinstance(other.owner,list):
                        hitboxes.remove(other)
        #decay handelr
        if time.time()-tech['born']>tech['decay']:
            for hitbox in hitboxes:
                if isinstance(hitbox.owner,list) and hitbox.owner[1] == 'Gojo' and hitbox.owner[0]=='Purple':
                    hitboxes.remove(hitbox)
            tech['exist']=False
    if tech['song']:
        #play song for 30 seconds
        if time.time()-tech['songborn']>tech['songtime']:
            tech['song']=False
            pyg.mixer.music.stop()

                
def applygrav(x=0,y=0):
    global cursedenergy
    tech = cursedtech['gravity']
    if tech['enabled']:
        cursedenergy-=int(tech['cost']*dist([600,400],mousePos))
        x = -1*(math.cos(math.radians(gojorot))*tech['force'])*dist([600,400],mousePos)**1.04
        y = math.sin(math.radians(gojorot))*tech['force']*dist([600,400],mousePos)**1.04
        for op in ops:
            op.velocity=[
                    op.velocity[0]+x,
                    op.velocity[1]+y
                ]
        for hitbox in hitboxes:
            if isinstance(hitbox.owner,list) and hitbox.owner[1] != 'Gojo':
                hitbox.velocity=[
                    hitbox.velocity[0]+x,
                    hitbox.velocity[1]+y
                ]

def hitbox_manage():
    global gojohealth
    for hitbox in hitboxes:
        hitbox.animate() 
        if isinstance(hitbox.owner,Toji):
            toji=hitbox.owner
            if dist(toji.pos,gojopos) < tojisize+gojosize and (time.time()-toji.cooldown)>toji.delay:
                #toji gets cool meelee attack that has no projectile so its idfferent
                toji.cooldown = time.time()
                gojohealth-=toji.movesets['basic']['damage']

        if isinstance(hitbox.owner,list):
            #this is an attack
            # hitboxes[attack,owner,when it was born]
            if hitbox.owner[1] == 'Gojo':
                #is attack by gojo
                if hitbox.owner[0]=='Basic':
                    #is basic attack by gojo
                    tech = cursedtech['basic']
                    decaybox(hitbox,cursedtech['basic'])
                    for op in ops:
                        if dist(nextpos(op.pos,op.velocity),hitbox.pos)<(tech['size']+op.size) and op not in hitbox.affected:
                            op.health-=tech['damage']
                            hitbox.affected.append(op)
                            op.velocity=[op.velocity[0]+hitbox.velocity[0]*tech['dampen'],op.velocity[1]+hitbox.velocity[1]*tech['dampen']]
                    for other in hitboxes:
                        if dist(nextpos(other.pos,other.velocity),hitbox.pos)<tech['size'] and isinstance(other.owner,list) and other.owner[1]!='Gojo':
                            deflectforce=25
                            other.velocity=[
                            -1*(math.cos(math.radians(gojorot))*other.velocity[0])+-1*(math.cos(math.radians(gojorot))*deflectforce),
                            math.sin(math.radians(gojorot))*other.velocity[1]+math.sin(math.radians(gojorot))*deflectforce
                            ]
                
                if hitbox.owner[0]=='Blue':
                    # force=.75 #force to mouse
                    # new_angle=(math.atan2(pyg.mouse.get_pos()[0]-hitbox.pos[0], pyg.mouse.get_pos()[1]-hitbox.pos[1]))-90
                    # #hitbox.friction=dist(hitbox.pos,pyg.mouse.get_pos())/100
                    # hitbox.velocity=[
                    # hitbox.velocity[0]+(math.cos(new_angle)*force),
                    # hitbox.velocity[1]+(math.sin(new_angle)*force*-1)]


                    hitbox.pos[0] = lerp(hitbox.pos[0],mousePos[0],.1)
                    hitbox.pos[1] = lerp(hitbox.pos[1],mousePos[1],.1)

                    tech = cursedtech['blue']
                    decaybox(hitbox,cursedtech['blue'])
                    for op in ops:
                        distance = abs(dist(op.pos,hitbox.pos))
                        if distance<tech['effect rad']:
                            if distance>(tech['size']):
                                #math.cos and math.sin only takes radians
                                new_angle=(math.atan2(hitbox.pos[0]-op.pos[0], hitbox.pos[1]-op.pos[1]))-90
                                # new_angle=(math.atan2(pyg.mouse.get_pos()[0]-op.pos[0], pyg.mouse.get_pos()[1]-op.pos[1]))-90
                                #y axis is flipped
                                op.health-=tech['damage']
                                op.velocity=[
                                op.velocity[0]+(math.cos(new_angle)*tech['force']),
                                op.velocity[1]+(math.sin(new_angle)*tech['force']*-1)]
                            else:
                                op.velocity=[0,0]
                    hitboxmulti = 3
                    for otherhitbox in hitboxes:
                        distance = abs(dist(otherhitbox.pos,hitbox.pos))
                        if distance<tech['effect rad'] and isinstance(otherhitbox.owner,list) and otherhitbox.owner[1]!='Gojo':
                            #every attack hitbox that isnt from gojo
                            if distance>(tech['size']):
                                new_angle=(math.atan2(hitbox.pos[0]-otherhitbox.pos[0], hitbox.pos[1]-otherhitbox.pos[1]))-90
                                otherhitbox.velocity=[
                                otherhitbox.velocity[0]+(math.cos(new_angle)*tech['force']*hitboxmulti),
                                otherhitbox.velocity[1]+(math.sin(new_angle)*tech['force']*-1*hitboxmulti)]
                                otherhitbox.blue_affect = True
                            else:
                                otherhitbox.velocity=[0,0]
                        if distance>tech['effect rad']:
                            otherhitbox.blue_affect = False

            if isinstance(hitbox.owner[1],Toji):
                if hitbox.owner[0]=='Gun':
                    decaybox2(hitbox,'gun') 
                    tech = hitbox.owner[1].movesets['gun']
                    if dist(hitbox.pos,gojopos)<(gojosize+tech['size']) and True not in hitbox.affected:
                        hitbox.affected.append(True)
                        gojohealth-=tech['damage']
                        try:
                            hitboxes.remove(hitbox)
                        except:
                            pass

                    if friendlyfire:
                        ffdamp = .01
                        immunity=.75
                        for op in ops:
                        
                            if dist(hitbox.pos,op.pos)<(op.size+tech['size']) and op not in hitbox.affected:
                                if op!=hitbox.owner[1] and time.time()-hitbox.owner[2]>immunity:
                                    op.health-=tech['damage']
                                    hitbox.affected.append(op)
                                    try:
                                        hitboxes.remove(hitbox)
                                    except:
                                        pass
                    
                if hitbox.owner[0]=='Slash':
                    tech = hitbox.owner[1].movesets['slash']
                    decaybox2(hitbox,'slash') 
                    if dist(hitbox.pos,gojopos)<(gojosize+tech['size']) and True not in hitbox.affected:
                        hitbox.affected.append(True)
                        gojohealth-=tech['damage']
                        try:
                            hitboxes.remove(hitbox)
                        except:
                            pass

                    if friendlyfire:
                        ffdamp = .24
                        immunity=.1
                        for op in ops:
                        
                            if dist(hitbox.pos,op.pos)<(op.size+tech['size']) and op not in hitbox.affected:
                                if op!=hitbox.owner[1] and time.time()-hitbox.owner[2]>immunity:
                                    op.health-=tech['damage']
                                    hitbox.affected.append(op)
                                    try:
                                        hitboxes.remove(hitbox)
                                    except:
                                        pass


            if isinstance(hitbox.owner[1],Jogo):
                #attacj from jogo
                if hitbox.owner[0]=='Fireball':
                    decaybox2(hitbox,'fireball')
                    tech = hitbox.owner[1].movesets['fireball']
                    if dist(hitbox.pos,gojopos)<(gojosize+tech['size']) and True not in hitbox.affected:
                        dmg = int(math.ceil(tech['damage']*vel2force(hitbox.velocity)**.2))
                        if dmg>=16:
                            dmg=16
                        if dmg<=0:
                            dmg=1
                        gojohealth-=dmg
                        #lol only you get immunity not the ops
                        hitbox.affected.append(True)
                            
                    #friendly fire
                    if friendlyfire:
                        ffdamp = .01
                        immunity=.75
                        for op in ops:
                            if dist(hitbox.pos,op.pos)<(op.size+tech['size']) and op not in hitbox.affected:
                                if op!=hitbox.owner[1] and time.time()-hitbox.owner[2]>immunity:
                                    dmg = int(math.ceil(tech['damage']*vel2force(hitbox.velocity)**.2)*ffdamp)
                                    if dmg>=16:
                                        dmg=16
                                    if dmg<=0:
                                        dmg=1
                                    op.health-=dmg
                                    hitbox.affected.append(op)
                                else:
                                    #damage self
                                    if time.time()-hitbox.owner[2]>immunity:
                                        dmg = int(math.ceil(tech['damage']*vel2force(hitbox.velocity)**.2)*ffdamp)
                                        if dmg<=0:
                                            dmg=1
                                        if dmg>=16:
                                            dmg=16
                                        op.health-=dmg
                                        hitbox.affected.append(hitbox.owner[1])
                if hitbox.owner[0]=='Maximum':
                    decaybox2(hitbox,'maximum')
                    tech = hitbox.owner[1].movesets['maximum']
                    if dist(hitbox.pos,gojopos)<(gojosize+tech['size']) and True not in hitbox.affected:
                        hitbox.affected.append(True)
                        gojohealth-=tech['damage']
                    
                    # i should really get a friendlyfire function
                    if friendlyfire:
                        ffdamp = .01
                        immunity=.75
                        for op in ops:
                        
                            if dist(hitbox.pos,op.pos)<(op.size+tech['size']) and op not in hitbox.affected:
                                if op!=hitbox.owner[1] and time.time()-hitbox.owner[2]>immunity:
                                    op.health-=tech['damage']
                                    hitbox.affected.append(op)
                                else:
                                    #damage self
                                    if time.time()-hitbox.owner[2]>immunity:
                                        tech['damage']
                                        hitbox.affected.append(hitbox.owner[1])
                if hitbox.owner[0]=='Laser':
                    decaybox2(hitbox,'laser')
                    tech = hitbox.owner[1].movesets['laser']
                    if dist(hitbox.pos,gojopos)<(gojosize+tech['size']) and True not in hitbox.affected:
                        hitbox.affected.append(True)
                        gojohealth-=tech['damage']

                    #adding an extra comment so ican reach 1000 lines soon
                    #lol no friiendly fire function jsut ctrl c and ctrl v
                    if friendlyfire:
                        ffdamp = .01
                        immunity=.75
                        for op in ops:
                        
                            if dist(hitbox.pos,op.pos)<(op.size+tech['size']) and op not in hitbox.affected:
                                if op!=hitbox.owner[1] and time.time()-hitbox.owner[2]>immunity:
                                    op.health-=tech['damage']
                                    hitbox.affected.append(op)
                                else:
                                    #damage self
                                    if time.time()-hitbox.owner[2]>immunity:
                                        tech['damage']
                                        hitbox.affected.append(hitbox.owner[1])

            if cursedtech['infinity']['enabled'] and hitbox.owner[1]!='Gojo':
                #checks if its not gojos attack
                distance = dist(nextpos(hitbox.pos,hitbox.velocity),gojopos)
                if distance<cursedtech['infinity']['distance'] and distance!=0:
                    new_angle=(math.atan2(gojopos[0]-hitbox.pos[0], gojopos[1]-hitbox.pos[1]))-90
                    #the force will go up by the power fo 4 depending on distance so it starts slow but goes fast
                    factor = 4
                    hitbox.velocity=[
                    hitbox.velocity[0]+(math.cos(new_angle)*cursedtech['infinity']['force']*-1*(150**4/(distance**factor))),
                    hitbox.velocity[1]+(math.sin(new_angle)*cursedtech['infinity']['force'])*(150**4/(distance**factor))]

                    hitbox.friction=cursedtech['infinity']['friction']#250/dist(gojopos,hitbox.pos)
                if distance<35:
                    try:
                        hitboxes.remove(hitbox)
                    except:
                        pass

            
                             

def start_game():
    ops.clear()
    hitboxes.clear()
    texts.clear()
    #ops.append(Toji([800,400],health=math.inf,speed=0))
    #ops.append(Jogo([609,400]))
    hitboxes.append(Hitbox(gojopos,30,True))
    for op in ops:
        hitboxes.append(Hitbox(op.pos,30,op))

start_game()

while True:

    if cursedtech['infinite void']['enabled']:
        game.blit(domainimg,[0,0])
        for op in ops:
            op.speed=op.speed/4

        # for hitbox in hitboxes:
        #     if isinstance(hitbox.owner,list) and hitbox.owner[1]!='Gojo':
        #         hitbox.friction=1

        if (time.time()-cursedtech['infinite void']['last used'])>cursedtech['infinite void']['decay']:
            cursedtech['infinite void']['enabled'] = False
    else:
        game.blit(shibuyaimg,[0,0])

    mouse = pyg.mouse
    mousePos=mouse.get_pos()
    mouseState=mouse.get_pressed()
    clock = pyg.time.Clock()
    dt = clock.tick(120)


    for action in pyg.event.get():
        if action.type == QUIT:
            quit()
        if action.type==pyg.KEYDOWN:
            if action.key == pyg.K_w:
                movement[0]=True
            if action.key ==pyg.K_a:
                movement[1]=True
            if action.key ==pyg.K_s:
                movement[2]=True
            if action.key ==pyg.K_d:
                movement[3]=True

        if action.type==pyg.KEYUP:
            if action.key == pyg.K_w:
                movement[0]=False
            if action.key ==pyg.K_a:
                movement[1]=False
            if action.key ==pyg.K_s:
                movement[2]=False
            if action.key ==pyg.K_d:
                movement[3]=False
            
            if action.key  == pyg.K_SPACE and len(ops)<=0:
                wave+=1
                for i in range(int(wave*5)):
                    chose = random.randint(0,1)
                    x,y = random.randint(0,1200), random.randint(0,800)
                    if chose:
                        new_op = Toji([x,y],velocity=[0,0])
                        ops.append(new_op)
                        hitboxes.append(Hitbox(new_op.pos,30,new_op))
                    else:
                        new_op = Jogo([x,y],velocity=[0,0])
                        ops.append(new_op)
                        hitboxes.append(Hitbox(new_op.pos,30,new_op))


            if action.key==pyg.K_g and (time.time()-cursedtech['blue']['last used']) >= cursedtech['blue']['cooldown']:
                tech=cursedtech['blue']
                tech['last used'] = time.time()
                cursedenergy-=tech['cost']
                tech['enabled']=True
                hitboxes.append(Hitbox(gojopos.copy(),tech['size'],['Blue','Gojo',time.time()],velocity=[0,0],affected=[],col=[0,0,255],width=50,friction=.05))
            
            if action.key==pyg.K_q:
                cursedtech['infinity']['enabled']=not cursedtech['infinity']['enabled']
                for hitbox in hitboxes:
                    if hitbox.owner==True:
                        if cursedtech['infinity']['enabled']:
                            hitbox.col=[0,0,255]
                        else:
                            hitbox.col=[255,0,0]

            if action.key==pyg.K_e:
                cursedtech['rct']['enabled']=not cursedtech['rct']['enabled']
            
            if action.key==pyg.K_r and (time.time()-cursedtech['red']['last used']) >= cursedtech['red']['cooldown']:
                tech=cursedtech['red']
                cursedenergy-=tech['cost']
                tech['last used'] = time.time()
                endpos = [(x-gojopos[i])*850 for i,x in enumerate(mousePos)]
                other.append(Line(gojopos.copy(),endpos,['Red','Gojo',time.time()],width=tech['width'],vel=[0,0]))
                for op in ops: 
                    #prepare for desmos trash code and math combo reversal technique smashing them together to form imaginary code https://www.desmos.com/calculator/nkf7zbxlob
                    a=op.pos[0]
                    b=-op.pos[1]
                    n,m=gojopos
                    c,d=mousePos
                    s=(d-m)/0.01 if (c-n)==0 else (d-m)/(c-n)
                    r=30
                    #dist(mousePos,op.pos)<dist(gojopos,op.pos)
                    if (2*b*s+2*m*s-2*a-2*n*(s**2))**2-4*(s**2+1)*(a**2-r**2+m**2+2*b*m+b**2-2*m*n*s-2*b*n*s+(n*s)**2)>=0 and (dist(mousePos,op.pos)-dist(gojopos,op.pos)<0 or dist(op.pos,mousePos)-dist(gojopos,mousePos)<0):
                        # to fix backwards check the distance from toji to mouse to gojo theres a difference in distance
                        new_vel = [
                                op.velocity[0]+(-1*math.cos(math.radians(gojorot))*tech['force']) if abs(op.velocity[0])<abs((-1*math.cos(math.radians(gojorot))*tech['force'])) else 0,
                                op.velocity[1]+(math.sin(math.radians(gojorot))*tech['force']) if abs(op.velocity[1]) < abs((math.sin(math.radians(gojorot))*tech['force'])) else 0]
                        op.velocity=new_vel
                        op.health-=tech['damage']
                for hitbox in hitboxes:
                    a=hitbox.pos[0]
                    b=-hitbox.pos[1]
                    n,m=gojopos
                    c,d=mousePos
                    s=(d-m)/0.01 if (c-n)==0 else (d-m)/(c-n)
                    r=30

                    if (2*b*s+2*m*s-2*a-2*n*(s**2))**2-4*(s**2+1)*(a**2-r**2+m**2+2*b*m+b**2-2*m*n*s-2*b*n*s+(n*s)**2)>=0 and (dist(mousePos,hitbox.pos)-dist(gojopos,hitbox.pos)<0 or dist(hitbox.pos,mousePos)-dist(gojopos,mousePos)<0):
                        if isinstance(hitbox.owner,list) and hitbox.owner[0]=='Blue' and not cursedtech['purple']['exist']:
                            purptech=cursedtech['purple']
                            hitboxes.append(Hitbox(hitbox.pos,purptech['size'],['Purple','Gojo',time.time()],velocity=[0,0],affected=[],col=[125,0,225],width=1500,friction=10000))
                            hitboxes.remove(hitbox)
                            pyg.mixer.music.load('gojosong.mp3')
                            pyg.mixer.music.set_volume(.35)
                            pyg.mixer.music.play()

                            cursedenergy-=purptech['cost']
                            purptech['exist']=True
                            purptech['song']=True
                            purptech['songborn']=time.time()
                            purptech['born']=time.time()

                        new_vel = [
                                hitbox.velocity[0]+(-1*math.cos(math.radians(gojorot))*tech['force']) if abs(hitbox.velocity[0])< abs((-1*math.cos(math.radians(gojorot))*tech['force'])) else 0,
                                hitbox.velocity[1]+(math.sin(math.radians(gojorot))*tech['force']) if abs(hitbox.velocity[1])<abs((math.sin(math.radians(gojorot))*tech['force'])) else 0]

                        hitbox.velocity=new_vel


            if action.key == pyg.K_f and (time.time()-cursedtech['teleport']['last used']) >= cursedtech['teleport']['cooldown']:
                tech=cursedtech['teleport']
                # newpos=[
                #     gojopos[0]+-1*(math.cos(math.radians(gojorot))*tech['distance']),
                #     gojopos[1]+math.sin(math.radians(gojorot))*tech['distance']
                # ]
                newpos =list(mousePos)
                if 0<newpos[0]<1200 and 0<newpos[1]<800:
                    tech['last used'] = time.time()
                    cursedenergy-=int(tech['cost']*dist(gojopos,newpos))
                    gojopos=newpos
                    for hitbox in hitboxes:
                        if hitbox.owner==True:
                            hitbox.pos=gojopos

            if action.key == pyg.K_h:
                tech=cursedtech['infinite void']
                if cursedtech['infinite void']['enabled']:
                    tech['enabled']=False
                if (time.time()-cursedtech['infinite void']['last used']) > cursedtech['infinite void']['cooldown'] and not cursedtech['infinite void']['enabled']:
                    tech['enabled']=True
                    tech['last used']=time.time()
            
            
            if action.key==pyg.K_t :
                tech=cursedtech['gravity']
                tech['enabled'] = not tech['enabled']

    
    if mouseState[0] and (time.time()-cursedtech['basic']['last used']) >= cursedtech['basic']['cooldown']:
        #players basic attack
        cursedtech['basic']['last used'] = time.time()
        tech = cursedtech['basic']
        #newpos = [position[0]+ math.cos(math.radians(rotation)*(usersize+tech['size'])),gojopos[1]+ math.sin(math.radians(rotation))*(usersize+tech['size'])]
        new_vel = [
                -1*(math.cos(math.radians(gojorot))*tech['speed']),
                math.sin(math.radians(gojorot))*tech['speed']]
        cursedenergy-=tech['cost']
        hitboxes.append(Hitbox(gojopos.copy(),tech['size'],['Basic','Gojo',time.time()],velocity=new_vel,affected=[]))

    #make it when debug is cool
    if mouseState[2] and debug and (time.time()-lastdebug)>2:
        #debug
        lastdebug = time.time()
        force = 15
        new_vel = [
                (math.cos(math.radians(gojorot))*force),
                -1*math.sin(math.radians(gojorot))*force]
        
        #hitboxes.append(Hitbox(list(mousePos),20,['Debug','Debug',time.time()],velocity=new_vel,affected=[],friction=.9))
        

        new_op = Toji(list(mousePos),velocity=[0,0])
        ops.append(new_op)
        hitboxes.append(Hitbox(new_op.pos,30,new_op))

    if (mousePos[1]-gojopos[1]) !=0:
        #atan 2 knows the difference between -1/1 and 1/-1
        gojorot = math.degrees(math.atan2((mousePos[0]-gojopos[0]),(mousePos[1]-gojopos[1])))+90

    purple()
    applygrav()
    draw_enemies()
    display_stats()
    draw_gojo()
    hitbox_manage()
    regen_cursed()
    draw_others()
    #remove this later
    for hitbox in hitboxes:
        hitbox.draw()

    pyg.display.update()