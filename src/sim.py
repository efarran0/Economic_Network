import random
import numpy as np
from src.anomaly_detection import tsa


class EconomyNetwork:
    def __init__(self, savings, prop, sens, mem_input):
        self.sens = sens
        self.mem_input = mem_input
        self.sys = {
            0: {
                "alpha": prop[0],
                "rho": prop[1],
                "outliers":
                    {
                    "alpha": [False],
                    "rho": [False]
                    },
                "c": 0,
                "w": 0,
                "s_h": savings[0],
                "s_f": savings[1]
            }
        }

    def get_values(self, key):
        return [state[key] for t, state in sorted(self.sys.items())[-(self.mem_input -1):]]

    def step(self, alpha_override=None, rho_override=None):
        t = max(self.sys.keys())
        prev = self.sys[t]

        alpha = (
            alpha_override
            if alpha_override is not None
            else max(0.01, min(0.99, prev["alpha"] + random.uniform(-self.sens, self.sens)))
        )

        rho = (
            rho_override
            if rho_override is not None
            else max(0.01, min(0.99, prev["rho"] + random.uniform(-self.sens, self.sens)))
        )

        try:
            c = (1 / alpha - rho) ** (-1) * (rho * prev["s_f"] + prev["s_h"])
            w = (1 / rho - alpha) ** (-1) * (alpha * prev["s_h"] + prev["s_f"])
        except ZeroDivisionError:
            c = prev["c"]
            w = prev["w"]

        s_h = prev["s_h"] + w - c
        s_f = prev["s_f"] + c - w

        if len(self.sys) >= self.mem_input:
            alpha_vals = self.get_values('alpha') + [alpha]
            rho_vals = self.get_values('rho') + [rho]
            alpha_is_out = tsa(alpha_vals)
            rho_is_out = tsa(rho_vals)
            outliers = {
            'alpha': (prev['outliers']['alpha'] + [alpha_is_out])[-self.mem_input:],
            'rho': (prev['outliers']['rho'] + [rho_is_out])[-self.mem_input:]
            }
        else:
            outliers = {
                'alpha': [False] * (len(self.sys) + 1),
                'rho': [False] * (len(self.sys) + 1)
            }

        self.sys[t + 1] = {
            "alpha": alpha,
            "rho": rho,
            "outliers": outliers,
            "c": c,
            "w": w,
            "s_h": s_h,
            "s_f": s_f
        }

    def get_matrix(self):
        t = max(self.sys.keys())
        now = self.sys[t]
        N = now["c"] + now["w"] + now["s_h"] + now["s_f"]

        if N == 0:
            return np.zeros((2, 2))

        c_nrm = now["c"] / N
        w_nrm = now["w"] / N
        s_h_nrm = now["s_h"] / N
        s_f_nrm = now["s_f"] / N

        return np.array([
            [s_h_nrm, c_nrm],
            [w_nrm, s_f_nrm]
        ])
