1. Why SUMO? (Why did you choose SUMO?)
Answer:
I chose SUMO (Urban Mobility Modeling) for three main reasons:
Open source and microscopic: It's a free, open-source tool that models traffic at a microscopic level. This means it looks at the physics and behavior of each individual car (acceleration, braking, lane changes, engine type), not just abstract fluid flow. This is important for training AI.
TraCI API (Traffic Management Interface): This is the main advantage. SUMO has excellent integration with Python via TraCI. This allows me to obtain the state of the car's environment (where? What's the speed?) and transmit a command to the traffic lights (turn green!) in real time, step by step. Without this, it would have been impossible to integrate the neural network.
Realistic: SUMO supports real-world maps (OpenStreetMap), complex intersection types, and new gas models (HBEFA3), making the research results applicable to the first world.
2. Why DQN/Deep RL?
Answer:
Classical methods like Q-Learning (Q-tables) don't work for traffic control problems due to the dimensionality of the spaces.
Problem Tables: In a Q-Table, we need to create a code for each possible state. But a road state is a combination of the number of cars in each lane, their speed, and the current traffic light phase.
If an intersection can have anywhere from 0 to 50 cars in 4 lanes, the number of combinations is millions. The table becomes gigantic, and the agent will never be able to visit all the locations to learn.
Solution (Deep RL): We use a Deep Q-Network (PPO) as the approximator function. The neural network doesn't remember each state, but generalizes. It recognizes the pattern: "If there are a lot of cars, then the light is red—that's bad," even if it's the first time it's seen that exact number of cars. This allows us to work with a continuous switching space (a continuous state space), which is necessary for a continuous road network.
3. Why reward for "varying waiting times"? (Why reward for "changing waiting times"?)
Answer:
Choosing a reward function is the hardest part of RL. We chose Diff-Waiting-Time because simpler metrics don't work:
Why not just "Waiting Time"?
If a penalty is paid for the total waiting time, the agent gets a huge penalty for each step simply because there's a car on the map. It doesn't understand whether its actions have improved the situation right now. This is called the delayed reward problem.
The essence of "Diff-Waiting-Time":
We reward the agent for improving the situation.
Formula: Reward = Wait{t-1}-Wait{t}
If the agent changed the light and the traffic jam decreased, the difference is positive (reward).
If the traffic jam increased, the difference is negative (penalty).
Result: This gives the agent instant feedback (a dense reward signal). It immediately understands, "I performed this action, and, in turn, this happened," which significantly hinders learning and its own getting stuck in local minima (when the agent simply holds the red light, afraid of making things worse).
