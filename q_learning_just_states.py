import random, time
import numpy as np
import gym
from gym_chess import ChessEnvV1, ChessEnvV2

class q_learning_agent(object):
    def __init__(self, environment, alpha=0.2, discount=1.0, epsilon=0.15):
        # set hyperparameters
        self.alpha = alpha          #learning rate
        self.discount = discount    #discount factor
        self.epsilon = epsilon      #epsilon greedy term

        # create value lookup table
        self.Q = {}

        # set environment
        self.env = environment

        self.total_extra_time = 0
        self.total_atm = 0
        self.total_ns = 0
        self.total_en = 0

    def reset_memory(self):
        # resets the value lookup table
        self.Q = {}
    
    def train(self, stop_time):
        no_episodes = 0
        episode_rewards = []

        print('Starting position:')
        self.env.render()
        print("Training...")
        start = time.time()

        # loop for each episode
        #for i in range(no_episodes):
        while((time.time()-start)<stop_time):
            no_episodes += 1
            total_reward = 0    # total reward collected over this episode
            self.env.reset()

            # loop for each action in an episode
            done = False
            while(not done):
                state = self.env.state
                reward = 0

                # White's move
                available_actions = self.env.possible_actions
                # make sure all actions are initialized in the lookup table
                for option in available_actions:
                    state_rep = self.post_move_state(state, self.env.player, option)
                    if(state_rep not in self.Q):
                        self.Q[state_rep] = 0  #initialise all action value pairs as zero

                action = self.choose_egreedy_action(state, available_actions)
                new_state, white_move_reward, done, info = self.env.white_step(action)
                reward += white_move_reward

                if(not done):   # if white's move ended the game, black does not move
                    # Black's move
                    black_actions = self.env.get_possible_actions()
                    new_state, black_move_reward, done, info = self.env.black_step(random.choice(black_actions))
                    reward += black_move_reward
                
                if(done):
                    # when the new state is terminal there are no further actions from it and its Q value is 0
                    self.update_table(state, action, reward)
                else:
                    self.update_table(state, action, reward, new_state)

                total_reward += reward
            
            episode_rewards.append(round(total_reward, 1))

        end = time.time()

        # Create an array to store the rolling averages
        average_rewards = np.zeros_like(episode_rewards, dtype=float)

        # Calculate the rolling averages
        over = no_episodes//50
        for i in range(over-1, len(episode_rewards)):
            average_rewards[i] = np.mean(episode_rewards[i+1-over:i+1])

        print("Training complete")
        print(f'Time taken: {round(end-start, 1)}')
        print(f'Extra time: {round(self.total_extra_time, 1)}')
        print(f'Action to move time: {round(self.total_atm, 1)}')
        print(f'New state time: {round(self.total_ns, 1)}')
        print(f'Encoding time: {round(self.total_en, 1)}')
        print(f"Number of episodes: {no_episodes}")
        print(f"{len(self.Q)} states have been assigned values")
        
        return(average_rewards)
    
    def update_table(self, state, action, reward, new_state=None):
        state_rep = self.post_move_state(state, self.env.player, action)
        
        if new_state == None:
            ## new state is terminal so has a value of 0
            self.Q[state_rep] += self.alpha*(reward - self.Q[state_rep])
        else:
            available_actions = self.env.possible_actions

            #make sure all actions are initialised in the lookup table
            for option in available_actions:
                new_state_option_rep = self.post_move_state(new_state, self.env.player, option)
                if(new_state_option_rep not in self.Q):
                    self.Q[new_state_option_rep] = 0  #initialise all action value pairs as zero

            best_action = self.best_action(new_state, available_actions)
            new_state_rep = self.post_move_state(new_state, self.env.player, best_action)
            # update Q value
            self.Q[state_rep] += self.alpha*(reward + self.discount*self.Q[new_state_rep] - self.Q[state_rep])

    def choose_egreedy_action(self, state, actions):
        if(random.random() > self.epsilon):
            # select action with the largest value
            chosen_action = self.best_action(state, actions)
        else:
            # select random action
            chosen_action = random.choice(actions)
        
        return chosen_action
    
    def best_action(self, state, actions):
        # select action with the largest value
        values = [self.Q[self.post_move_state(state, self.env.player, action)] for action in actions]
        max_value = max(values)

        # make sure that if there are multiple actions with the max value, one is chosen at random
        potential_actions = [actions[i] for i in range(len(actions)) if values[i]==max_value]
        best_action = random.choice(potential_actions)

        return best_action

    def post_move_state(self, state, player, action):
        start = time.time()
        move = self.env.action_to_move(action)
        atm = time.time()
        state_rep, _ = self.env.next_state(state, player, move)
        ns = time.time()
        state_rep = self.env.encode_state(state_rep)
        end = time.time()
        self.total_extra_time += end-start
        self.total_atm += atm-start
        self.total_ns += ns-atm
        self.total_en += end-ns
        return state_rep

    def play_human(self):
        print("Starting Game:")
        self.env.reset()
        total_reward = 0
        
        # iterate through moves
        while(not self.env.done):
            self.env.render()

            available_actions = self.env.possible_actions
            encoded_state = self.env.encode_state()
            #make sure all actions are initialised in the lookup table
            for option in available_actions:
                if((encoded_state, option) not in self.Q):
                    self.Q[(encoded_state, option)] = 0  #initialise all action value pairs as zero
            action = self.best_action(encoded_state, available_actions)
            
            _, whtie_reward, _, _ = self.env.white_step(action)
            self.env.render()
            total_reward += whtie_reward
            if(self.env.done):
                break

            moves = self.env.possible_moves
            print("Possible moves:")
            for i in range(len(moves)):
                print(i, self.env.move_to_string(moves[i]))
            index = int(input())
            move = moves[index]
            action = self.env.move_to_action(move)

            _, black_reward, _, _ = self.env.black_step(action)
            total_reward += black_reward
        
        self.env.render()
        print(f'Total reward: {total_reward}')
