import sys
import pygame
from stable_baselines3 import PPO
from dodge_env import DodgeEnv


MODEL_PATH = "models/dodge_ppo.zip"


def main():
    print(f"Loading model from {MODEL_PATH} …")
    model = PPO.load(MODEL_PATH, device="cpu")

    env = DodgeEnv(render_mode="human")
    obs, _ = env.reset()

    # Force pygame init so event handling works from the start
    env.render()

    running = True
    while running:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

        # Process events after step (render is called inside step)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if terminated or truncated:
            print(f"Episode ended — survived {env.steps} steps")
            obs, _ = env.reset()

    env.close()


if __name__ == "__main__":
    main()
