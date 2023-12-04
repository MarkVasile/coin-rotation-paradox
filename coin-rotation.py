from inspect import CO_ITERABLE_COROUTINE
from colorama import Fore, Back
from math import cos, sin
from numpy import arccos, arcsin
from manim import *

CENTER_X = 3 * PI * LEFT
CENTER_Y = 3 * DOWN
CIRCLE_B_CENTER = CENTER_X + CENTER_Y

##########################################################################
# Class Rope
# A simple rope implementation quite specific to our exercise here,
# I'll work on cleaning it up and making it generic later.
##########################################################################
class Rope:
    def __init__(self, radius):
        self.circle_radius = radius

    def rope(self, x, y, z, t, unrolling):
        # We receive (xy) from [-9,0] counter-clockwise back to [-9,0] and t between 0 and 1.
        qx = (x + 3 * PI)/3
        qy = y/3 + 1
        lx = arccos(qx) # --> PI/2 --> PI --> PI/2 --> 0 --> PI/2
        ly = arcsin(qy) # --> PI/2 --> 0 --> -PI/2 --> 0 --> PI/2

        # Compute the central angle theta subtended by the arc A~B for A(PI/2, 0) and B(xy).
        if lx >= PI/2 and ly > 0:
            theta = lx - PI/2 # quadrant = 1
        elif lx >= PI/2 and ly <= 0:
            theta = PI/2 - ly # quadrant = 2
        elif lx < PI/2 and ly < 0:
            theta = 3 * PI/2 + ly # quadrant = 3
        else:
            theta = 3 * PI/2 + ly # quadrant = 4

        # The idea is to keep the B(xy) point at the right distance from the current point of contact with the circle,
        # which we can interpolate using "t" --> alpha is the angle at the point of contact.
        if (unrolling):
            alpha = -1 * interpolate(theta, 2*PI, t)
            shrink_factor = interpolate(0.4, 1, t) # just some magic numbers to fix my failed math at x1, y1 down below
        else:
            alpha = -1 * interpolate(2*PI, theta, t)
            shrink_factor = interpolate(1, 0.4, t)

        # At the same time we rotate (xy) counter-clockwise around, keeping it tangential to the point of contact.
        beta = alpha + theta

        # Coordinates for point of contact C
        xc = self.circle_radius * sin(alpha) # reversed sin/cos due to having the starting point at the very top of the circle.
        yc = self.circle_radius * cos(alpha)

        # Coordinates for point Bi on the tangent at C, away from C exactly radius * beta
        # normally we would integrate over the entire rope to maintain length,
        # but this is an incremental call with 0 <= t <= 1, and I couldn't devise a quick implementation
        # so cheating is it: shrink_factor
        x1 = xc + shrink_factor * self.circle_radius * beta * sin(alpha - PI/2) - 3 * PI
        y1 = yc + shrink_factor * self.circle_radius * beta * cos(alpha - PI/2) - 3

        return [x1, y1, z]


    def unroll(self, x, y, z, t):
        return self.rope(x, y, z, t, True)

    def roll(self, x, y, z, t):
        return self.rope(x, y, z, t, False)


##########################################################################
# Class RollWithRope
# A custom animation to keep the unit circle at the tip of the rope.
##########################################################################
class RollWithRope(Animation):
    def __init__(
        self,
        mobject: Mobject,
        **kwargs,
    ):
        super().__init__(mobject, **kwargs)
        self.rope = Rope(3)

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float,
    ):
        smooth_alpha = rate_functions.rush_from(alpha)
        cos_rad = cos(smooth_alpha * 2*PI)
        sin_rad = sin(smooth_alpha * 2*PI)
        offset_x = 3*PI
        offset_y = 0

        def rotate(x, y):
            origin_x = (x - offset_x)
            origin_y = (y - offset_y)
            qx = offset_x + cos_rad * origin_x + sin_rad * origin_y
            qy = offset_y + -sin_rad * origin_x + cos_rad * origin_y
            return np.array([qx, qy, 0])

        def action(xyz):
            translate = self.rope.roll(-3*PI, 0, 0, alpha)
            ret = rotate(xyz[0], xyz[1]) + translate - [3*PI, 0, 0]
            return ret

        submobject.become(starting_submobject.copy().apply_function(action))
        return self


##########################################################################
# Class RollingCircle
# Our main class which should be invoked in the manim command.
##########################################################################
class RollingCircle(MovingCameraScene):
    def construct(self):
        # Create the unit circle, and rotate it -pi/2 -- this will make its starting point xy = [0, -1]
        circle = Circle(radius=1, color=BLUE).rotate(-PI/2)

        # Create the radius 3 circle, and rotate it pi/2 -- this makes its starting point up on the top xy = [0, 3]
        circle3 = Circle(radius=3, color=GREEN).shift(CIRCLE_B_CENTER).rotate(PI/2)

        # Set the unit circle at the initial position on top of circle3
        circle.move_to(UP + LEFT * 3 * PI)

        # Create a dot on the unit circle to visualize its rotation
        dot = Dot(color=RED)
        dot.move_to(circle.get_start())

        # Create the three steps for our unit circle to roll on, each equal to 2pi.
        line_center1 = Line(Point([-3 * PI, 1, 0]), Point([-PI, 1, 0]))
        line_center2 = Line(Point([-PI, 1, 0]), Point([PI, 1, 0]))
        line_center3 = Line(Point([PI, 1, 0]), Point([3*PI, 1, 0]))

        # Create a straight line of length 2 * pi * R; where R=3 in our case
        circumference3 = Line(Point([-3 * PI, 0, 0]), Point([3 * PI, 0, 0]))

        # Create our rope to visualize circumference rolling and unrolling over the circle
        rope = Rope(3)

        # Create a VGroup to hold the circle, dot, and line
        unit_group = VGroup(circle, dot)

        self.camera.frame.move_to([0, -5, 0])
        self.camera.frame.scale(3)

        # Add the group to the scene
        self.play(
            Create(VGroup(circle, circle3, dot)),
        )

        self.wait()
        self.clear()
        self.add(unit_group)
        self.add(circle3)

        self.play(
            *[
                Homotopy(rope.unroll, circle3.copy()),
                FadeToColor(circle3, color=DARK_GRAY),
            ]
        )
        self.add(circumference3)

        self.wait()

        # Move the circle tangentially along the line
        self.play(
            MoveAlongPath(circle, line_center1, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle.reverse_points(), run_time=2, rate_func=linear),
        )
        self.wait()

        self.play(
            MoveAlongPath(circle, line_center2, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle, run_time=2, rate_func=linear),
        )
        self.wait()

        self.play(
            MoveAlongPath(circle, line_center3, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle, run_time=2, rate_func=linear),
        )
        self.wait()

        self.play(
            self.camera.frame.animate.move_to([0, -6, 0]),
        )

        self.wait()

        self.clear()
        self.add(unit_group)
        self.add(circle3)

        self.play(
            *[
                FadeToColor(circle3, GREEN),
                Homotopy(rope.roll, circle3.copy()),
                RollWithRope(unit_group),
            ],
            run_time=8,
        )
        self.wait()

        self.clear()
        self.add(unit_group)
        self.add(circle3)

        self.wait()

