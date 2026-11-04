from enum import Enum, auto

import numpy as np

from models.astronaut import Astronaut
from models.rocket import Rocket


class AnimationState(Enum):
    WAITING = auto()
    COUNTDOWN = auto()
    LIFTOFF = auto()
    ASTRONAUT_ACTION = auto()
    COMPLETE = auto()


class StateMachine:
    STATE_DURATIONS = {
        AnimationState.WAITING: 2.0,
        AnimationState.COUNTDOWN: 4.0,
        AnimationState.LIFTOFF: 5.0,
        AnimationState.ASTRONAUT_ACTION: 4.0,
    }

    STATE_LABELS = {
        AnimationState.WAITING: "Aguardando lancamento",
        AnimationState.COUNTDOWN: "Contagem regressiva",
        AnimationState.LIFTOFF: "Decolagem",
        AnimationState.ASTRONAUT_ACTION: "Astronauta acena",
        AnimationState.COMPLETE: "Sequencia concluida",
    }

    def __init__(self, rocket: Rocket, astronaut: Astronaut) -> None:
        self.rocket = rocket
        self.astronaut = astronaut
        self._rocket_start_position = rocket.position.copy()
        self._astronaut_start_position = astronaut.position.copy()
        self.state = AnimationState.WAITING
        self.state_time = 0.0
        self.elapsed_time = 0.0
        self.reset()

    @property
    def label(self) -> str:
        return self.STATE_LABELS[self.state]

    def reset(self) -> None:
        self.state = AnimationState.WAITING
        self.state_time = 0.0
        self.elapsed_time = 0.0
        self.rocket.position = self._rocket_start_position.copy()
        self.rocket.set_support_angle(0.0)
        self.rocket.set_flame_scale(0.2)
        self.astronaut.position = self._astronaut_start_position.copy()
        self.astronaut.set_arm_swing(0.0)
        self.astronaut.set_leg_swing(0.0)
        self.astronaut.set_raised_arm_angle(0.0)
        self.astronaut.set_head_yaw(0.0)
        self.astronaut.set_body_yaw(0.0)

    def update(self, delta_time: float) -> None:
        if delta_time < 0.0:
            raise ValueError("O delta time da maquina de estados nao pode ser negativo.")
        if delta_time == 0.0 or self.state is AnimationState.COMPLETE:
            return

        remaining_time = delta_time
        while remaining_time > 0.0 and self.state is not AnimationState.COMPLETE:
            duration = self.STATE_DURATIONS.get(self.state)
            if duration is None:
                break
            available_time = duration - self.state_time
            step = min(remaining_time, available_time)

            self.state_time += step
            self.elapsed_time += step
            remaining_time -= step
            self._apply_current_state()

            if self.state_time >= duration:
                self._advance_state()

    def _apply_current_state(self) -> None:
        duration = self.STATE_DURATIONS.get(self.state)
        progress = 1.0 if duration is None else self.state_time / duration
        progress = float(np.clip(progress, 0.0, 1.0))

        if self.state is AnimationState.WAITING:
            return

        if self.state is AnimationState.COUNTDOWN:
            self.rocket.set_support_angle(1.05 * progress)
            self.rocket.set_flame_scale(0.2 + 0.65 * progress)
            return

        if self.state is AnimationState.LIFTOFF:
            eased_progress = progress * progress * (3.0 - 2.0 * progress)
            self.rocket.position[1] = (
                self._rocket_start_position[1] + 8.0 * eased_progress
            )
            self.rocket.set_support_angle(1.05)
            self.rocket.set_flame_scale(0.85 + 0.75 * progress)
            self.astronaut.set_head_yaw(-0.2 * progress)
            return

        if self.state is AnimationState.ASTRONAUT_ACTION:
            self.rocket.position[1] = self._rocket_start_position[1] + 8.0
            self.rocket.set_flame_scale(0.2)
            self.astronaut.set_head_yaw(-0.2)
            self.astronaut.set_raised_arm_angle(1.15 * progress)
            self.astronaut.set_arm_swing(0.15 * np.sin(self.state_time * 5.0))
            self.astronaut.set_leg_swing(0.08 * np.sin(self.state_time * 3.0))
            return

        self.rocket.position[1] = self._rocket_start_position[1] + 8.0
        self.rocket.set_flame_scale(0.2)
        self.astronaut.set_head_yaw(-0.2)
        self.astronaut.set_raised_arm_angle(1.15)
        self.astronaut.set_arm_swing(0.0)
        self.astronaut.set_leg_swing(0.0)

    def _advance_state(self) -> None:
        next_states = {
            AnimationState.WAITING: AnimationState.COUNTDOWN,
            AnimationState.COUNTDOWN: AnimationState.LIFTOFF,
            AnimationState.LIFTOFF: AnimationState.ASTRONAUT_ACTION,
            AnimationState.ASTRONAUT_ACTION: AnimationState.COMPLETE,
        }
        self.state = next_states[self.state]
        self.state_time = 0.0
        if self.state is AnimationState.COMPLETE:
            self._apply_current_state()
