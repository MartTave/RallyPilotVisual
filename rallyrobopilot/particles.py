from ursina import *
from ursina import curve

from rallyrobopilot.time_manager import Time

class Particles(Entity):

    timeManager: Time

    def __init__(self, timeManager: Time, car, position):
        super().__init__(
            model = "particles.obj",
            scale = 0.1,
            position = position, 
            rotation_y = random.random() * 360
        )

        self.timeManager = timeManager

        self.car = car
        self.direction = Vec3(random.random(), random.random(), random.random())

        if hasattr(self.car, "forest_track"):
            if car.forest_track.enabled:
                self.texture = "particle_forest_track.png"

    def update(self):
        self.position += self.direction * 5 * self.timeManager.dt
        if hasattr(self.car, "graphics"):
            if self.car.graphics != "fancy":
                self.scale_x += 0.1 * self.timeManager.dt
                self.scale_y += 0.1 * self.timeManager.dt

    def destroy(self, delay = 1):
        self.fade_out(duration = 0.2, delay = 0.7, curve = curve.linear)
        destroy(self, delay)
        del self

class TrailRenderer(Entity):
    def __init__(self, thickness = 10, length = 6, **kwargs):
        super().__init__(**kwargs)
        self.thickness = thickness
        self.length = length

        self._t = 0
        self.update_step = 0.025
        self.trailing = False

    def update(self):
        if self.trailing:
            self._t += self.timeManager.dt
            if self._t >= self.update_step:
                self._t = 0
                self.renderer.model.vertices.pop(0)
                self.renderer.model.vertices.append(self.world_position)
                self.renderer.model.generate()

    def start_trail(self):
        self.trailing = True
        self.renderer = Entity(model = Mesh(
            vertices = [self.world_position for i in range(self.length)],
            mode = "line",
            thickness = self.thickness,
            static = False,
        ), color = color.rgba(10, 10, 10, 90))

    def end_trail(self, now = False):
        if not now:
            self.renderer.fade_out(duration = 1, delay = 8, curve = curve.linear)
            destroy(self.renderer, 10)
        else:
            destroy(self.renderer)
        self.trailing = False

# class Smoke(Entity):
#     def __init__(self, position, rotation_y, amount_of_smoke):
#         super().__init__(
#             model = "smoke.obj",
#             texture = "smoke.png",
#             scale = 3,
#             position = position,
#             rotation_y = rotation_y,
#         )

#         self.amount_of_smoke = amount_of_smoke
#         if self.amount_of_smoke >= 0.1:
#             self.amount_of_smoke = 0.1
#         elif self.amount_of_smoke <= 0.05:
#             self.amount_of_smoke = 0.05
#         self.direction = Vec3(random.random(), random.random(), random.random()) * self.amount_of_smoke

#     def update(self):
#         self.position += self.direction * 120 * self.timeManager.dt

#         if self.amount_of_smoke >= 0.1:
#             self.amount_of_smoke = 0.1
#         elif self.amount_of_smoke <= 0.05:
#             self.amount_of_smoke = 0.05
