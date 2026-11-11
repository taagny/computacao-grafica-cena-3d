"""Deterministic mission timeline. Every pose is a function of elapsed seconds.

The drone cannot inspect until the rover arrives; the rover cannot depart
until the scan and sensor acknowledgement finish. No frame-based increments.
"""
import math
import numpy as np


def smooth(t):
    t = float(np.clip(t, 0, 1))
    return t * t * (3 - 2 * t)


class Mission:
    STAGES = (
        ("SISTEMAS PRONTOS", 2.5, "Rover e drone aguardam autorização da missão."),
        ("APROXIMAÇÃO", 6.0, "O rover avança até o marco de inspeção."),
        ("DECOLAGEM", 3.5, "Chegada confirmada. Drone liberado para decolar."),
        ("VARREDURA ORBITAL", 8.0, "O drone inspeciona o rover; o sensor acompanha a órbita."),
        ("ENLACE CONFIRMADO", 3.0, "O rover confirma a leitura com um giro do sensor."),
        ("EXPLORAÇÃO CONJUNTA", 6.5, "Inspeção concluída. O drone escolta o rover."),
        ("RETORNO À BASE", 4.5, "Rover em posição segura. Drone retorna e pousa."),
        ("MISSÃO CONCLUÍDA", 0.0, "Operação concluída. R reinicia a missão."),
    )
    TOTAL = sum(stage[1] for stage in STAGES)

    def __init__(self, rover, drone):
        self.rover, self.drone = rover, drone
        self.time = 0.0
        self.index = 0
        self.local_time = 0.0
        self.reset()

    @property
    def label(self):
        return self.STAGES[self.index][0]

    @property
    def description(self):
        return self.STAGES[self.index][2]

    @property
    def progress(self):
        return self.time / self.TOTAL

    def reset(self):
        self.time = 0.0
        self.update(0)

    def update(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("O delta time deve ser finito e não negativo.")
        self.time = min(self.TOTAL, self.time + dt)
        t = self.time
        self.index = len(self.STAGES) - 1
        self.local_time = 0.0
        for i, (_, duration, _) in enumerate(self.STAGES[:-1]):
            if t < duration:
                self.index, self.local_time = i, t
                break
            t -= duration
        i, t = self.index, self.local_time
        duration = self.STAGES[i][1]
        p = smooth(t / duration) if duration else 1.0
        rover = np.array([-3.2, 0.08, 5.0], dtype=np.float32)
        drone = np.array([3.8, 0.68, 0.0], dtype=np.float32)
        yaw, sensor, travel = math.pi, 0.0, 0.0
        drone_yaw = 0.0
        if i == 1:
            rover[2] = 5 - 5 * p
            travel = 5 * p
        elif i >= 2:
            rover[2] = 0
            travel = 5.0
        if i == 2:
            drone[:] = (3.8 - 4.5 * p, 0.68 + 3.12 * p, 0)
            drone_yaw = -math.pi / 2 * p
            sensor = -math.pi / 2 * p
        elif i == 3:
            angle = math.tau * p
            drone[:] = (-3.2 + 2.5 * math.cos(angle),
                        3.8 + 0.25 * math.sin(angle * 2), 2.5 * math.sin(angle))
            drone_yaw = -angle - math.pi / 2
            sensor = math.pi / 2 - angle - math.pi
        elif i == 4:
            drone[:] = (-0.7, 3.8, 0)
            drone_yaw = -math.pi / 2
            sensor = -math.pi / 2 + 0.5 * math.sin(math.tau * p)
        elif i == 5:
            rover[2] = -5 * p
            travel = 5 + 5 * p
            drone[:] = (-0.7, 3.8, -5 * p)
            drone_yaw = -math.pi / 2 * (1 - p) + math.pi * p
            sensor = -math.pi / 2 * (1 - p)
        elif i >= 6:
            rover[2], travel = -5, 10
            drone[:] = (-0.7 + 4.5 * p, 3.8 - 3.12 * p, -5 + 5 * p)
            drone_yaw = math.pi * (1 - p)
        if 2 <= i <= 6:
            # The envelope vanishes at takeoff/landing, so no pose jumps.
            envelope = math.sin(math.pi * p / 2) if i == 2 else (math.cos(math.pi * p / 2) if i == 6 else 1)
            drone[1] += 0.055 * math.sin(self.time * 3) * envelope
        self.rover.position = rover
        self.rover.rotation[1] = yaw
        self.rover.sensor.rotation[1] = sensor
        self.rover.set_travel(travel)
        self.drone.position = drone
        self.drone.rotation[1] = drone_yaw
        self.drone.rotation[2] = 0.055 * math.sin(math.tau * p) if i in (2, 3, 5, 6) else 0
        self.drone.gimbal.rotation[0] = (0.5 * p if i == 2 else
                                        (0.5 if 3 <= i <= 5 else
                                         (0.5 * (1 - p) if i == 6 else 0)))
        # Integrate a piecewise-linear rotor speed analytically for continuity.
        start, stop = 8.5, self.TOTAL
        elapsed = max(0, min(self.time - start, stop - start))
        ramp = min(elapsed, 1.0)
        angle = 50 * ramp * ramp + 100 * max(0, elapsed - 1)
        landing_ramp = max(0, elapsed - (stop - start - 1))
        angle -= 50 * landing_ramp * landing_ramp
        self.drone.set_rotors(angle)
