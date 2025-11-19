# Adaptive Traffic Signal Control using RL (PPO)

A project on traffic signal control using Reinforcement Learning (PPO) in the SUMO simulator.
The system adapts to intermittent traffic and shows significant advantages over strict timers.

## 📊 Results

The algorithm was tested on the "Uneven" scenario (Rush Hour / Intermittent Flow):

| Metric | Standard Traffic Signal | AI (PPO Agent) | Improvement |
|---------|----------------------|----------------|-----------|
| **Dwell Time** | 84.2 sec | **61.9 sec** | 🟢 **+26.5%** |
| **CO2 Emissions** | 1311 kg | **1102 kg** | 🟢 **+15.9%** |
| **Queue Length** | 17.3 cars | **12.9 cars** | 🟢 **+25.9%** |
| **Avg. Speed** | 16.2 km/h | **19.2 km/h** | 🟢 **+18.7%** |

## 🛠 Installation

1. Install [SUMO Simulator](https://eclipse.dev/sumo/).
2. Clone the repository:
```bash
git clone https://github.com/vvsrq/stlc.git
cd stlc
```

Install dependencies:
```bash
pip install -r requirements.txt
```
##🚀 Launch
1. Agent training
```bash
python train_avenue.py
```
2. Visualization (See with your own eyes)
Comparison of AI and a standard traffic light:
```bash
# Launching AI
python visualize_ai.py
```

# Launching the Standard
python visualize_standard.py
3. Collecting statistics (Tables)
```bash
python compare_ultimate.py
```
📂 Project structure
my_avenue.net.xml - Road network (avenue).
traffic_*.rou.xml - Traffic scenarios (Light, Medium, Heavy, Uneven).
ppo_avenue_model.zip - Trained model.
