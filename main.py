from objects import Vector, Simulation, Planet, BasicObject
from setup import objects
import pygame as pg
import time


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
TRACE_COLOR = (12, 200, 12)
DISTANCE_COLOR = (255, 0, 0, 128)

# scale: the amount of pixel 1 meter represents
SCALE = 1*10**(-8)

# how many "fake" seconds one real second represents
TIME_SCALE = 1

# graphics configuration
FOLLOW_CENTER = False   # can be toggled by pressing f
PAUSE = True   # can be toggled by pressing p
SHOW_VELOCITY = True    # v
GRAVITY = True  # g
COLLISION = True    # c
AUTO_SCALE = True   # a
SHOW_TRACE = True   # t
TRACE_LENGTH = 1000
SHOW_INFO = True    # i
SHOW_RADIUS = True  # r
REAL_DIAMETER = True   # d
WINDOW_SIZE = (1920, 1080)
SHOW_NAMES = False  # n


def calculate_offset(center: Vector) -> Vector:
    """
    calculate the offset needed to focus on center
    """
    size_off= Vector.from_cartesian(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2)
    return center - size_off


def calculate_scale(window_size: tuple, system_size: Vector) -> float:
    x_size = window_size[0] / (system_size.x if system_size.x != 0 else 1)
    y_size = window_size[1] / (system_size.y if system_size.y != 0 else 1)

    return min(x_size/2.5, y_size/2.5)


def handle_pygame_events() -> None:
    global FOLLOW_CENTER, PAUSE, SCALE, SHOW_VELOCITY
    global GRAVITY, AUTO_SCALE, COLLISION, SHOW_TRACE, SHOW_INFO
    global REAL_DIAMETER, SHOW_RADIUS, SHOW_NAMES
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                print(f"quitting...")
                pg.quit()
                exit()

            case pg.KEYDOWN:
                match event.key:
                    case pg.K_f:
                        FOLLOW_CENTER = not FOLLOW_CENTER

                    case pg.K_p:
                        PAUSE = not PAUSE

                    case pg.K_v:
                        SHOW_VELOCITY = not SHOW_VELOCITY

                    case pg.K_g:
                        GRAVITY = not GRAVITY

                    case pg.K_a:
                        AUTO_SCALE = not AUTO_SCALE

                    case pg.K_c:
                        COLLISION = not COLLISION

                    case pg.K_t:
                        SHOW_TRACE = not SHOW_TRACE

                    case pg.K_i:
                        SHOW_INFO = not SHOW_INFO

                    case pg.K_d:
                        REAL_DIAMETER = not REAL_DIAMETER

                    case pg.K_r:
                        SHOW_RADIUS = not SHOW_RADIUS

                    case pg.K_n:
                        SHOW_NAMES = not SHOW_NAMES

            case pg.MOUSEBUTTONDOWN:
                match event.button:
                    case 4:
                        SCALE += SCALE*0.1

                    case 5:
                        SCALE -= SCALE*0.1


def main() -> None:
    """
    Runs the program
    """
    global SCALE
    screen = pg.display.set_mode(WINDOW_SIZE, pg.SCALED)
    surface0 = pg.Surface(WINDOW_SIZE, pg.SRCALPHA, 32)
    surface1 = pg.Surface(WINDOW_SIZE, pg.SRCALPHA, 32)
    surface2 = pg.Surface(WINDOW_SIZE, pg.SRCALPHA, 32)
    font = pg.font.SysFont(None, 24)
    pg.display.set_caption("Gravity Sim")
    pg.mouse.set_visible(False)

    # set initial Objects

    sim = Simulation(objects)

    SCALE = calculate_scale(WINDOW_SIZE, sim.size)
    orig_scale = SCALE

    # so you can position your objects better
    print(f"total grid size: {WINDOW_SIZE[0] / SCALE}x{WINDOW_SIZE[1] / SCALE}")

    def mass_scale_multiplier() -> float:
        return 20 / (sim.total_mass / len(sim.objects))

    start = time.perf_counter()
    offset = calculate_offset(sim.gravity_center*SCALE)
    while True:
        # calculate physics
        now = time.perf_counter()
        dt = now-start
        if not PAUSE:
            sim.iter((dt)*TIME_SCALE, gravity=GRAVITY, collision=COLLISION)
        start = now

        # draw objects
        screen.fill(BLACK)
        surface0.fill(BLACK)
        surface1.fill((0, 0, 0, 0))
        surface2.fill((0, 0, 0, 0))
        if FOLLOW_CENTER:
            offset = calculate_offset(sim.gravity_center*SCALE)

        # scale the simulation if enabled
        if AUTO_SCALE:
            tmp = calculate_scale(WINDOW_SIZE, sim.size)
            SCALE = min(tmp, SCALE)

        # draw center of mass
        gc = sim.gravity_center
        gc_pos = gc.x * SCALE - offset.x, gc.y * SCALE - offset.y
        pg.draw.circle(surface2, RED, gc_pos, 2)

        # iterate objects and draw them
        for element in sim.objects:
            element: BasicObject | Planet
            # calculate position and scale
            pos = element.position.x*SCALE-offset.x, element.position.y*SCALE-offset.y
            scale = element.mass*mass_scale_multiplier()*(SCALE/orig_scale)
            scale = scale if scale > 1 else 1

            # if the object is a planet and REAL_DIAMETER is true,
            # set the size of the sphere to the correct size
            scale = scale
            if type(element) == Planet and REAL_DIAMETER:
                scale = (element.diameter/2) * SCALE
                scale = 1 if scale < 1 else scale

            # draw object
            pg.draw.circle(surface1, WHITE, pos, scale)

            # draw trace
            if SHOW_TRACE:
                for i, trace in enumerate(element.trace[-TRACE_LENGTH::]):
                    pos = trace.x*SCALE-offset.x, trace.y*SCALE-offset.y
                    pg.draw.circle(surface0, TRACE_COLOR+(i*(255/TRACE_LENGTH),), pos, 1)

            # draw center line
            if SHOW_RADIUS:
                gc_vec = Vector.from_cartesian(*gc_pos)
                radius = gc_vec - Vector.from_cartesian(*pos)
                pg.draw.line(surface0, DISTANCE_COLOR, gc_pos, pos)
                r = font.render(f"r={round(radius.length/SCALE, 2)}m", True, DISTANCE_COLOR)
                r_pos = gc_vec - radius/2
                surface0.blit(r, (r_pos.x, r_pos.y))

            # draw velocity label and direction
            if SHOW_VELOCITY:
                velocity = font.render(f"{round(element.velocity.length, 3)} m/s", True, BLUE)
                surface0.blit(velocity, (pos[0]+scale, pos[1]-scale))

                tmp = Vector.from_polar(angle=element.velocity.angle, length=scale*2)
                p2x = pos[0] + tmp.x
                p2y = pos[1] + tmp.y
                pg.draw.line(surface0, BLUE, pos, (p2x, p2y))

            # # draw name label
            if type(element) == Planet and SHOW_NAMES:
                name = font.render(element.name, True, RED)
                surface0.blit(name, (pos[0]+scale, pos[1]+scale))

        # draw toggle infos
        inf = [
            f"FPS: {round(1/dt, 1)}",
            f"Gravity: {GRAVITY}",
            f"Collision: {COLLISION}",
            f"scale: {SCALE}",
            f"Auto-scale: {AUTO_SCALE}",
            f"real Diameter: {REAL_DIAMETER}",
            f"Pause: {PAUSE}",
            f"Follow center: {FOLLOW_CENTER}",
            f"show Velocity: {SHOW_VELOCITY}",
            f"show Radius: {SHOW_RADIUS}",
            f"show Trace: {SHOW_TRACE}",
            f"show Names: {SHOW_NAMES}"
        ]

        if SHOW_INFO:
            for i, line in enumerate(inf):
                img = font.render(line, True, WHITE)
                surface2.blit(img, (0, 20*i))

        # handle pygame events
        handle_pygame_events()

        # update screen
        screen.blit(surface0, (0, 0))
        screen.blit(surface1, (0, 0))
        screen.blit(surface2, (0, 0))
        pg.display.update()


if __name__ == "__main__":
    try:
        pg.init()
        pg.font.init()
        main()

    finally:
        pg.quit()
        pg.font.quit()
