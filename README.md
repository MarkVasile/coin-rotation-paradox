# coin-rotation-paradox

I've been enjoying watching Veritasium youtube channel, as well as other amazing science channels. Recently he posted [this video](https://www.youtube.com/watch?v=FUHkTs-Ipfg) which gave me a couple of white nights trying to come up with an understanding of this problem.

This repository creates a video visualization of this "paradox", providing what I think is an easier way to understand it intuitively and may very well serve as a visual proof.

In the first example `RollingCircle` we see the unit circle roll on the exterior of the big circle, of radius 3. In this animation the unit circle rolls in a clockwise direction, and we can see it makes only 3 turns along the circumference when the circumference is unrolled into a straight line.

However, when we roll the unit circle around the big circle, this circumference is not straight anymore, and a mapping from the straight motion to the circular motion will immediately reveal an extra clockwise rotation, so in total N+1 = 4 rotations for a radius ratio or 3 to 1. 

Similarly, when rolling on the interior of the big circle, as you can see in the `RollingCircleInterior`, the unit circle is rotating anti-clockwise 3 times, as expected, but the circumference is rolled back into the circle in a clockwise direction which reverts one of the rotations of our unit circle, giving us N-1 rotations.

Perhaps there is a more strict approach in topology, when mapping the motion inside one manifold onto another manifold (folding?). Personally I found this programming exercise quite amazing, as I've never worked with the manim library before. If anyone has more in depth knowledge on the connected subjects (topology, geometry, ...) I'd love to connect.
