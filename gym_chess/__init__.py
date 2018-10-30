from gym_chess.chess import ChessEnv
from gym.envs.registration import register

register(
	id='ChessVsRandomBot-v0',
	entry_point='gym_chess:ChessEnv',
	kwargs={'opponent' : 'random'},
)

register(
	id='ChessVsSelf-v0',
	entry_point='gym_chess:ChessEnv',
	kwargs={'opponent' : 'none'},
)
