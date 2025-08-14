# qos/qos/rl_agent.py

import os
import json
import random
import pickle
from collections import defaultdict

class RLAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.995):
        self.q_table = defaultdict(lambda: [0.0 for _ in actions])
        self.actions = actions
        self.lr = learning_rate
        self.df = discount_factor
        self.er = exploration_rate
        self.ed = exploration_decay

    def get_state(self, traffic, service):
        return f"{service}:{min(traffic // 50, 10)}"  # bucketized state

    def choose_action(self, state):
        if random.random() < self.er:
            return random.choice(range(len(self.actions)))
        return max(range(len(self.actions)), key=lambda x: self.q_table[state][x])

    def learn(self, state, action, reward, next_state):
        old_value = self.q_table[state][action]
        future_max = max(self.q_table[next_state])
        self.q_table[state][action] = old_value + self.lr * (reward + self.df * future_max - old_value)

    def decay_exploration(self):
        self.er *= self.ed

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.q_table.update(pickle.load(f))
