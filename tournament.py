import gameEngine
import itertools
import time

import botTeamFredrik
import botTeamErik

class Tournament():
  def __init__(self, participants, nRounds = 1, stockPileSize = 30, pointDistribution = [1, 0], maxNbrOfMatches = 10000):
    self.participants = participants
    self.nRounds = nRounds
    self.pointDistribution = pointDistribution
    self.stockPileSize = stockPileSize
    approxNbrOfMatches = nRounds * (sum(1 for _ in itertools.combinations(self.participants, 2))) * 2
    print(f"Approx number of matches: {approxNbrOfMatches}")
    print(f"Number of matches per participant: : {nRounds * (len(self.participants) - 1) * 2}")

  def play(self):
    tournamentStartTime = time.monotonic()

    # A list to keep track of points
    pointList = [0] * len(self.participants)

    # For each round, everyone plays everyone 1-on-1 two times (both starting and going second)
    for round in range(1, 1 + self.nRounds):
      roundStartTime = time.monotonic()
      for matchupIndexes in itertools.combinations(range(len(self.participants)), 2):
        # Get the actual players that plays in this match given by the indexes in matchupIndexes
        roundPlayers = [self.participants[i] for i in matchupIndexes]
        for startingPlayer in range(len(roundPlayers)): #TODO Replace with itertools.permutation to go over every possible setup when more than 2 players play?
          # Play a game between the two players in this round
          g = gameEngine.Game(roundPlayers , stockPileSize = self.stockPileSize, startingPlayer = startingPlayer, verbose = 0)
          g.play()
          placements = g.getPlacementList()

          # Points for first and second place
          pointList[matchupIndexes[placements[0]]] += self.pointDistribution[0]
          pointList[matchupIndexes[placements[1]]] += self.pointDistribution[1]
          #TODO make this for loop if many participate

      roundEndTime = time.monotonic()
      print(f"Round {round} of {self.nRounds} is done. It took {(roundEndTime - roundStartTime) * 1000:.0f} ms. Estimated time left: {((roundEndTime - tournamentStartTime) / round * (self.nRounds - round)):.0f} seconds")

    return pointList



if __name__ == "__main__":
  # Participating bots in the tournament
  participants = []
  participants += [gameEngine.BareMinimumBot("Bare minimum Bot %d" % (i+1)) for i in range(1)]
  participants += [botTeamFredrik.DiscardUserBot("Discard Pile User %d" % (i%5), i%5) for i in range(5)]
  participants += [botTeamErik.EriksBot("Eriks Bot")]

  # Parameters for the tournament
  nRounds = 4
  stockPileSize = 30

  # Create tournament and play
  t = Tournament(participants, nRounds = nRounds, stockPileSize = stockPileSize)
  scores = t.play()

  # Display result
  participantScores = zip(participants, scores)
  participantScores = sorted(participantScores, key=lambda x: -x[1])
  print("Results:")
  print(f"{'Player':40}score   Type")
  for p, s in participantScores:
      print(f"{p.getName():40}{s:5}   {p.getType()}")
