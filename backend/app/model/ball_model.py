import json
import math
import os
import random

_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights.json")

with open(_WEIGHTS_PATH) as f:
    _MODEL = json.load(f)

WEIGHTS = _MODEL["weights"]
OUTCOMES = _MODEL["outcomes"]
N_FEATURES = len(_MODEL["features"])


def _softmax(logits):
    m = max(logits)
    exps = [math.exp(v - m) for v in logits]
    s = sum(exps)
    return [v / s for v in exps]


def outcome_probs(x):
    logits = [sum(WEIGHTS[k][f] * x[f] for f in range(N_FEATURES)) for k in range(len(WEIGHTS))]
    return _softmax(logits)


def sample_outcome(x):
    probs = outcome_probs(x)
    return random.choices(OUTCOMES, weights=probs, k=1)[0]
