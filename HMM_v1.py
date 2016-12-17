from hmmlearn import hmm
import numpy as np


import matplotlib.pyplot as plt
states = ["Rainy", "Sunny"]
n_states = len(states)

observations = ["walk", "shop", "clean"]
n_observations = len(observations)

start_probability = np.array([0.6, 0.4])

transition_probability = np.array([
  [0.7, 0.3],
  [0.4, 0.6]
])

emission_probability = np.array([
  [0.1, 0.4, 0.5],
  [0.6, 0.3, 0.1]
])

model = hmm.MultinomialHMM(n_components=n_states)
model.startprob = np.array([
  [0.7, 0.3],
  [0.4, 0.6]
])

model.emissionprob_ = np.array([
  [0.1, 0.4, 0.5],
  [0.6, 0.3, 0.1]
])
model.fit()
# predict a sequence of hidden states based on visible states
bob_says = [0, 2, 1, 1, 2, 0]
logprob, alice_hears = model.decode(bob_says, algorithm="viterbi")
print("Bob says:", ", ".join(map(lambda x: observations[x], bob_says)))
print("Alice hears:", ", ".join(map(lambda x: states[x], alice_hears)))