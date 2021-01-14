from gym_chess.gym_chess import ChessEngine  # rust module
from gym_chess.envs import ChessEnvV0, ChessEnvV1, ChessEnvV2  # envs
from gym.envs.registration import register  # to register envs


register(
    id="ChessVsRandomBot-v0",
    entry_point="gym_chess.envs:ChessEnvV0",
    kwargs={"opponent": "random"},
)

register(
    id="ChessVsSelf-v0",
    entry_point="gym_chess.envs:ChessEnvV0",
    kwargs={"opponent": "none"},
    # max_episode_steps=100,
    # reward_threshold=.0, # optimum = .0
)

register(
    id="ChessVsRandomBot-v1",
    entry_point="gym_chess.envs:ChessEnvV1",
    kwargs={"opponent": "random"},
)

register(
    id="ChessVsSelf-v1",
    entry_point="gym_chess.envs:ChessEnvV1",
    kwargs={"opponent": "none"},
)

register(
    id="ChessVsRandomBot-v2",
    entry_point="gym_chess.envs:ChessEnvV2",
    kwargs={"opponent": "random"},
)

register(
    id="ChessVsSelf-v2",
    entry_point="gym_chess.envs:ChessEnvV2",
    kwargs={"opponent": "none"},
)
