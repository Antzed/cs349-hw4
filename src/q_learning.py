import numpy as np
import src.random


class QLearning:
    """
    QLearning reinforcement learning agent.

    Arguments:
      epsilon - (float) The probability of randomly exploring the action space
        rather than exploiting the best action.
      alpha - (float) The weighting to give current rewards in estimating Q. This 
        should range [0,1], where 0 means "don't change the Q estimate based on 
        current reward" 
      gamma - (float) This is the weight given to expected future rewards when 
        estimating Q(s,a). It should be in the range [0,1]. Here 0 means "don't
        incorporate estimates of future rewards into the reestimate of Q(s,a)"

      See page 131 of Sutton and Barto's Reinforcement Learning book for
        pseudocode and for definitions of alpha, gamma, epsilon 
        (http://incompleteideas.net/book/RLbook2020.pdf).  
    """

    def __init__(self, epsilon=0.2, alpha=0.5, gamma=0.5):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def fit(self, env, steps=1000, num_bins=100):
        """
        Trains an agent using Q-Learning on an OpenAI Gymnasium Environment.

        See page 131 of Sutton and Barto's book Reinforcement Learning for
        pseudocode (http://incompleteideas.net/book/RLbook2020.pdf).
        Initialize your parameters as all zeros. Choose actions with
        an epsilon-greedy approach Note that unlike the pseudocode, we are
        looping over a total number of steps, and not a total number of
        episodes. This allows us to ensure that all of our trials have the same
        number of steps--and thus roughly the same amount of computation time.

        See (https://gymnasium.farama.org/) for examples of how to use the OpenAI
        Gymnasium Environment interface.

        In every step of the fit() function, you should sample
            two random numbers using functions from `src.random`.
            1.  First, use either `src.random.rand()` or `src.random.uniform()`
                to decide whether to explore or exploit.
            2. Then, use `src.random.choice` or `src.random.randint` to decide
                which action to choose. Even when exploiting, you should make a
                call to `src.random` to break (possible) ties.

        Please don't use `np.random` functions; use the ones from `src.random`!
        Please do not use `env.action_space.sample()`!

        Hints:
          - Use env.action_space.n and env.observation_space.n to get the
            number of available actions and states, respectively.
          - Remember to reset your environment at the end of each episode. To
            do this, call env.reset() whenever the value of "terminated or truncated" returned
            from env.step() is True.
          - In addition to resetting the environment, calling env.reset() will
            return the environment's initial state.
          - When choosing to exploit the best action rather than exploring,
            do not use np.argmax: it will deterministically break ties by
            choosing the lowest index of among the tied values. Instead,
            please *randomly choose* one of those tied-for-the-largest values.

        Arguments:
          env - (Env) An OpenAI Gymnasium environment with discrete actions and
            observations. See the OpenAI Gymnasium documentation for example use
            cases (https://gymnasium.farama.org/api/core/).
          steps - (int) The number of actions to perform within the environment
            during training.

        Returns:
          state_action_values - (np.array) The values assigned by the algorithm
            to each state-action pair as a 2D numpy array. The dimensionality
            of the numpy array should be S x A, where S is the number of
            states in the environment and A is the number of possible actions.
          rewards - (np.array) A 1D sequence of averaged rewards of length num_bins.
            Let s = int(np.ceil(steps / num_bins)), then rewards[0] should
            contain the average reward over the first s steps, rewards[1]
            should contain the average reward over the next s steps, etc.
            Please note that: The total number of steps will not always divide evenly by the 
            number of bins. This means the last group of steps may be smaller than the rest of 
            the groups. In this case, we can't divide by s to find the average reward per step 
            because we have less than s steps remaining for the last group.
        """
        n_actions, n_states = env.action_space.n, env.observation_space.n
        state_action_values = np.zeros((n_states, n_actions))
        avg_rewards = np.zeros(num_bins)
        all_rewards = []
        current_state, _ = env.reset()

        # Step grouping for rewards binning
        steps_per_bin = int(np.ceil(steps / num_bins))

        for step in range(steps):
            # Decide whether to explore or exploit
            explore = src.random.rand() < self.epsilon

            if explore:
                # Randomly choose action
                action = src.random.randint(0, n_actions)
            else:
                # Exploit: Choose best action, breaking ties randomly
                q_values = state_action_values[current_state]
                max_q_value = np.max(q_values)
                best_actions = np.flatnonzero(q_values == max_q_value)
                action = src.random.choice(best_actions)

            next_state, reward, terminated, truncated, _ = env.step(action)
            all_rewards.append(reward)

            # Update Q(s, a)
            next_q_values = state_action_values[next_state]
            best_next_q = np.max(next_q_values)
            state_action_values[current_state, action] += self.alpha * (
                reward + self.gamma * best_next_q - state_action_values[current_state, action]
            )

            current_state = next_state

            if terminated or truncated:
                current_state, _ = env.reset()

            # Update average rewards
            if (step + 1) % steps_per_bin == 0 or step == steps - 1:
                bin_index = step // steps_per_bin
                bin_start = bin_index * steps_per_bin
                bin_end = min((bin_index + 1) * steps_per_bin, steps)
                avg_rewards[bin_index] = np.mean(all_rewards[bin_start:bin_end])

        return state_action_values, avg_rewards
        
    def predict(self, env, state_action_values):
        """
        Runs prediction on an OpenAI environment using the policy defined by
        the QLearning algorithm and the state action values. Predictions are
        run for exactly one episode. Note that one episode may produce a
        variable number of steps.

        Hints:
          - You should not update the state_action_values during prediction.
          - Exploration is only used in training. During prediction, you
            should only "exploit."
          - In addition to resetting the environment, calling env.reset() will
            return the environment's initial state
          - You should use a loop to predict over each step in an episode until
            it terminates by returning `terminated or truncated=True`.
          - When choosing to exploit the best action, do not use np.argmax: it
            will deterministically break ties by choosing the lowest index of
            among the tied values. Instead, please *randomly choose* one of
            those tied-for-the-largest values.

        Arguments:
          env - (Env) An OpenAI Gymnasium environment with discrete actions and
            observations. See the OpenAI Gymnasium documentation for example use
            cases (https://gymnasium.farama.org/).
          state_action_values - (np.array) The values assigned by the algorithm
            to each state-action pair as a 2D numpy array. The dimensionality
            of the numpy array should be S x A, where S is the number of
            states in the environment and A is the number of possible actions.

        Returns:
          states - (np.array) The sequence of states visited by the agent over
            the course of the episode. Does not include the starting state.
            Should be of length K, where K is the number of steps taken within
            the episode.
          actions - (np.array) The sequence of actions taken by the agent over
            the course of the episode. Should be of length K, where K is the
            number of steps taken within the episode.
          rewards - (np.array) The sequence of rewards received by the agent
            over the course  of the episode. Should be of length K, where K is
            the number of steps taken within the episode.
        """

        states, actions, rewards = [], [], []

        # Reset environment before starting
        current_state, _ = env.reset()

        while True:
            # Exploit the best action
            q_values = state_action_values[current_state]
            max_q_value = np.max(q_values)
            best_actions = np.flatnonzero(q_values == max_q_value)
            action = src.random.choice(best_actions)

            next_state, reward, terminated, truncated, _ = env.step(action)

            states.append(next_state)
            actions.append(action)
            rewards.append(reward)

            if terminated or truncated:
                break

            current_state = next_state

        return np.array(states), np.array(actions), np.array(rewards)
