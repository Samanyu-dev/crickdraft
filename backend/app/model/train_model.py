"""
Offline trainer for the ball-outcome model.

There's no real ball-by-ball dataset to learn from here (the players are
fictionalized), so this generates a synthetic training set from a
hand-specified cricket domain model (ground_truth_probs below encodes
things like "higher skill_diff shifts mass from dots/wickets to
boundaries", "death overs raise both boundary and wicket risk", "low
morale under pressure raises collapse risk"), sampling actual ball
outcomes from those probabilities. A multinomial logistic regression
(softmax over 7 outcome classes) is then fit on that sampled data with
plain gradient descent - no numpy/sklearn, just lists and loops, since the
dataset and model are both small.

Run: python3 train_model.py  (writes weights.json next to this file)
"""
import json
import math
import os
import random

from features import FEATURE_NAMES, OUTCOMES

random.seed(7)

N_FEATURES = len(FEATURE_NAMES)
N_CLASSES = len(OUTCOMES)
N_SAMPLES = 2000
EPOCHS = 200
LR = 0.4
L2 = 1e-3


def ground_truth_probs(x):
    _, batter_skill, bowler_skill, skill_diff, fielding, morale, powerplay, death, pressure = x

    # base rates for an "average" ball: [0,1,2,3,4,6,W]
    probs = [0.42, 0.30, 0.06, 0.01, 0.12, 0.04, 0.05]

    # better batter relative to bowler -> more boundaries, fewer dots/wickets.
    # This is the single biggest lever on how "stat-driven vs random" matches
    # feel - a moderate rating gap should turn into a clearly better win rate,
    # not something close to a coin flip.
    shift = skill_diff * 0.55
    probs[4] += shift * 0.5
    probs[5] += shift * 0.3
    probs[0] -= shift * 0.5
    probs[6] -= shift * 0.3

    # good fielding side: tightens singles into dots, and lifts wicket risk
    field_bonus = (fielding - 0.6) * 0.10
    probs[0] += max(0, field_bonus)
    probs[1] -= max(0, field_bonus) * 0.6
    probs[6] += max(0, field_bonus) * 0.4

    # powerplay: new ball, fielding restrictions favor the bowler slightly on
    # wickets but boundaries still come from gaps
    if powerplay:
        probs[6] += 0.015
        probs[0] += 0.01

    # death overs: batters swing, so both boundaries and wickets spike
    if death:
        probs[4] += 0.05
        probs[5] += 0.05
        probs[6] += 0.03
        probs[0] -= 0.08

    # required-rate pressure pushes risk up; comfortable chases pull it down
    probs[4] += pressure * 0.05
    probs[5] += pressure * 0.04
    probs[6] += pressure * 0.03
    probs[0] -= pressure * 0.09

    # low effective morale under pressure -> real collapse risk
    if morale < 0.5:
        collapse = (0.5 - morale) * 0.3
        probs[6] += collapse
        probs[0] += collapse * 0.4

    probs = [max(0.005, p) for p in probs]
    total = sum(probs)
    return [p / total for p in probs]


def sample_features():
    batter_skill = random.uniform(0.1, 1.0)
    bowler_skill = random.uniform(0.15, 1.0)
    fielding = random.uniform(0.35, 1.0)
    morale = random.uniform(0.2, 1.0)
    powerplay = 1.0 if random.random() < 0.3 else 0.0
    death = 0.0 if powerplay else (1.0 if random.random() < 0.3 else 0.0)
    pressure = random.uniform(-0.5, 1.0)
    return [1.0, batter_skill, bowler_skill, batter_skill - bowler_skill, fielding, morale, powerplay, death, pressure]


def generate_dataset(n):
    X, Y = [], []
    for _ in range(n):
        x = sample_features()
        probs = ground_truth_probs(x)
        label = random.choices(range(N_CLASSES), weights=probs)[0]
        X.append(x)
        Y.append(label)
    return X, Y


def softmax(logits):
    m = max(logits)
    exps = [math.exp(v - m) for v in logits]
    s = sum(exps)
    return [v / s for v in exps]


def train(X, Y):
    W = [[random.gauss(0, 0.05) for _ in range(N_FEATURES)] for _ in range(N_CLASSES)]
    n = len(X)
    for epoch in range(EPOCHS):
        grad = [[0.0] * N_FEATURES for _ in range(N_CLASSES)]
        loss = 0.0
        for x, y in zip(X, Y):
            logits = [sum(W[k][f] * x[f] for f in range(N_FEATURES)) for k in range(N_CLASSES)]
            probs = softmax(logits)
            loss -= math.log(max(probs[y], 1e-9))
            for k in range(N_CLASSES):
                err = probs[k] - (1.0 if k == y else 0.0)
                for f in range(N_FEATURES):
                    grad[k][f] += err * x[f]
        for k in range(N_CLASSES):
            for f in range(N_FEATURES):
                g = grad[k][f] / n + L2 * W[k][f]
                W[k][f] -= LR * g
        if epoch % 40 == 0 or epoch == EPOCHS - 1:
            print(f"epoch {epoch:3d}  loss {loss / n:.4f}")
    return W


def main():
    X, Y = generate_dataset(N_SAMPLES)
    W = train(X, Y)
    out_path = os.path.join(os.path.dirname(__file__), "weights.json")
    with open(out_path, "w") as f:
        json.dump({"features": FEATURE_NAMES, "outcomes": OUTCOMES, "weights": W}, f, indent=2)
    print(f"wrote weights to {out_path}")


if __name__ == "__main__":
    main()
