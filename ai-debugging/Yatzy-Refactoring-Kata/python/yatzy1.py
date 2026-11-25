from itertools import product


# Architecture: Yatzy contains score-calculation methods for the Yatzy dice game.
# It supports both static score methods with individual dice arguments and
# instance methods whose dice are stored by __init__ in a five-element list.
class Yatzy:
    
    @staticmethod
    def score_with_joker(dice: list, scoring_function):
        joker_positions = [index for index, die in enumerate(dice) if die == 0]
        highest_score = None

        for joker_values in product(range(1, 7), repeat=len(joker_positions)):
            substituted_dice = dice.copy()
            for position, value in zip(joker_positions, joker_values):
                substituted_dice[position] = value
            score = scoring_function(*substituted_dice)
            if highest_score is None or score > highest_score:
                highest_score = score

        return highest_score

    # Logic: Adds all five supplied dice values.
    # Read: Five integer dice values d1 through d5.
    # Output: The sum of the five dice values.
    @staticmethod
    def chance(d1, d2, d3, d4, d5):
        total = 0
        total += d1
        total += d2
        total += d3
        total += d4
        total += d5
        return total

    # Logic: Tallies each die value and awards 50 only when one face appears five times.
    # Read: A sequence/list of five integer dice values.
    # Output: 50 for a Yatzy, otherwise 0.
    @staticmethod
    def yatzy(dice):
        counts = [0] * (len(dice) + 1)
        for die in dice:
            counts[die - 1] += 1
        for i in range(len(counts)):
            if counts[i] == 5:
                return 50
        return 0

    # Logic: Adds 1 for each supplied die whose value is 1.
    # Read: Five integer dice values d1 through d5.
    # Output: The number of ones multiplied by 1.
    @staticmethod
    def ones(d1, d2, d3, d4, d5):
        sum = 0
        if (d1 == 1):
            sum += 1
        if (d2 == 1):
            sum += 1
        if (d3 == 1):
            sum += 1
        if (d4 == 1):
            sum += 1
        if (d5 == 1):
            sum += 1

        return sum

    # Logic: Adds 2 for each supplied die whose value is 2.
    # Read: Five integer dice values d1 through d5.
    # Output: The number of twos multiplied by 2.
    @staticmethod
    def twos(d1, d2, d3, d4, d5):
        sum = 0
        if (d1 == 2):
            sum += 2
        if (d2 == 2):
            sum += 2
        if (d3 == 2):
            sum += 2
        if (d4 == 2):
            sum += 2
        if (d5 == 2):
            sum += 2
        return sum

    # Logic: Adds 3 for each supplied die whose value is 3.
    # Read: Five integer dice values d1 through d5.
    # Output: The number of threes multiplied by 3.
    @staticmethod
    def threes(d1, d2, d3, d4, d5):
        s = 0
        if (d1 == 3):
            s += 3
        if (d2 == 3):
            s += 3
        if (d3 == 3):
            s += 3
        if (d4 == 3):
            s += 3
        if (d5 == 3):
            s += 3
        return s

    # Logic: Initializes the instance by storing five dice in positional order.
    # Read: Up to five integer dice values d1 through _5, each defaulting to 0.
    # Output: No return value; creates the instance's five-element dice list.
    def __init__(self, d1=0, d2=0, d3=0, d4=0, _5=0):
        self.dice = [0] * 5
        self.dice[0] = d1
        self.dice[1] = d2
        self.dice[2] = d3
        self.dice[3] = d4
        self.dice[4] = _5

    # Logic: Iterates over the instance dice and adds 4 for each die equal to 4.
    # Read: The instance's five-element dice list.
    # Output: The number of fours multiplied by 4.
    def fours(self):
        sum = 0
        for at in range(5):
            if (self.dice[at] == 4):
                sum += 4
        return sum

    # Logic: Iterates over the instance dice and adds 5 for each die equal to 5.
    # Read: The instance's five-element dice list.
    # Output: The number of fives multiplied by 5.
    def fives(self):
        s = 0
        i = 0
        for i in range(len(self.dice)):
            if (self.dice[i] == 5):
                s = s + 5
        return s

    # Logic: Iterates over the instance dice and adds 6 for each die equal to 6.
    # Read: The instance's five-element dice list.
    # Output: The number of sixes multiplied by 6.
    def sixes(self):
        sum = 0
        for at in range(len(self.dice)):
            if (self.dice[at] == 6):
                sum = sum + 6
        return sum

    # Logic: Tallies all five dice and scans faces from highest to lowest for a pair.
    # Read: Five integer dice values d1 through d5.
    # Output: Twice the highest face occurring exactly twice, otherwise 0.
    def score_pair(self, d1, d2, d3, d4, d5):
        counts = [0] * 6
        counts[d1 - 1] += 1
        counts[d2 - 1] += 1
        counts[d3 - 1] += 1
        counts[d4 - 1] += 1
        counts[d5 - 1] += 1
        at = 0
        for at in range(6):
            if (counts[6 - at - 1] == 2):
                return (6 - at) * 2
        return 0

    # Logic: Tallies dice, counts complete pairs by face, and requires exactly two pairs.
    # Read: Five integer dice values d1 through d5.
    # Output: Twice the sum of the two pair face values, otherwise 0.
    @staticmethod
    def two_pair(d1, d2, d3, d4, d5):
        counts = [0] * 6
        counts[d1 - 1] += 1
        counts[d2 - 1] += 1
        counts[d3 - 1] += 1
        counts[d4 - 1] += 1
        counts[d5 - 1] += 1
        pairs = [i + 1 for i in range(6) if counts[i] >= 2]

        if len(pairs) == 2:
            return sum(pairs) * 2
        return 0

    # Logic: Tallies all faces and returns the first face occurring at least four times.
    # Read: Five integer dice values _1, _2, d3, d4, and d5.
    # Output: Four times that face value, or 0 if no face occurs four times.
    @staticmethod
    def four_of_a_kind(_1, _2, d3, d4, d5):
        tallies = [0] * 6
        tallies[_1 - 1] += 1
        tallies[_2 - 1] += 1
        tallies[d3 - 1] += 1
        tallies[d4 - 1] += 1
        tallies[d5 - 1] += 1
        for i in range(6):
            if (tallies[i] >= 4):
                return (i + 1) * 4
        return 0

    # Logic: Tallies all faces and returns the first face occurring at least three times.
    # Read: Five integer dice values d1 through d5.
    # Output: Three times that face value, or 0 if no face occurs three times.
    @staticmethod
    def three_of_a_kind(d1, d2, d3, d4, d5):
        t = [0] * 6
        t[d1 - 1] += 1
        t[d2 - 1] += 1
        t[d3 - 1] += 1
        t[d4 - 1] += 1
        t[d5 - 1] += 1
        for i in range(6):
            if (t[i] >= 3):
                return (i + 1) * 3
        return 0

    # Logic: Tallies all faces and verifies that faces 1 through 5 occur exactly once each.
    # Read: Five integer dice values d1 through d5.
    # Output: 15 for a small straight, otherwise 0.
    @staticmethod
    def smallStraight(d1, d2, d3, d4, d5):
        tallies = [0] * 6
        tallies[d1 - 1] += 1
        tallies[d2 - 1] += 1
        tallies[d3 - 1] += 1
        tallies[d4 - 1] += 1
        tallies[d5 - 1] += 1
        if (tallies[0] == 1 and
                tallies[1] == 1 and
                tallies[2] == 1 and
                tallies[3] == 1 and
                tallies[4] == 1):
            return 15
        return 0

    # Logic: Tallies all faces and verifies that faces 2 through 6 occur exactly once each.
    # Read: Five integer dice values d1 through d5.
    # Output: 20 for a large straight, otherwise 0.
    @staticmethod
    def largeStraight(d1, d2, d3, d4, d5):
        tallies = [0] * 6
        tallies[d1 - 1] += 1
        tallies[d2 - 1] += 1
        tallies[d3 - 1] += 1
        tallies[d4 - 1] += 1
        tallies[d5 - 1] += 1
        if (tallies[1] == 1 and
                tallies[2] == 1 and
                tallies[3] == 1 and
                tallies[4] == 1
                and tallies[5] == 1):
            return 20
        return 0

    # Logic: Tallies faces, identifies one face occurring at least twice and one at least three times.
    # Read: Five integer dice values d1 through d5.
    # Output: The sum of twice the pair face and three times the triple face, otherwise 0.
    @staticmethod
    def fullHouse(d1, d2, d3, d4, d5):
        tallies = [0] * 6
        for die in (d1, d2, d3, d4, d5):
            tallies[die - 1] += 1

        if sorted(tallies) == [0, 0, 0, 0, 2, 3]:
            triple = next(i + 1 for i, count in enumerate(tallies) if count == 3)
            pair = next(i + 1 for i, count in enumerate(tallies) if count == 2)
            return triple * 3 + pair * 2

        return 0
