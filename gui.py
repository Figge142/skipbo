import tkinter as tk
import gameEngine

# TODO Display the game state in the window and not only console
# TODO disable unusable buttons with self.button['state'] = tk.DISABLED
class Human(gameEngine.Player):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.root = tk.Frame()
    self.createWindow()

  def getMove(self, gameState, playerIndex, gameStateHistory = None, moveHistory = None):
    # Print current state
    print("Game state:")
    print("Building piles:", gameState["buildingPiles"])
    # print()
    print("Stock pile:        %d    (there are %d cards left)" % (gameState["playerStockPilesTopCard"][playerIndex], gameState["playerStockPilesN"][playerIndex]))
    print("Hand:      ", gameState["playerHands"][playerIndex])
    print("Discard piles:")
    [print(f"Index {di}: ", gameState["playerDiscardPiles"][playerIndex][di]) for di in range(4)]

    self.root.update()
    self.root.wait_variable(self.humanMove)
    moveString = self.humanMove.get()
    return gameEngine.Move(moveString[0], int(moveString[1]), moveString[2], int(moveString[3]))

  def createWindow(self):
    self.humanMove = tk.StringVar()

    # Frame for displaying build piles
    bFrame = tk.Frame(self.root)
    for i in range(4):
      label = tk.Label(bFrame, text = str(i), relief = tk.RAISED, width = 4, height = 3)
      label.grid(row = 0, column = i)
    bFrame.grid(row = 0, column = 0)

    # Frame for displaying stock pile
    sFrame = tk.Frame(self.root)
    # First row: 4 buttons representing plays
    sPlayButtonsFrame = tk.Frame(sFrame)
    for bIndex in range(4):
      button = PlayCardButton(sPlayButtonsFrame, move = gameEngine.Move("S", 0, "B", bIndex), text = str(bIndex), humanMove = self.humanMove, relief = tk.RAISED, width = 4, height = 3)
      button.grid(row = 0, column = bIndex)
    sPlayButtonsFrame.grid(row = 0, column = 0)
    # Second row: Stock pile card value
    label = tk.Label(sFrame, text = "S", relief = tk.RAISED, width = 4, height = 3)
    label.grid(row = 1, column = 0)
    sFrame.grid(row = 1, column = 0, pady = 20)

    # Frame for displaying hand
    hFrame = tk.Frame(self.root)
    for hIndex in range(5):
      hSingleCardFrame = tk.Frame(hFrame)
      # First row: 4 buttons for build plays
      hPlayBuildButtonsFrame = tk.Frame(hSingleCardFrame)
      for bIndex in range(4):
        button = PlayCardButton(hPlayBuildButtonsFrame, move = gameEngine.Move("H", hIndex, "B", bIndex), humanMove = self.humanMove, text = str(bIndex), relief = tk.RAISED, width = 4, height = 3)
        button.grid(row = 0, column = bIndex)
      hPlayBuildButtonsFrame.grid(row = 0, column = 0)
      # Second row: Hand card value
      label = tk.Label(hSingleCardFrame, text = "H%d" % hIndex, relief = tk.RAISED, width = 4, height = 3)
      label.grid(row = 1, column = 0)
      # Third row: 4 buttons for discard plays
      hPlayDiscardButtonsFrame = tk.Frame(hSingleCardFrame)
      for dIndex in range(4):
        button = PlayCardButton(hPlayDiscardButtonsFrame, move = gameEngine.Move("H", hIndex, "D", dIndex), humanMove = self.humanMove, text = str(dIndex), relief = tk.RAISED, width = 4, height = 3)
        button.grid(row = 0, column = dIndex)
      hPlayDiscardButtonsFrame.grid(row = 2, column = 0)

      # Place the card frame
      hSingleCardFrame.grid(row = 0, column = hIndex, padx = 20)
    # Place hand frame
    hFrame.grid(row = 2, column = 0, pady = 20)

    # Frame for displaying discard piles
    dFrame = tk.Frame(self.root)
    for dIndex in range(4):
      dSinglePileFrame = tk.Frame(dFrame)
      # First row: 4 buttons for build plays
      dPlayButtonsFrame = tk.Frame(dSinglePileFrame)
      for bIndex in range(4):
        button = PlayCardButton(dPlayButtonsFrame, move = gameEngine.Move("D", dIndex, "B", bIndex), humanMove = self.humanMove, text = str(bIndex), relief = tk.RAISED, width = 4, height = 3)
        button.grid(row = 0, column = bIndex)
      dPlayButtonsFrame.grid(row = 0, column = 0)
      # Second row: Hand card value
      label = tk.Label(dSinglePileFrame, text = "D%d" % dIndex, relief = tk.RAISED, width = 4, height = 3)
      label.grid(row = 1, column = 0)

      # Place the discard frame
      dSinglePileFrame.grid(row = 0, column = dIndex, padx = 20)
    # Place discard frame
    dFrame.grid(row = 3, column = 0, pady = 20)


    self.root.pack()

class PlayCardButton(tk.Button):
  def __init__(self, master, move, humanMove, *args, **kwargs):
    super().__init__(master, command = self.buttonPressed, *args, **kwargs)
    self.move = move
    self.humanMove = humanMove

  def buttonPressed(self):
    print("Pressed button for move %s" % self.move.toString())
    self.humanMove.set(self.move.toString())


if __name__ == "__main__":
  players = [gameEngine.BareMinimumBot("Bot %d" % (i+1)) for i in range(1)]
  players.append(Human("Human"))

  g = gameEngine.Game(players = players, stockPileSize = 4)
  pointList = g.play()

  playerPoints = zip(players, pointList)
  playerPoints = sorted(playerPoints, key=lambda x: -x[1])
  print(f"{'Player':45}score   type")
  for player, points in playerPoints:
      print(f"{player.getName():45}{points:5}   {player.getType()}")
