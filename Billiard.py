import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import combinations
from celluloid import Camera
from copy import deepcopy

ball_r = 5.73/2
tableW = 254
tableH = 127

def elastic_collision(b1,b2):
    """Perfectly elastic collision between 2 balls.

    Args:
        pos1: Center of the first ball.
        vel1: Velocity of the first ball.
        mass1: Mass of the first ball.
        pos2: Center of the second ball.
        vel2: Velocity of the second ball.
        mass2: Mass of the second ball.

    Return:
        Two velocities after the collision.

    """

    pos1 = b1.pos
    pos2 = b2.pos
    vel1 = b1.vel
    vel2 = b2.vel

    # switch to coordinate system of ball 1
    pos_diff = np.subtract(pos2, pos1)
    vel_diff = np.subtract(vel2, vel1)

    pos_dot_vel = np.dot(pos_diff, vel_diff)
    assert pos_dot_vel < 0  # colliding balls do not move apart

    dist_sqrd = np.dot(pos_diff, pos_diff)

    bla = 2 * (pos_dot_vel * pos_diff) / ((2) * dist_sqrd)
    vel1 += bla
    vel2 -= bla
    return vel1, vel2

def dist(bs):
    b1, b2 = bs
    dist = np.hypot(b1.pos[0]-b2.pos[0],b1.pos[1]-b2.pos[1])
    return dist


def iscol(bs):
    if dist(bs) <= 2*ball_r:
        return True
    else: return False

def isout(b):
    if b.pos[0]-ball_r <= 0:
        b.vel[0] = -b.vel[0]
    elif b.pos[0]+ball_r >= tableW:
        b.vel[0] = -b.vel[0]
    
    if b.pos[1]-ball_r <= 0:
        b.vel[1] = -b.vel[1]
    elif b.pos[1]+ball_r >= tableH:
        b.vel[1] = -b.vel[1]
    

class Board:
    def __init__(self,Balls):
        self.W = tableW
        self.H = tableH
        self.N = len(Balls)
        self.holes = [np.array([0+ball_r,0+ball_r]),np.array([tableW//2,0+ball_r//2]),np.array([tableW-ball_r,0+ball_r]),np.array([0+ball_r,tableH-ball_r]),np.array([tableW//2,tableH-ball_r//2]),np.array([tableW-ball_r,tableH-ball_r])]
        self.balls = Balls
        self.cntballs = len(Balls)
        self.play_ball = self.balls[0]
        self.last_ball = self.balls[-1]


    def checkrestballs(self):
        for ball in self.balls:
            if any(ball.vel):
                break
        else:
            return False
        return True

    def checkcollisionballs(self):
        col_group = []
        for balls_idx in combinations(range(self.cntballs),2):
            balls = [self.balls[idx] for idx in balls_idx]
            if iscol(balls):
                col_group.append(balls)
        return col_group

    

    

    def playtakeshot(self,F,interval=1):

        fig = plt.gcf()
        tables = [[0, 0], [0, self.H], [self.W, self.H], [self.W, 0]]
        ax = plt.gca()
        line = plt.Polygon(tables, closed=True, fill=True, edgecolor='r', fc='green', alpha=0.3, zorder=0)
        ax.add_patch(line)
        camera = Camera(fig)



        self.balls[0].getforce(F)
        cnt = 0
        while self.checkrestballs():
            cnt += 1
            col_group = self.checkcollisionballs()


            for b1, b2 in col_group:
                # print('col!')
                # print(b1,b2)
                b1.vel, b2.vel = elastic_collision(b1,b2)



            for ball in self.balls:
                ball.update()
                isout(ball)
                #circle = plt.Circle(ball.pos, ball.r, fc=ball.color)
                if not cnt%interval:
                    circle = plt.Circle(ball.pos[:], ball.r, fc=ball.color)
                    circle = deepcopy(circle)
                    ax.add_patch(circle)


                # print(ball.vel, ball.pos)
            if not cnt % interval:
                line = plt.Polygon(tables, closed=True, fill=True, edgecolor='r', fc='green', alpha=0.5, zorder=0)
                ax.add_patch(line)
                plt.xlim(-20, self.W + 20)
                plt.ylim(-10, self.H + 10)
                plt.axis('scaled')
                camera.snap()
            # for _ in camera._photos:
            #     print(_)
            #
            # print('----')
        if not cnt % interval:
            plt.xlim(-20, self.W+20)
            plt.ylim(-10, self.H+10)
            plt.axis('scaled')

        animation = camera.animate(blit=True, interval=10)
        print(cnt)
        animation.save('play.gif')



    def play(self,F,flag=False):

        if flag:
            out = []

        self.balls[0].getforce(F)
        cnt = 0
        sub = []
        while self.checkrestballs():
            cnt += 1
            col_group = self.checkcollisionballs()


            for b1, b2 in col_group:
                b1.vel, b2.vel = elastic_collision(b1,b2)

            for ball in self.balls:
                ball.update()
                isout(ball)
                # print(ball.vel, ball.pos)
                if flag and cnt%100:
                    sub.append(ball.pos)

            if flag and cnt%100:
                out.append(sub)
                sub = []

        #print(cnt)
        if flag:
            return out

    def plot(self):
        plt.axes()
        ax = plt.gca()
        tables = [[0, 0], [0, self.H], [self.W, self.H], [self.W, 0]]
        line = plt.Polygon(tables, closed=True, fill=True, edgecolor='r', fc='green', alpha=0.3, zorder=0)


        for ball in self.balls:
            circle = plt.Circle(ball.pos, ball.r, fc=ball.color)
            ax.add_patch(circle)

        ax.add_patch(line)
        plt.axis('scaled')
        plt.show()

    def multiplot(self,data):
        plt.axes()
        ax = plt.gca()
        tables = [[0, 0], [0, self.H], [self.W, self.H], [self.W, 0]]
        line = plt.Polygon(tables, closed=True, fill=True, edgecolor='r', fc='green', alpha=0.3, zorder=0)

        ##


class Ball():
    def __init__(self,pos):
        self.pos = pos
        self.vel = np.zeros(2, dtype=float)
        self.r = 5.73/2
        self.color = None

    def getforce(self,F,dt=0.1):
        self.vel += F*dt

    def update(self):
        self.pos += self.vel
        self.vel *= 0.999

        if np.hypot(*self.vel) < 0.01:
            self.vel = np.zeros(2, dtype=float)

    def __repr__(self):
        return str(self.pos)+'+'+str(self.vel)+'*dt'



if __name__ == '__main__':
    W = 254
    H = 127
    Balls = []
    Ball_pos = [np.array([W*3/5,H*0.8]),np.array([W*2/4,0.2*H]),np.array([W*3/5,H/2])]
    Ball_color = ['w','r','k']
    for idx in range(len(Ball_pos)):
        b = Ball(Ball_pos[idx])
        b.color = Ball_color[idx]
        Balls.append(b)
    board = Board(Balls)
    #plot(board)
    F = np.array([5,0.8])
    Final = True
    #plot(board)

    # if Final:
    #     matplotlib.use('Agg')
    #     board.playtakeshot(F)
    #
    # else:
    #     board.plot()
    #     board.play(F)
    #     board.plot()


    def algorithm(board):
        def findthepath(x,y):
            #todo
            #   단위백터
            #   시작 점 -> 끝 점
            #   두 공 제외하고 다른 공이 경로에 있으면 False 출력
            pass


        stack = []
        #self.holes = [np.array([0,0]),np.array([127,0]),np.array([254,0]),np.array([0,127]),np.array([127,127]),np.array([254,127])]
        for Holl in board.holes:
            #Holl = board.holes[2]
            #목적구
            objball=board.balls[1].pos
            #수구
            myball = board.balls[0].pos

            objballtoholev = Holl - objball
            tmpv = np.hypot(*objballtoholev)
            #목적 위치
            togoball = objball - 2*ball_r*objballtoholev/tmpv

            # print(myball)
            # print(objball)
            # print(Holl)
            # print(togoball)
            F_dir = (togoball - myball)/np.hypot(*(togoball - myball))
            objectballv = np.dot(objballtoholev / tmpv, F_dir)
            if objectballv <= 0:
                continue
            # print('F_dir',F_dir)
            # print('obj',objectballv)
            F = F_dir*3/objectballv
            #F = F/200
            # 목적구의 필요 속도
            # print(objectballv)
            # print(F)
            if objectballv <= 0:
                continue
            stack.append([np.hypot(*F),F])

        stack.sort()

        return stack[0][1:][0]


    F = algorithm(board)
    print(F)
    # board.plot()
    # board.play(F)
    # board.plot()

    matplotlib.use('Agg')
    board.playtakeshot(F,40)