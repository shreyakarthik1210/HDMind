import tensorflow as tf
import gym
from collections import deque
import numpy as np
import torch
import pickle
import torch.optim as optim

class MongoDBDataset:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client["HackUTD"]
        self.collection = self.db["HDMind"]

    def add(self, state, action, reward):
        document = {'state': Binary(pickle.dumps(state, -1)), 'action': action, 'reward': reward}
        self.collection.insert_one(document)

    def sample(self, batch_size):
        documents = self.collection.aggregate([{'$sample': {'size': batch_size}}])
        states, actions, rewards = [], [], []
        for document in documents:
            states.append(pickle.loads(document['state']))
            actions.append(document['action'])
            rewards.append(document['reward'])
        return states, actions, rewards

    def delete_all(self):
        self.collection.delete_many({})

class A3CAgent:
    def __init__(self, environment, mongo_client, db_name, collection_name):
        self.environment = environment
        self.mongo_dataset = MongoDBDataset(mongo_client, db_name, collection_name)

        self.sess = tf.Session()
        self.policy_network = self.build_policy_network()
        self.value_network = self.build_value_network()
        self.sess.run(tf.global_variables_initializer())

    def build_policy_network(self):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(self.environment.observation_space.shape[0],)),
            tf.keras.layers.Dense(self.environment.action_space.n, activation='softmax')
        ])
        model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Adam(lr=0.001))
        return model

    def build_value_network(self):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(self.environment.observation_space.shape[0],)),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(lr=0.001))
        return model

    def compute_advantages(self, states, actions, rewards, gamma):
        n_states = len(states)
        values = np.zeros(n_states)
        advantages = np.zeros(n_states)

        # Compute value estimates using Monte Carlo estimation of rewards
        for t in reversed(range(n_states)):
            if t == n_states - 1:
                values[t] = 0
            else:
                values[t] = rewards[t] + gamma * values[t + 1]

            # Update advantages using GAE formula
            delta = rewards[t] + gamma * values[t + 1] - values[t]
            advantages[t] = delta + gamma  * advantages[t + 1]

        return advantages

    def update_policy_network(self, states, actions, advantages):
         # Calculate the policy network's output
        logits = self.policy_network(states)

        # Convert the actions into one-hot vectors
        action_one_hot = torch.zeros_like(logits)
        action_one_hot.scatter_(1, actions.unsqueeze(-1), 1)

        # Calculate the policy network's loss
        policy_loss = -torch.sum(action_one_hot * logits, dim=1) * advantages
        policy_loss = policy_loss.mean()

        # Update the policy network
        self.optimizer.zero_grad()
        policy_loss.backward()
        self.optimizer.step()

    def update_value_network(self, states, rewards, gamma):
        optimizer = optim.Adam(self.parameters(), lr=0.01)

        for i in range(len(states) - 1, -1, -1):
            target_value = rewards[i] + gamma * self(states[i+1]).item()
            current_value = self(states[i]).item()

            loss = (target_value - current_value) ** 2

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        return self

    def train(self, batch_size, gamma):
        states, actions, rewards = self.mongo_dataset.sample(batch_size)
        advantages = self.compute_advantages(states, actions, rewards, gamma)
        self.update_policy_network(states, actions, advantages)
        self.update_value_network(states, rewards, gamma)

    def run(self, num_episodes, max_steps, gamma):
        for episode in range(num_episodes):
            state = self.environment.reset()
            for step in range(max_steps):
                action = self.policy_network.act(state)
                new_state, reward, done, _ = self.environment.step(action)
                self.mongo_dataset.add(state, action, reward)
                state = new_state
                if done:
                    break
            self.train(32, gamma)