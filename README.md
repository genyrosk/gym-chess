# gym-chess

### Setup

Install the environment:

``` python

pip install -e .  

```

Play against yourself or against a random bot.

``` python

import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0')
env = gym.make('ChessVsSelf-v0')

```

### Play

You can either get available moves and convert them into the action space, or get the available actions directly. 

``` python 

import random

# moves
moves = env.get_possible_moves(state, player)
m = random.choice(moves)
action = env.move_to_actions(m)

# actions
actions = env.get_possible_actions(state, player)
action = random.choice(actions)


```


A move is a dictionary that holds the id of the piece (from 1 to 16 for white and -1 to -16 for black), its current position and its new position. 

``` python

move = {
    'piece_id': <int>,
    'pos': [<int>,<int>],
    'new_pos': [<int>,<int>]
}

```

NB: when a move is converted to an action and vice-versa, the `'pos'` attribute is dropped (it doesn't provide any useful information since the current position of a given piece is recorded in the current state). 


Pass an action to the environment and retrieve the `new state`, `reward`, `done` and `info`:

``` python 

state, reward, done, __ = env.step(action)

```

Reset the environment:

``` python 

initial_state = env.reset()

```

### Visualise the chess board

Visualise the current state of the chess game:

```

env.render()

```

Show the moves that a piece can make given a set of moves (by any/all pieces on the board)

```

# Player 1 moves
piece = 6 # white queen
env.render_moves(state, piece, moves, mode='human')

```

You can also retrieve the list of squares that pieces are attacking and defending by specifying the "attack" option:

``` python

attacking_moves = env.get_possible_moves(state, player, attack=True)

```

## TODO

- threefold repetition