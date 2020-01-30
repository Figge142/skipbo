import gameEngine

class EriksBot(gameEngine.Player):
  def __init__(self, name, *args, **kwargs):
    super().__init__(name, *args, **kwargs)

  def getMove(self, gameState, playerIndex, gameStateHistory = None, moveHistory = None):
    # Get variables needed from gameState
    buildingPiles = gameState["buildingPiles"]
    sCard = gameState["playerStockPilesTopCard"][playerIndex]
    nS = gameState["playerStockPilesN"][playerIndex]
    hand = gameState["playerHands"][playerIndex]
    discardPiles = gameState["playerDiscardPiles"][playerIndex]

    # Play any joker that comes up on stockpile on building pile 0
    if sCard == 0:
      return gameEngine.Move("S", 0, "B", 0)

    # Play stockpile if able
    for bi in range(4):
      if buildingPiles[bi] == sCard - 1:
        return gameEngine.Move("S", 0, "B", bi)

    # Look for playable card in hand (completely excluding jokers)
    for bi in range(4):
      for hi in range(5):
        if buildingPiles[bi] == hand[hi] - 1:
          return gameEngine.Move("H", hi, "B", bi)

    # No more plays - discard the first card in hand
    for hi in range(5):
      if hand[hi] != -1:
        return gameEngine.Move("H", hi, "D", 0)

    # Unreachable
    return None
