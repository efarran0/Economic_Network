import random
import numpy as np

class EconomyNetwork:
    def __init__(self, savings, prop, sens):
        self.sens = sens
        self.sys = {0: {
            "alpha": prop[0],
            "ro": prop[1],
            "c": 0,
            "w": 0,
            "s_h": savings[0],
            "s_f": savings[1]
        }}

    def step(self):
        t = max(self.sys.keys())
        prev = self.sys[t]

        alpha = max(0.01,
                    min(0.99,
                        prev["alpha"] + random.uniform(-self.sens,
                                                       self.sens)
                        )
                    )
        ro = max(0.01,
                 min(0.99,
                     prev["ro"] + random.uniform(-self.sens,
                                                 self.sens)
                     )
                 )

        c = (1/alpha - ro)**(-1) * (ro * prev["s_f"] + prev["s_h"])
        w = (1/ro - alpha)**(-1) * (alpha * prev["s_h"] + prev["s_f"])
        s_h = prev["s_h"] + w - c
        s_f = prev["s_f"] + c - w

        self.sys[t+1] = {
            "alpha": alpha,
            "ro": ro,
            "c": c,
            "w": w,
            "s_h": s_h,
            "s_f": s_f
        }

    def get_matrix(self):
        t = max(self.sys.keys())
        now = self.sys[t]
        agg = now["c"] + now["w"] + now["s_h"] + now["s_f"]
        c_nrm = now["c"] / agg
        w_nrm = now["w"] / agg
        s_h_nrm = now["s_h"] / agg
        s_f_nrm = now["s_f"] / agg

        matrix = np.array([
            [s_h_nrm, c_nrm],
            [w_nrm, s_f_nrm]
        ])

        return matrix