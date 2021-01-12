from gym.envs.registration import register

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
    # max_episode_steps=100,
    # reward_threshold=.0, # optimum = .0
)
