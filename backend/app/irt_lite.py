import math

class IRTEngine:
    def __init__(self, ability=0.5, lr=0.50):
        self.theta = self.to_irt(ability)   # store internally in IRT space
        self.lr = lr
        self.history = []

    # -3 to +3
    def to_irt(self, x: float):return x * 6 - 3
    
    # 0.1 to 1.0
    def from_irt(self, theta: float): return max(0.1, min(1.0, (theta + 3) / 6))

    def prob(self, theta: float, diff: float): 
        return 1 / (1 + math.exp(-(theta - diff)))

    def update(self, correct: bool, question_difficulty: float):
        diff = self.to_irt(question_difficulty)

        p = self.prob(self.theta, diff)
        x = 1 if correct else 0

        # update ONLY theta
        self.theta = self.theta + self.lr * (x - p)

        # store history (converted for readability)
        self.history.append(self.from_irt(self.theta))

        return self.from_irt(self.theta)
    
    def update_difficulty(self, target_p:int=0.6): 
        new_diff = self.theta - math.log(target_p / (1-target_p))
        return max(-3, min(3, new_diff))



if __name__ == '__main__':
    irt_engine = IRTEngine(ability=0.0)
    is_correct = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    newdiff = 0.0
    for correct in is_correct:
        irt_engine.update(correct, question_difficulty=irt_engine.to_irt(newdiff))
        newdiff = irt_engine.from_irt(irt_engine.update_difficulty())
        print(irt_engine.theta, newdiff)


