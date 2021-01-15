# gym-chess ♟️

A simple chess environment for gym. It computes all available moves, including castling, pawn promotions and 3-fold repetition draws.

<table style="text-align:center;border-spacing:0pt;font-family:'Arial Unicode MS'; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 0pt">
<tr>
<td style="width:12pt">8</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 1pt"><span style="font-size:150%;">♜</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♞</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♝</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♛</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♚</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♝</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♞</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 1pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♜</span></td>
</tr>
<tr>
<td style="width:12pt">7</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"><span style="font-size:150%;">♟</span></td>
</tr>
<tr>
<td style="width:12pt">6</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"></td>
</tr>
<tr>
<td style="width:12pt">5</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"></td>
</tr>
<tr>
<td style="width:12pt">4</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"></td>
</tr>
<tr>
<td style="width:12pt">3</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"></td>
</tr>
<tr>
<td style="width:12pt">2</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
</tr>
<tr>
<td style="width:12pt">1</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 1pt" bgcolor="silver"><span style="font-size:150%;">♖</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♘</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♗</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♕</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♔</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♗</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♘</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 1pt 0pt"><span style="font-size:150%;">♖</span></td>
</tr>
<tr>
<td></td>
<td>a</td>
<td>b</td>
<td>c</td>
<td>d</td>
<td>e</td>
<td>f</td>
<td>g</td>
<td>h</td>
</tr>
</table>


## Setup

Install the module:

``` python

pip install -e .

```


## Environments

There are 3 environments available: `v0`, `v1` and `v2`. The original `v0` version contains legacy code and is no longer supported, so it's recommended to use `v1` or `v2`.

Both `v1` and `v2` share the same basic API so in most scenarios can be used interchangeably. The `v1` version is implemented in pure Python, while `v2` has its core logic implemented in Rust and is over 100 times faster. Hence, if performance and speed are of the essence, `v2` is the way to go.


## Usage

You can import the Python classes directly, or create pre-defined environments with `gym`:


```python

import gym
from gym_chess import ChessEnvV1, ChessEnvV2

env1 = ChessEnvV1()
env2 = ChessEnvV2()

env1 = gym.make('ChessVsSelf-v1')
env2 = gym.make('ChessVsSelf-v2')

```

You can also play against a random bot:

``` python

env = gym.make('ChessVsSelf-v1')

```


## Play

Moves are pre-calculated for the current state and can be accessed from the environment. You can also access them in the form of actions from the environment action space.

Once you have chosen a move, make sure to convert it into an action (or select an action directly) and pass it to the environment to get the next state.

``` python

import random
from gym_chess import ChessEnvV1

env = ChessEnvV1() # or ChessEnvV2

# current state
state = env.state

# select a move and convert it into an action
moves = env.possible_moves
move = random.choice(moves)
action = env.move_to_actions(move)

# or select an action directly
actions = env.possible_actions
action = random.choice(actions)

# pass it to the env and get the next state
new_state, reward, done, info = env.step(action)

```

Reset the environment:

``` python

initial_state = env.reset()

```

## Visualise the chess board and moves

Visualise the current state of the chess game:

``` python

env.render()

```

```shell
    -------------------------
 8 |  ♖  ♘  ♗  ♕  ♔  ♗  ♘  ♖ |
 7 |  ♙  ♙  ♙  ♙  ♙  ♙  ♙  ♙ |
 6 |  .  .  .  .  .  .  .  . |
 5 |  .  .  .  .  .  .  .  . |
 4 |  .  .  .  .  .  .  .  . |
 3 |  .  .  .  .  .  .  .  . |
 2 |  ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟ |
 1 |  ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜ |
    -------------------------
      a  b  c  d  e  f  g  h
```


You can also visualise multiple moves:

```python

moves = env.possible_moves
env.render_moves(moves[10:12] + moves[16:18])

```


## API

### Initialize environment

#### `ChessEnvV1(player_color="WHITE", opponent="random", log=True, initial_state=DEFAULT_BOARD)`

- `opponent`: can be `"random"`, `"none"` or a function. Tells the environment whether to use a bot that picks a random move, play against self or use a specific bot policy (default: `"random"`)
- `log`: `True` or `False`, specifies whether to log every move and render every new state (default: `True`)
- `initial_state`: initial board positions, the default value is the default chess starting board. You can specify a custom board. View scripts `gym_chess/test/v1` for some examples
- `player_color`: `"WHITE"` or `"BLACK"`, only useful if playing against a bot (default: `"WHITE"`)


#### `env.get_possible_moves(state=state, player="WHITE", attack=False)`

This method will calculate the possible moves. By default they are calculated at the current state for the current player (`state.current_player`).

- `state`: (optional) state for which to calculate the moves
- `player`: (optional) "WHITE" or "BLACK", specifies the player
- `attack`: if set to True, will return the **attacks** instead of moves


## Move specification:

Moves are encoded as either:
- a tuple of coordinates `((from_x, from_y), (to_x, to_y))`
- or a string e.g. `"CASTLE_KING_SIDE_WHITE"`, `"CASTLE_QUEEN_SIDE_BLACK"`, `"RESIGN"`

Moves are pre-calculated for every new state and stored in `possible_moves`.


## State and differences between v1 and v2

`v1` and `v2` share most of the API, but the internals a little bit different.

For instance `v1` stores the board matrix directly in the state as `env.state`, while in `v2` the state is a dictionary where board can be accessed with `env.state['board']`.

```python
>>> print(env.state) # v1
>>> print(env.state['board']) # v2
```
```shell
[[-3, -5, -4, -2, -1, -4, -5, -3],
 [-6, -6, -6, -6, -6, -6, -6, -6],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [6, 6, 6, 6, 6, 6, 6, 6],
 [3, 5, 4, 2, 1, 4, 5, 3]]
```


Every integer represents a piece. Positive pieces are white and negative ones are black.

Piece IDs are stored in constants that can be imported.

```python
from gym_chess.envs.chess_v1 import (
    KING_ID,
    QUEEN_ID,
    ROOK_ID,
    BISHOP_ID,
    KNIGHT_ID,
    PAWN_ID,
)
```

The schema is:

```python
EMPTY_SQUARE_ID = 0
KING_ID = 1
QUEEN_ID = 2
ROOK_ID = 3
BISHOP_ID = 4
KNIGHT_ID = 5
PAWN_ID = 6
```

Additional information can be found in other attributes of the environment:

```python
env.current_player
env.white_king_castle_possible
env.white_queen_castle_possible
env.black_king_castle_possible
env.black_queen_castle_possible
env.white_king_on_the_board
env.black_king_on_the_board
```


## Examples

Examples can be found in `gym_chess/example`. The `v1` examples are valid for both the `v1` and `v2` environments.


# Testing

Run all the tests with `pytest`.


# Code linting and fixing

Code fixing is done with [black](https://github.com/psf/black) with max line width of 100 characters with the command `black -l 100 .` No config needed.

Rust code is formatted with `cargo fmt`.


# Building the Rust code

The `v2` environment uses a chess engine implemented in Rust that uses [PyO3](https://github.com/PyO3/pyo3) to bind to the Python interpreter. Rust is an amazing compiled language and this project holds 2 configurations:

- `Cargo.py.toml` is used to build the library into a Python module with `setup.py`
- `Cargo.dev.toml` is used to build directly with `cargo` and to access the library in the `main.rs` script for development purposes

Note: we haven't found a way to specify the Cargo toml file to either process, so copy the contents of the config you want to use into `Cargo.toml` to make it work.


# Notes:

En-passant moves are not currently supported in the V1 environment.


# References

- https://pyo3.rs/v0.4.1/print.html
- https://github.com/PyO3/pyo3
- https://www.forrestthewoods.com/blog/how-to-debug-rust-with-visual-studio-code/


# Benchmarks

The `v2` environment is over 100 times faster than the `v1` environment. However, since most of the code is written in Rust, it's generally harder to debug.

```python

from gym_chess import ChessEnvV1, ChessEnvV2

env_v1 = ChessEnvV1()
env_v2 = ChessEnvV2()

# v1: written in Python
>>> %timeit -n 50 -r 8 env_v1.get_possible_moves()
## 29.5 ms ± 872 µs per loop (mean ± std. dev. of 8 runs, 50 loops each)

# v2: compiled in Rust
>>> %timeit -n 50 -r 8 env_v2.get_possible_moves()
## 240 µs ± 31.9 µs per loop (mean ± std. dev. of 8 runs, 50 loops each)

```
