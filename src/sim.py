import random
import numpy as np

class EconomyNetwork:
    def __init__(self, savings, prop, sens):
        self.sens = sens
        self.sys = {
            0: {
                "alpha": prop[0],
                "rho": prop[1],
                "c": 0,
                "w": 0,
                "s_h": savings[0],
                "s_f": savings[1]
            }
        }

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
            # Evitar error numèric en cas d'inestabilitat extrema
            c = prev["c"]
            w = prev["w"]

        s_h = prev["s_h"] + w - c
        s_f = prev["s_f"] + c - w

        self.sys[t + 1] = {
            "alpha": alpha,
            "rho": rho,
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
            # Evitar divisió per zero si tot és 0 (molt improbable)
            return np.zeros((2, 2))

        c_nrm = now["c"] / N
        w_nrm = now["w"] / N
        s_h_nrm = now["s_h"] / N
        s_f_nrm = now["s_f"] / N

        return np.array([
            [s_h_nrm, c_nrm],
            [w_nrm, s_f_nrm]
        ])
