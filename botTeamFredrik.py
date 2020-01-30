import random

import gameEngine

class DiscardUserBot(gameEngine.Player):
  def __init__(self, name, nDiscardPilesUsed, *args, **kwargs):
    super().__init__(name, *args, **kwargs)
    self.nDiscardPilesUsed = nDiscardPilesUsed
    self.moveList = []

  def getPlaySMoveList(self, buildingPiles, sCard, hand, discardPiles):
    SBDistance = [(sCard - b - 1) % 12 + 1 for b in buildingPiles] # Cards between S and B. Dist between 1-12
    minDist = min(SBDistance) # One less card than minDist is needed to play S
    targetB = SBDistance.index(minDist)
    #nCardsNeeded = minDist - 1
    cardsNeeded = [(buildingPiles[targetB] + d) % 12 + 1 for d in range(minDist-1)] # Cards needed to play stockpile

    # Look for the cards needed in hand and on top of discard piles
    nJokers = 0
    trialMoveList = [None] * len(cardsNeeded)
    # First, look in hand
    for hi in range(5):
      if hand[hi] == 0:
        nJokers += 1
        continue

      for cni in range(len(cardsNeeded)):
        if hand[hi] == cardsNeeded[cni]:
          cardsNeeded[cni] = -2
          trialMoveList[cni] = gameEngine.Move("H", hi, "B", targetB)

    # Then, look in discard piles
    for di in range(self.nDiscardPilesUsed):
      if not discardPiles[di]:
        continue

      if discardPiles[di][-1] == 0:
        nJokers += 1
        continue

      for cni in range(len(cardsNeeded)):
        if discardPiles[di] == cardsNeeded[cni]:
          cardsNeeded[cni] = -2
          trialMoveList[cni] = gameEngine.Move("H", hi, "B", targetB)

    # Check if jokers can fill in all needed spots in missing cards
    nJokersNeeded = sum(m is None for m in trialMoveList)
    if nJokersNeeded > nJokers:
      # More moves needs a joker card than there are jokers available. Fail.
      return []

    # Iterate hand and discard piles for jokers and add plays accordingly as long as more jokers should be played
    nJokersUsed = 0
    for hi in range(5):
      if nJokersUsed == nJokersNeeded:
        break
      if hand[hi] == 0:
        trialMoveList[trialMoveList.index(None)] = gameEngine.Move("H", hi, "B", targetB)
        nJokersUsed += 1

    for di in range(self.nDiscardPilesUsed):
      if nJokersUsed == nJokersNeeded:
        break

      if not discardPiles[di]:
        continue

      if discardPiles[di][-1] == 0:
        trialMoveList[trialMoveList.index(None)] = gameEngine.Move("D", di, "B", targetB)
        nJokersUsed += 1

    # Finally, play the stock pile card
    trialMoveList.append(gameEngine.Move("S", 0, "B", targetB))

    return trialMoveList

  def getMoveList(self, buildingPiles, sCard, hand, discardPiles):
    # Play any joker directly
    if sCard == 0:
      return [gameEngine.Move("S", 0, "B", 0)] #TODO Decide which build pile to play on depending on gameEnginestate (maximize variance in build piles, ruin for opponent after etc)

    # Try to play non-joker from S
    playSMoveList = self.getPlaySMoveList(buildingPiles, sCard, hand, discardPiles)
    if playSMoveList:
      return playSMoveList

    # Empty hand of non-jokers
    for bi in range(4):
      for hi in range(5):
        if buildingPiles[bi] == hand[hi] - 1:
          return [gameEngine.Move("H", hi, "B", bi)]

    # Discard a card
    for hi in range(5):
      if hand[hi] != -1:
        return [gameEngine.Move("H", hi, "D", random.randint(0, max(0, self.nDiscardPilesUsed - 1)))]

  def getMove(self, gameState, playerIndex, gameStateHistory = None, moveHistory = None):
    # Get variables needed from gameState
    buildingPiles = gameState["buildingPiles"]
    sCard = gameState["playerStockPilesTopCard"][playerIndex]
    # nS = gameState["playerStockPilesN"][playerIndex]
    hand = gameState["playerHands"][playerIndex]
    discardPiles = gameState["playerDiscardPiles"][playerIndex]

    if not self.moveList:
      self.moveList += self.getMoveList(buildingPiles, sCard, hand, discardPiles)

    assert(self.moveList)
    return self.moveList.pop(0)
