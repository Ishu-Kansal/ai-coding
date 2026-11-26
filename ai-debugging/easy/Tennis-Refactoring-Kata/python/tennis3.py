class TennisGame3:
    def __init__(self, player1_name, player2_name):
        self.p1_n = player1_name
        self.p2_n = player2_name
        self.p1 = 0
        self.p2 = 0
        self.isActive = True
        self.winner = None

    def won_point(self, n):
        if not self.isActive:
            raise ValueError("Game is already over")

        if n == self.p1_n:
            self.p1 += 1
        else:
            self.p2 += 1

        if self.p1 >= 4 and self.p1 - self.p2 >= 2:
            self.isActive = False
            self.winner = self.p1_n
        elif self.p2 >= 4 and self.p2 - self.p1 >= 2:
            self.isActive = False
            self.winner = self.p2_n

    def score(self):
        if not self.isActive:
            return "Win for " + self.winner

        if (self.p1 < 4 and self.p2 < 4) and (self.p1 + self.p2 < 6):
            p = ["Love", "Fifteen", "Thirty", "Forty"]
            s = p[self.p1]
            return s + "-All" if (self.p1 == self.p2) else s + "-" + p[self.p2]
        else:
            if self.p1 == self.p2:
                return "Deuce"
            s = self.p1_n if self.p1 > self.p2 else self.p2_n
            return (
                "Advantage " + s
                if ((self.p1 - self.p2) * (self.p1 - self.p2) == 1)
                else "Win for " + s
            )
