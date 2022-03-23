"""
Classes of all the physics objects
Author:
Nilusink
"""
import typing as tp
import numpy as np

# gravitational constant
G: float = 6.67408e-11

# pi
PI = 3.1415926535897932384626433832795028841971

# one astronomical unit
AU = 149597870700


class Vector:
    x: float
    y: float
    angle: float
    length: float

    # creation of new elements
    def __init__(self) -> None:
        self.__x: float = 0
        self.__y: float = 0
        self.__angle: float = 0
        self.__length: float = 0

    @staticmethod
    def from_cartesian(x: float, y: float) -> "Vector":
        p = Vector()
        p.x = x
        p.y = y

        return p

    @staticmethod
    def from_polar(angle: float, length: float) -> "Vector":
        p = Vector()
        while angle > 2*PI:
            angle -= 2*PI
        while angle < 0:
            angle += 2*PI
        p.angle = angle
        p.length = length

        return p

    # variable getters / setters
    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float) -> None:
        self.__x = value
        self.__update("c")

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float) -> None:
        self.__y = value
        self.__update("c")

    @property
    def angle(self) -> float:
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value: float) -> None:
        """
        value in radian
        """
        self.__angle = value
        self.__update("p")

    @property
    def length(self) -> float:
        return self.__length

    @length.setter
    def length(self, value: float) -> None:
        self.__length = value
        self.__update("p")

    # maths
    def __add__(self, other) -> "Vector":
        if type(other) == Vector:
            return Vector.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vector.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other) -> "Vector":
        if type(other) == Vector:
            return Vector.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vector.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other) -> "Vector":
        if type(other) == Vector:
            return Vector.from_polar(angle=self.angle + other.angle, length=self.length * other.length)

        return Vector.from_cartesian(x=self.x * other, y=self.y * other)

    def __truediv__(self, other) -> "Vector":
        return Vector.from_cartesian(x=self.x / other, y=self.y / other)

    # internal functions
    def __update(self, calc_from: str) -> None:
        """
        :param calc_from: polar (p) | cartesian (c)
        """
        if calc_from in ("p", "polar"):
            self.__x = np.cos(self.angle) * self.length
            self.__y = np.sin(self.angle) * self.length

        elif calc_from in ("c", "cartesian"):
            self.__length = np.sqrt(self.x**2 + self.y**2)
            self.__angle = np.arctan2(self.y, self.x)
            return

        else:
            raise ValueError("Invalid value for \"calc_from\"")

    def __abs__(self) -> float:
        return np.sqrt(self.x**2 + self.y**2)

    def __repr__(self) -> str:
        return f"<\n" \
               f"\tVector:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"


class BasicObject:
    def __init__(self, mass: float,
                 position: Vector,
                 velocity: Vector = Vector.from_cartesian(0, 0),
                 acceleration: Vector = Vector.from_cartesian(0, 0),
                 fixed: bool = False) -> None:
        """
        Basic physics object
        :param mass: mass
        :param position: x start position
        :param velocity: start velocity
        :param acceleration: the start acceleration of the object
        :param fixed: if true, the object won't be moved in the simulation
        """
        self.__mass = mass
        self.__position = position
        self.__trace: tp.List[Vector] = []
        self.velocity = velocity
        self.acceleration = acceleration
        self.fixed = fixed

    @property
    def mass(self) -> float:
        return self.__mass

    @property
    def position(self) -> Vector:
        return self.__position

    @position.setter
    def position(self, pos: Vector) -> None:
        self.__trace.append(pos)
        self.__position = pos

    @property
    def trace(self) -> tp.List[Vector]:
        return self.__trace


class Planet(BasicObject):
    def __init__(self, name: str, diameter: float, *args, **kw):
        super().__init__(*args, **kw)
        self.__name = name
        self.__d = diameter

    @property
    def name(self) -> str:
        return self.__name

    @property
    def diameter(self) -> float:
        return self.__d


class Simulation:
    def __init__(self, objects: tp.List[BasicObject] | tp.Tuple[BasicObject]) -> None:
        """
        All Objects to simulate should be in this class
        """
        self.__objects = objects
        self.__last_collided = [
            [],
            [],
            []
        ]

    @property
    def objects(self) -> list:
        return self.__objects

    @property
    def total_mass(self) -> float:
        return sum([obj.mass for obj in self.objects])

    @property
    def max_mass(self) -> float:
        return max([obj.mass for obj in self.objects])

    @property
    def size(self) -> Vector:
        """
        The total size in x and y
        """
        x_vals = [obj.position.x for obj in self.objects]
        y_vals = [obj.position.y for obj in self.objects]

        return Vector.from_cartesian(x=max(x_vals)-min(x_vals), y=max(y_vals)-min(y_vals))

    @property
    def gravity_center(self) -> Vector:
        gx = sum([obj.position.x*obj.mass for obj in self.objects])
        gx /= self.total_mass
        gy = sum([obj.position.y*obj.mass for obj in self.objects])
        gy /= self.total_mass

        return Vector.from_cartesian(gx, gy)

    def add_object(self, object_: BasicObject) -> None:
        self.__objects.append(object_)

    def iter(self, dt: float, gravity: bool = True, collision: bool = True, precision: int = 2) -> None:
        """
        run 1 iteration of the simulation
        """
        # iterate each object and then calculate all the forces to the other objects
        # based on F = G*(m1*m2)/r**2
        dt /= precision
        for _ in range(precision):
            if gravity:
                done_objects = []
                for now_object in self.objects.copy():
                    for influence_object in self.objects.copy():
                        if influence_object is not now_object and not {now_object, influence_object} in done_objects:
                            done_objects.append({now_object, influence_object})

                            f_l = G * (now_object.mass * influence_object.mass)
                            delta = now_object.position - influence_object.position
                            f_l = f_l / delta.length ** 2

                            f = Vector.from_polar(angle=delta.angle + PI, length=f_l)

                            now_a = f / now_object.mass
                            inf_a = f / -influence_object.mass

                            now_object.acceleration = now_a
                            now_object.velocity += now_object.acceleration * dt

                            influence_object.acceleration = inf_a
                            influence_object.velocity += influence_object.acceleration * dt

            if collision:
                done_objects = []
                for now_object in self.objects:
                    if type(now_object) == Planet:
                        for influence_object in self.objects:
                            if type(influence_object) == Planet and influence_object is not now_object:
                                now_object: Planet
                                influence_object: Planet
                                delta = now_object.position - influence_object.position

                                # check if they touch
                                if delta.length < now_object.diameter/2 + influence_object.diameter/2 and not now_object in done_objects\
                                        and not any([{now_object, influence_object} in self.__last_collided[i] for i in range(len(self.__last_collided))]):
                                    # v1' = (m1*v1 + m2*(2*v2-v1)) / (m1+m2)
                                    #
                                    done_objects += [now_object, influence_object]
                                    self.__last_collided.append({now_object, influence_object})

                                    # split the velocities in two directions (90°)
                                    a = (delta.angle-now_object.velocity.angle)
                                    now_carry = Vector.from_polar(angle=delta.angle-PI/2, length=now_object.velocity.length*np.sin(a))
                                    now_collision = Vector.from_polar(angle=delta.angle, length=now_object.velocity.length*np.cos(a))

                                    a = (delta.angle-influence_object.velocity.angle)
                                    inf_carry = Vector.from_polar(angle=delta.angle-PI/2, length=influence_object.velocity.length*np.sin(a))
                                    inf_collision = Vector.from_polar(angle=delta.angle, length=influence_object.velocity.length*np.cos(a))

                                    now_v = now_collision.length * now_object.mass
                                    now_v += (inf_collision.length * 2 - now_collision.length) * influence_object.mass
                                    now_v /= now_object.mass + influence_object.mass

                                    inf_v = inf_collision.length * influence_object.mass
                                    inf_v += (now_collision.length * 2 - inf_collision.length) * now_object.mass
                                    inf_v /= influence_object.mass + now_object.mass

                                    now_v = now_carry + Vector.from_polar(angle=now_collision.angle, length=now_v)
                                    inf_v = inf_carry + Vector.from_polar(angle=inf_collision.angle, length=inf_v)

                                    # assign velocities to objects
                                    now_object.acceleration = Vector()
                                    now_object.velocity = now_v

                                    influence_object.acceleration = Vector()
                                    influence_object.velocity = inf_v

                # move 1 down
                self.__last_collided = [
                    [],
                    [self.__last_collided[0]],
                    [self.__last_collided[1]]
                ]

            for now_object in self.objects:
                if not now_object.fixed:
                    now_object.velocity += now_object.acceleration * dt
                    now_object.position += now_object.velocity * dt
