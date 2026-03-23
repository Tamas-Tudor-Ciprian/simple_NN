import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random
from collections import deque


class DodgeEnv(gym.Env):
    """Custom Gymnasium environment wrapping the pygame dodge game."""

    metadata = {"render_modes": ["human"], "render_fps": 60}

    # --- Game constants (matched to main.py) ---
    SCREEN_W, SCREEN_H = 1280, 720
    LEFT_WALL = pygame.Rect(SCREEN_W // 2 - 400, 0, 100, SCREEN_H)   # x=[240,340)
    RIGHT_WALL = pygame.Rect(SCREEN_W // 2 + 300, 0, 100, SCREEN_H)  # x=[940,1040)
    MIN_X = LEFT_WALL.right   # 340
    MAX_X = RIGHT_WALL.left   # 940
    PLAYER_SPEED = 300         # px/s
    OBS_SPEED = 300            # px/s
    SPAWN_INTERVAL = 0.8       # seconds
    PLAYER_RADIUS = 40
    PLAYER_START_X = SCREEN_W / 2   # 640
    PLAYER_START_Y = SCREEN_H / 2   # 360
    DT = 1.0 / 60.0           # fixed timestep
    MAX_STEPS = 3600           # ~60 s of game time

    # Observation: player_x, player_y, dist_left_wall, dist_right_wall
    #              + 10 nearest obstacles (rel_x, rel_y)
    N_OBS_TRACKED = 10
    OBS_DIM = 4 + N_OBS_TRACKED * 2  # 24

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(3)  # 0=left, 1=stay, 2=right
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.OBS_DIM,), dtype=np.float32
        )

        # pygame rendering state (lazy init)
        self._screen = None
        self._clock = None

        self._reset_game()

    # ------------------------------------------------------------------
    # Gymnasium API
    # ------------------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._reset_game()
        obs = self._get_obs()
        return obs, {}

    def step(self, action):
        # Apply action
        if action == 0:
            self.player_x -= self.PLAYER_SPEED * self.DT
        elif action == 2:
            self.player_x += self.PLAYER_SPEED * self.DT

        # Update obstacles
        self._spawn_and_move()

        self.steps += 1

        # Collision check
        terminated = self._check_collision()
        truncated = self.steps >= self.MAX_STEPS

        reward = -10.0 if terminated else 1.0

        obs = self._get_obs()

        if self.render_mode == "human":
            self.render()

        return obs, reward, terminated, truncated, {}

    def render(self):
        if self.render_mode != "human":
            return

        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
            pygame.display.set_caption("Dodge – AI Playing")
            self._clock = pygame.time.Clock()
            self._font = pygame.font.SysFont(None, 36)

        # Pump events so the window stays responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        self._screen.fill("yellow")

        # Walls
        pygame.draw.rect(self._screen, "blue", self.LEFT_WALL)
        pygame.draw.rect(self._screen, "blue", self.RIGHT_WALL)

        # Obstacles
        for obs in self.obsts:
            pygame.draw.rect(self._screen, "blue", obs)

        # Player
        pygame.draw.circle(
            self._screen, "red",
            (int(self.player_x), int(self.player_y)),
            self.PLAYER_RADIUS,
        )

        # Score overlay
        score_surf = self._font.render(f"Steps: {self.steps}", True, "black")
        self._screen.blit(score_surf, (10, 10))

        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])

    def close(self):
        if self._screen is not None:
            pygame.quit()
            self._screen = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_game(self):
        self.player_x = float(self.PLAYER_START_X)
        self.player_y = float(self.PLAYER_START_Y)
        self.obsts: deque[pygame.Rect] = deque()
        self.spawn_timer = 0.0
        self.steps = 0

    def _spawn_and_move(self):
        self.spawn_timer += self.DT
        if self.spawn_timer >= self.SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            w = self.np_random.integers(30, 81)
            h = self.np_random.integers(20, 41)
            x = self.np_random.integers(self.MIN_X, self.MAX_X - w + 1)
            self.obsts.append(pygame.Rect(int(x), -int(h), int(w), int(h)))

        for obs in self.obsts:
            obs.y += int(self.OBS_SPEED * self.DT)

        while self.obsts and self.obsts[0].y > self.SCREEN_H:
            self.obsts.popleft()

    def _check_collision(self):
        px, py, r = self.player_x, self.player_y, self.PLAYER_RADIUS
        for rect in [self.LEFT_WALL, self.RIGHT_WALL, *self.obsts]:
            cx = max(rect.left, min(px, rect.right))
            cy = max(rect.top, min(py, rect.bottom))
            if (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2:
                return True
        return False

    def _get_obs(self):
        # Normalise player position to [-1, 1]
        px_norm = (self.player_x - self.SCREEN_W / 2) / (self.SCREEN_W / 2)
        py_norm = (self.player_y - self.SCREEN_H / 2) / (self.SCREEN_H / 2)

        # Distance to walls normalised to [0, 1] over playable width
        playable_w = self.MAX_X - self.MIN_X  # 600
        dist_left = (self.player_x - self.MIN_X) / playable_w
        dist_right = (self.MAX_X - self.player_x) / playable_w

        # Gather the N nearest obstacles by distance to player
        dists = []
        for obs in self.obsts:
            ox = obs.centerx
            oy = obs.centery
            d = (self.player_x - ox) ** 2 + (self.player_y - oy) ** 2
            dists.append((d, ox, oy))
        dists.sort()

        obs_features = np.zeros(self.N_OBS_TRACKED * 2, dtype=np.float32)
        for i, (_, ox, oy) in enumerate(dists[: self.N_OBS_TRACKED]):
            rel_x = (ox - self.player_x) / (self.SCREEN_W / 2)
            rel_y = (oy - self.player_y) / (self.SCREEN_H / 2)
            obs_features[i * 2] = np.clip(rel_x, -1.0, 1.0)
            obs_features[i * 2 + 1] = np.clip(rel_y, -1.0, 1.0)

        return np.concatenate(
            [np.array([px_norm, py_norm, dist_left, dist_right], dtype=np.float32),
             obs_features]
        )
