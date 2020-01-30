import random

# TODO boolean isPlayed (can only play once, getPlacementList only works on played games)
# TODO abort games when nPlayers == 2 for example, if only top 2 players in 4 player game gets points
class Game:
  def __init__(self, players, stockPileSize = 30, startingPlayer = 0, verbose = 2):
    self.players = players
    self.playingIndexList = list(range(len(players)))
    self.pointList = [0] * len(players)
    self.startingPlayer = startingPlayer
    self.stockPileSize = stockPileSize

    self.deck = self.Deck()
    self.gameState = self.startNewGameState(stockPileSize)

    self.gameStateHistory = []
    self.moveHistory = []

    self.verbose = verbose

  def startNewGameState(self, nCardsInStockPile):
    gameState = {}

    # Shared
    gameState["buildingPiles"] = [0, 0, 0, 0]

    # Per player
    gameState["playerStockPilesTopCard"] = [self.deck.draw() for player in self.players] # TODO keep list of these cards in game? Else, someone ocould get too many two's or jokers in a game (theoretically)
    gameState["playerStockPilesN"] = [nCardsInStockPile for player in self.players]
    gameState["playerHands"] = [[-1] * 5 for p in self.players]
    gameState["playerDiscardPiles"] = [[[] for i in range(4)] for p in self.players]

    return gameState

  # Small class to keep track of the deck. If it runs out, a new, shuffled deck is added.
  class Deck:
    def __init__(self):
      self.cards = []
      self.addDeckSet()

    def addDeckSet(self):
      deckSet = []
      deckSet += list(range(1, 13)) * 12
      deckSet += [0] * 18
      random.shuffle(deckSet)
      self.cards += deckSet

    def draw(self):
      if not self.cards:
        self.addDeckSet()

      return self.cards.pop()

  def printv(self, v, *args):
    if self.verbose >= v:
      print(*args)
    else:
      pass

  def isMoveLegal(self, move, hasDiscarded, playerIndex):
    # Check if source and destination is a valid combo
    if not move.isValid():
      return False

    # Check if this is the second discard play (Impossible?)
    if hasDiscarded and move.isDiscard():
      return False

    # Can't discard from an empty slot
    if move.isDiscard() and self.gameState["playerHands"][playerIndex][move.sourceIndex] == -1:
      return False

    #Any card can be discarded
    if move.destination == "D":
      return True

    # Get value of source cards
    cardValue = -2
    if move.source == "H":
      cardValue = self.gameState["playerHands"][playerIndex][move.sourceIndex]
    elif move.source == "D":
      cardValue = self.gameState["playerDiscardPiles"][playerIndex][move.sourceIndex][-1]
    elif move.source == "S":
      cardValue = self.gameState["playerStockPilesTopCard"][playerIndex]

    assert(move.destination) == "B"

    # Jokers are always valid
    if cardValue == 0:
      return True

    # Valid if it can be placed on build pile
    destinationValue = self.gameState["buildingPiles"][move.destinationIndex]
    return cardValue == destinationValue + 1

  def printGameState(self):
    print(self.gameState)

  def printPlayerState(self, playerIndex):
    print("State for player %s" % self.players[playerIndex].getName())
    print("Building piles:")
    print(self.gameState["buildingPiles"])
    print("Hand:")
    print(self.gameState["playerHands"][playerIndex])
    print("Discard piles:")
    print(self.gameState["playerDiscardPiles"][playerIndex])
    print("Stock pile top card: %d (there are %d cards left)" % (self.gameState["playerStockPilesTopCard"][playerIndex], self.gameState["playerStockPilesN"][playerIndex]))

  def makeMove(self, move, playerIndex):
    # Make a move that is already checked for validity and legality
    if move.isPlay():
      if move.isHandPlay():
        self.gameState["playerHands"][playerIndex][move.sourceIndex] = -1
        self.gameState["buildingPiles"][move.destinationIndex] += 1
      if move.isDiscardPlay():
        self.gameState["playerDiscardPiles"][playerIndex][move.sourceIndex].pop()
        self.gameState["buildingPiles"][move.destinationIndex] += 1
      if move.isStockPilePlay():
        self.gameState["playerStockPilesN"][playerIndex] -= 1
        self.gameState["buildingPiles"][move.destinationIndex] += 1
        if self.gameState["playerStockPilesN"][playerIndex] > 0:
          self.gameState["playerStockPilesTopCard"][playerIndex] = self.deck.draw()
        else:
          self.gameState["playerStockPilesTopCard"][playerIndex] = -1
      self.checkForFullBuildingPiles() #TODO Only check the one affected

    if move.isDiscard():
      card = self.gameState["playerHands"][playerIndex][move.sourceIndex]
      self.gameState["playerDiscardPiles"][playerIndex][move.destinationIndex].append(card)
      self.gameState["playerHands"][playerIndex][move.sourceIndex] = -1

  def checkForFullBuildingPiles(self):
    for i in range(4):
      if self.gameState["buildingPiles"][i] >= 12:
        self.gameState["buildingPiles"][i] -= 12

  def play(self):
    maxNumberOfTurns = 500 + 8 * self.stockPileSize # End games after many turns if they take an absurd time to finish
    self.printv(1, "Starting a game! The players are:")
    [self.printv(1, f"{p.getName():35}type: {p.getType()}") for p in self.players]
    for turn in range(1, maxNumberOfTurns+1):
      self.printv(2, f"Turn {turn}. Stock pile cards left: {self.gameState['playerStockPilesN']}")
      for playerIndex in range(len(self.players)):
        # Start with the starting player by skipping players before on first turn
        if turn == 1 and playerIndex < self.startingPlayer:
          continue

        # Check if game is over
        if len(self.playingIndexList) == 1 or turn == maxNumberOfTurns:
          self.printv(1, "Game is over!")
          return self.pointList

        # Only do the turns for still playing players
        if playerIndex not in self.playingIndexList:
          continue
        player = self.players[playerIndex]

        # Do all the moves the players wants
        hasDiscarded = False
        handSize = 0 # Forcing to zero triggers drawing to five first loop
        while (True):
          # Draw to 5 if legal
          if handSize == 0:
            for handSlotIndex in range(5):
              if self.gameState["playerHands"][playerIndex][handSlotIndex] == -1:
                self.gameState["playerHands"][playerIndex][handSlotIndex] = self.deck.draw()
            handSize = 5

          # Get a move from the player
          try:
            move = player.getMove(self.gameState, playerIndex)
          except Exception as e:
            points = sum(self.gameState["playerStockPilesN"])
            self.printv(0, f"Unhandeled exception: Player {player.getName()} is out with {-points} points!")
            self.pointList[playerIndex] = -points
            self.playingIndexList.remove(playerIndex)
            print(e)
            # raise e
            print("Moving on with the game...")
            break

          # Check if move is legal
          if not self.isMoveLegal(move, hasDiscarded, playerIndex):
            points = sum(self.gameState["playerStockPilesN"])
            self.printv(0, f"Illegal move {move.toString()} proposed: Player {player.getName()} is out with {-points} points!")
            self.pointList[playerIndex] = -points
            self.playingIndexList.remove(playerIndex)
            break

          # Execute move
          self.printv(3, "Player %s is making move %s" % (player.getName(),  move.toString()))
          self.makeMove(move, playerIndex)
          if move.isDiscard():
            hasDiscarded = True
          if move.isFromHand():
            handSize -= 1

          # A player takes extra turns until they must discard (i.e. as long as they play all 5 cards from hand)
          if hasDiscarded:
            break

          # Check if the player won
          if self.gameState["playerStockPilesN"][playerIndex] == 0:
            points = sum(self.gameState["playerStockPilesN"])
            self.printv(1, f"Player {player.getName()} is out with {points} points!")
            self.pointList[playerIndex] = points
            self.playingIndexList.remove(playerIndex)
            break

  def getPlacementList(self):
    # Get a list of placements where [1, 0, 2] means the first player came second, second player came first and third player came third
    playerIndexPoints = zip(range(len(self.players)), self.pointList)
    playerIndexPoints = sorted(playerIndexPoints, key=lambda x: -x[1])
    placements = [playerIndex for playerIndex, points in playerIndexPoints]
    return placements


# Small class to keep track of one move, represented by a string of 4 characters
class Move:
  def __init__(self, source, sourceIndex, destination, destinationIndex, cardValue = -1, isJoker = False):
    self.source = source
    self.sourceIndex = sourceIndex

    self.destination = destination
    self.destinationIndex = destinationIndex

    self.cardValue = cardValue
    self.isJoker = isJoker

    if not self.isValid():
      raise ValueError("Invalid move: %s" % self.toString())

  def isFromHand(self):
    return self.source == "H"

  def isPlay(self):
    return self.destination == "B"

  def isDiscardPlay(self):
    return self.source == "D"

  def isHandPlay(self):
    return self.isFromHand() and self.destination == "B"

  def isStockPilePlay(self):
    return self.source == "S"

  def isDiscard(self):
    return self.destination == "D"

  def isValid(self):
    # Check some input
    if len(self.source) != 1:
      return False
    if len(self.destination) != 1:
      return False

    # Check source/destination combo
    if self.destination == "B":
      if self.source not in "HDS":
        return False
    elif self.destination == "D":
      if self.source not in "H":
        return False
    else:
      return False

    # Check source slot
    if self.source == "H":
      if self.sourceIndex < 0 or self.sourceIndex > 4:
        return False
    if self.source == "D":
      if self.sourceIndex < 0 or self.sourceIndex > 3:
        return False
    if self.source == "S":
      if self.sourceIndex != 0:
        return False

    # Check destination slot
    if self.destination == "B":
      if self.destinationIndex < 0 or self.destinationIndex > 3:
        return False
    if self.destination == "D":
      if self.destinationIndex < 0 or self.destinationIndex > 3:
        return False

    return True

  def toString(self):
    s = f"{self.source}{self.sourceIndex}{self.destination}{self.destinationIndex}"
    if self.cardValue != -1:
      s += f"{self.cardValue}"
      if self.isJoker:
        s += f"J"
      else:
        s += "N"
    return s


# A player class to inherit from
class Player:
  def __init__(self, name):
    self.name = name

  def getName(self):
    return self.name

  def getType(self):
    return self.__class__.__name__

  def getMove(self, gameState, playerIndex, gameStateHistory = None, moveHistory = None):
     raise NotImplementedError("getMove must be implemented in subclass")



# A reference bot. This bot is really bad, but it is designed to actually end the game even if all players are instances of it
class BareMinimumBot(Player):
  def getMove(self, gameState, playerIndex, gameStateHistory = None, moveHistory = None):
    # Play any joker that comes up on stockpile on building pile 0
    if gameState["playerStockPilesTopCard"][playerIndex] == 0:
      return Move("S", 0, "B", 0)

    # Play stockpile if able
    for bi in range(4):
      if gameState["buildingPiles"][bi] == gameState["playerStockPilesTopCard"][playerIndex] - 1:
        return Move("S", 0, "B", bi)

    # Look for playable card in hand (completely excluding jokers)
    for bi in range(4):
      for hi in range(5):
        if gameState["buildingPiles"][bi] == gameState["playerHands"][playerIndex][hi] - 1:
          return Move("H", hi, "B", bi)

    # No more plays - discard the first card in hand
    for hi in range(5):
      if gameState["playerHands"][playerIndex][hi] != -1:
        return Move("H", hi, "D", 0)

    # Unreachable
    return None



if __name__ == "__main__":
  import botTeamFredrik
  import botTeamErik

  # Make a list of all the players that should play
  players = []
  # Add bots that do the bare minimum (don't use discard piles, don't use jokers, etc.)
  players += [BareMinimumBot("Bare minimum Bot %d" % (i+1)) for i in range(1)]
  # Add bots that use a certain number of discard piles (0-4) as a benchmark (not very smart either, but much better than Bare minimum bot)
  players += [botTeamFredrik.DiscardUserBot("Discard Pile User (%d)" % (i%5), i%5) for i in range(5)]
  # Add one bot representing team Erik
  players += [botTeamErik.EriksBot("Eriks Bot")]

  # Create game and play it
  g = Game(players = players, stockPileSize = 30)
  pointList = g.play()

  # Display result
  playerPoints = zip(players, pointList)
  playerPoints = sorted(playerPoints, key=lambda x: -x[1])
  print("Results:")
  print(f"{'Player':40}score   Type")
  for player, points in playerPoints:
      print(f"{player.getName():40}{points:5}   {player.getType()}")
