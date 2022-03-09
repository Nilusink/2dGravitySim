from objects import Planet, Vector, PI, AU

objects = [
    # solar system setup
    Planet(name="Sun", diameter=2*696342000, mass=1.9885e+30, position=Vector(), fixed=False),
    Planet(name="Mercury", diameter=2*2439700, mass=3.3011e+23,
           position=Vector.from_polar(angle=0, length=0.387098*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=47360)),
    Planet(name="Venus", diameter=2*6051800, mass=4.8675e+24,
           position=Vector.from_polar(angle=0, length=0.723332 * AU),
           velocity=Vector.from_polar(angle=PI / 2, length=35020)),
    Planet(name="Earth", diameter=2*6371000, mass=5.97237e+24,
           position=Vector.from_polar(angle=0, length=AU),
           velocity=Vector.from_polar(angle=PI / 2, length=29780)),
    Planet(name="Mars", diameter=2*3389500, mass=6.4171e+23,
           position=Vector.from_polar(angle=0, length=1.666*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=24007)),
    Planet(name="Jupiter", diameter=2*69911000, mass=1.8982e+27,
           position=Vector.from_polar(angle=0, length=5.2044*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=13070)),
    Planet(name="Saturn", diameter=2*60268000, mass=5.68343e+26,
           position=Vector.from_polar(angle=0, length=9.5826*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=9680)),
    Planet(name="Uranus", diameter=2*25362000, mass=8.6810e+25,
           position=Vector.from_polar(angle=0, length=19.19126*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=6800)),
    Planet(name="Neptune", diameter=2*24622000, mass=1.02413e+26,
           position=Vector.from_polar(angle=0, length=30.07*AU),
           velocity=Vector.from_polar(angle=PI / 2, length=5430))
]

# rename for another test  (timescale ing main.py should be changed!)
objects1 = [
    Planet(name="1", diameter=1, mass=500_000_000,
           position=Vector.from_cartesian(0, 0)),
    Planet(name="2", diameter=1, mass=500_000_000,
           position=Vector.from_cartesian(2, 0)),
    Planet(name="3", diameter=2, mass=5_000_000_000,
           position=Vector.from_cartesian(2, 5))
]

objects2 = [
    Planet(name="1", diameter=0.5, mass=2, position=Vector.from_cartesian(-1, 0),
           velocity=Vector.from_polar(angle=0, length=1)),

    Planet(name="2", diameter=0.5, mass=4, position=Vector.from_cartesian(0, 0)),
    Planet(name="2", diameter=0.5, mass=2, position=Vector.from_cartesian(0.5, 0)),
    Planet(name="2", diameter=0.5, mass=2, position=Vector.from_cartesian(1, 0))
]
