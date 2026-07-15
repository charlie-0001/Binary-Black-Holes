# all of this is chatgpt'd i just wanted to see how AI did it. this will not be used for research.
import pygame
import numpy as np
from pathlib import Path

SCREEN_WIDTH, SCREEN_HEIGHT = 800,800
FOV=np.radians(60)

def read_obj(path):
    verts=[]; tris=[]
    with open(path) as f:
        for line in f:
            p=line.split()
            if not p: continue
            if p[0]=="v":
                verts.append([float(p[1]),float(p[2]),float(p[3])])
            elif p[0]=="f":
                ids=[int(x.split('/')[0])-1 for x in p[1:]]
                if len(ids)==3: tris.append(ids)
                if len(ids)==4:
                    tris.append([ids[0],ids[1],ids[2]])
                    tris.append([ids[0],ids[2],ids[3]])
    return np.array(verts,float), np.array(tris,int)

def rot_y(a):
    c,s=np.cos(a),np.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])

def project(v,cam):
    p=v-cam[:3]
    yaw,pitch=cam[3],cam[4]
    Ry=rot_y(-yaw)
    cp,sp=np.cos(-pitch),np.sin(-pitch)
    Rx=np.array([[1,0,0],[0,cp,-sp],[0,sp,cp]])
    p=Rx@(Ry@p)
    if p[2]<=0.01:return None
    f=1/np.tan(FOV/2)
    x=(p[0]*f/p[2])*SCREEN_WIDTH/2+SCREEN_WIDTH/2
    y=(-p[1]*f/p[2])*SCREEN_HEIGHT/2+SCREEN_HEIGHT/2
    return x,y,p[2]

def main():
    pygame.init()
    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock=pygame.time.Clock()
    verts,tris=read_obj(Path(__file__).parent/"meshes"/"icosphere.obj")
    cam=np.array([0,30,0,0,np.pi/2]) # camera
    ang=0.
    running=True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running = False
        screen.fill((0,0,0))
        ang+=0.01
        R = rot_y(ang)

        offset = np.array([
            10 * np.cos(ang),
            0,
            10 * np.sin(ang)
        ])

        world1 = verts + offset # can be changed to verts @ R.T + offset to add spin on meshes
        world2 = verts - offset  # opposite side
        draw = []

        for world in (world1, world2):
            for tri in tris:
                pts = []
                z = 0
                ok = True

                for i in tri:
                    pr = project(world[i], cam)
                    if pr is None:
                        ok = False
                        break

                    pts.append(pr[:2])
                    z += pr[2]

                if ok:
                    draw.append((z / 3, pts))

        draw.sort(reverse=True)
        for _,pts in draw:
            pygame.draw.polygon(screen,(255,255,255),pts,1)
        pygame.display.flip()
        clock.tick(120)
    pygame.quit()

if __name__=="__main__":
    main()
