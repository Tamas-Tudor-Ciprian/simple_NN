import argparse
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from dodge_env import DodgeEnv


def make_env():
    """Factory that returns a new DodgeEnv (headless)."""
    def _init():
        return DodgeEnv(render_mode=None)
    return _init


def main():
    parser = argparse.ArgumentParser(description="Train a PPO agent on DodgeEnv")
    parser.add_argument(
        "--timesteps", type=int, default=500_000,
        help="Total training timesteps (default: 500000)",
    )
    parser.add_argument(
        "--n-envs", type=int, default=4,
        help="Number of parallel environments (default: 4)",
    )
    args = parser.parse_args()

    os.makedirs("models", exist_ok=True)
    os.makedirs("tb_logs", exist_ok=True)

    print(f"Training PPO for {args.timesteps} timesteps with {args.n_envs} parallel envs …")

    vec_env = SubprocVecEnv([make_env() for _ in range(args.n_envs)])

    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        device="cpu",
        tensorboard_log="./tb_logs/",
    )

    model.learn(total_timesteps=args.timesteps, tb_log_name="dodge_ppo")
    model.save("models/dodge_ppo")
    vec_env.close()

    print("\n✓ Model saved to models/dodge_ppo.zip")
    print("  Launch TensorBoard with:")
    print("    tensorboard --logdir=./tb_logs/")


if __name__ == "__main__":
    main()
