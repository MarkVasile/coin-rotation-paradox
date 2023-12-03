from inspect import CO_ITERABLE_COROUTINE
from colorama import Fore, Back
from math import cos, sin
from manim.utils.paths import spiral_path
from numpy import arccos, arcsin
from manim import *

CENTER_X = 3 * PI * LEFT
CENTER_Y = 3 * DOWN
CIRCLE_B_CENTER = CENTER_X + CENTER_Y

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

        # Create a straight line of length 2 * pi * R; where R=3 in our case
        circumference3 = Line(Point([-3 * PI, 0, 0]), Point([3 * PI, 0, 0]))

        # Create the three steps for our unit circle to roll on, each equal to 2pi.
        line_center1 = Line(Point([-3 * PI, 1, 0]), Point([-PI, 1, 0]))
        line_center2 = Line(Point([-PI, 1, 0]), Point([PI, 1, 0]))
        line_center3 = Line(Point([PI, 1, 0]), Point([3*PI, 1, 0]))

        # Create a VGroup to hold the circle, dot, and line
        unit_group = VGroup(circle, dot)

        kw = {"run_time": 2 * PI, "path_arc": PI / 2}

        self.camera.frame.move_to([0, -2, 0])
        self.camera.frame.scale(3.2)

        # Add the group to the scene
        self.play(
            Create(VGroup(circle, circle3, dot)),
        )

        self.wait()

        circle_radius = 3
        def roll(x, y, z, t):
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
            alpha = -1 * interpolate(2*PI, theta, t)

            # At the same time we rotate (xy) counter-clockwise around, keeping it tangential to the point of contact.
            beta = alpha + theta

            # Coordinates for point of contact C
            xc = circle_radius * sin(alpha) # reversed sin/cos due to having the starting point at the very top of the circle.
            yc = circle_radius * cos(alpha)

            # Coordinates for point Bi on the tangent at C, away from C exactly radius * beta
            x1 = xc + circle_radius * beta * sin(alpha - PI/2) - 3 * PI
            y1 = yc + circle_radius * beta * cos(alpha - PI/2) - 3

            return [x1, y1, z]


        def unroll(x, y, z, t):
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
            alpha = -1 * interpolate(theta, 2*PI, t)

            # At the same time we rotate (xy) counter-clockwise around, keeping it tangential to the point of contact.
            beta = alpha + theta

            # Coordinates for point of contact C
            xc = circle_radius * sin(alpha) # reversed sin/cos due to having the starting point at the very top of the circle.
            yc = circle_radius * cos(alpha)

            # Coordinates for point Bi on the tangent at C, away from C exactly radius * beta
            x1 = xc + circle_radius * beta * sin(alpha - PI/2) - 3 * PI
            y1 = yc + circle_radius * beta * cos(alpha - PI/2) - 3

            return [x1, y1, z]


        self.play(
            *[
                Homotopy(
                    unroll,
                    circle3.copy(),
                )
            ]
        )

        self.wait()

        # Move the circle tangentially along the line
        self.play(
            MoveAlongPath(circle, line_center1, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle.reverse_points(), run_time=2, rate_func=linear),
        )

        # Wait for the animation to finish
        self.wait()

        self.play(
            MoveAlongPath(circle, line_center2, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle, run_time=2, rate_func=linear),
        )

        # Wait for the animation to finish
        self.wait()

        self.play(
            MoveAlongPath(circle, line_center3, run_time=2, rate_func=linear),
            MoveAlongPath(dot, circle, run_time=2, rate_func=linear),
        )

        # Wait for the animation to finish
        self.wait()

        self.play(
            *[
                Homotopy(
                    roll,
                    circle3.copy(),
                ),
                MoveAlongPath(
                    unit_group,
                    CubicBezier(
                        np.array([3 * PI, 1, 0]),
                        np.array([3 * PI, -3 * PI, 0]),
                        np.array([-4 * PI, 1, 0]),
                        np.array([-3 * PI, 1, 0]),
                    ),
                    rate_functions = linear,
                ),
            ]
        )

        # Wait for the animation to finish
        self.wait()

