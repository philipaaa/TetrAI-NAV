import sys, random
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont

from tetris_model import BOARD_DATA, Shape
from tetris_ai import TETRIS_AI

AIplaying = True

class Tetris(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isStarted = False
        self.isPaused = False
        self.isGameOver = False
        self.nextMove = None
        self.lastShape = Shape.shapeNone

        self.initUI()

    def initUI(self):
        self.gridSize = 22
        self.speed = 1000

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

        hLayout = QHBoxLayout()
        self.tboard = Board(self, self.gridSize)
        hLayout.addWidget(self.tboard)

        self.sidePanel = SidePanel(self, self.gridSize)
        hLayout.addWidget(self.sidePanel)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        #self.start()

        self.center()
        self.setWindowTitle('TetrAI Nav')
        self.show()

        self.setFixedSize(self.tboard.width() + self.sidePanel.width(),
                          self.sidePanel.height() + self.statusbar.height())
        
        # Set the background color to dark blue
        self.setStyleSheet("background-color: #00008B;")  # Hex code for dark blue

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.isGameOver = False
        self.tboard.score = 0
        BOARD_DATA.clear()

        self.tboard.msg2Statusbar.emit(str(self.tboard.score))

        BOARD_DATA.createNewPiece()
        self.timer.start(self.speed, self)

        # Reset Start button opacity on restart
        self.sidePanel.startButton.setEnabled(False)
        self.sidePanel.startButton.setStyleSheet("opacity: 0.5;")


    def pause(self):
        if not self.isStarted or self.isGameOver: 
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.tboard.msg2Statusbar.emit("Paused")
        else:
            self.timer.start(self.speed, self)

        self.updateWindow()

    def updateWindow(self):
        self.tboard.updateData()
        self.sidePanel.updateData()
        self.update()

    def calculateDropPosition(self, shape, direction, x):
        y = 0
        while BOARD_DATA.tryMove(shape, direction, x, y + 1):
            y += 1
        return y

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.isGameOver:
                self.timer.stop()
                return

            if not self.nextMove:
                self.nextMove = TETRIS_AI.nextMove()
                BOARD_DATA.highlightShape = BOARD_DATA.currentShape
                BOARD_DATA.highlightDirection = self.nextMove[0]
                BOARD_DATA.highlightX = self.nextMove[1]
                BOARD_DATA.highlightY = self.calculateDropPosition(BOARD_DATA.highlightShape, 
                                                     BOARD_DATA.highlightDirection, 
                                                     BOARD_DATA.highlightX)
                
                self.nextMove = TETRIS_AI.nextWorstMove()
                BOARD_DATA.worstHighlightShape = BOARD_DATA.currentShape
                BOARD_DATA.worstHighlightDirection = self.nextMove[0]
                BOARD_DATA.worstHighlightX = self.nextMove[1]
                BOARD_DATA.worstHighlightY = self.calculateDropPosition(BOARD_DATA.worstHighlightShape, 
                                                     BOARD_DATA.worstHighlightDirection, 
                                                     BOARD_DATA.worstHighlightX)
                
                self.nextMove = TETRIS_AI.nextMove()

            if self.nextMove and AIplaying:
                k = 0
                while BOARD_DATA.currentDirection != self.nextMove[0] and k < 4:
                    BOARD_DATA.rotateRight()
                    k += 1
                k = 0
                while BOARD_DATA.currentX != self.nextMove[1] and k < 5:
                    if BOARD_DATA.currentX > self.nextMove[1]:
                        BOARD_DATA.moveLeft()
                    elif BOARD_DATA.currentX < self.nextMove[1]:
                        BOARD_DATA.moveRight()
                    k += 1
            lines = BOARD_DATA.moveDown()
            self.tboard.score += lines

            if BOARD_DATA.gameOver():
                self.gameOver()
                return

            if self.lastShape != BOARD_DATA.currentShape:
                self.nextMove = None
                self.lastShape = BOARD_DATA.currentShape
            self.updateWindow()
        else:
            super(Tetris, self).timerEvent(event)

    def keyPressEvent(self, event):
        if self.isGameOver:
            if event.key() == Qt.Key_R:
                self.restartGame()
            return

        if not self.isStarted or BOARD_DATA.currentShape == Shape.shapeNone:
            super(Tetris, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return
        elif key == Qt.Key_Left:
            BOARD_DATA.moveLeft()
        elif key == Qt.Key_Right:
            BOARD_DATA.moveRight()
        elif key == Qt.Key_Up:
            BOARD_DATA.rotateLeft()
        elif key == Qt.Key_Space:
            self.tboard.score += BOARD_DATA.dropDown()
        elif key == Qt.Key_R:
            self.restartGame()
        else:
            super(Tetris, self).keyPressEvent(event)

        self.updateWindow()

    def gameOver(self):
        self.isGameOver = True
        self.timer.stop()
        self.tboard.msg2Statusbar.emit("Game Over! Press R to Restart.")
        self.updateWindow()

    def restartGame(self):
        self.isPaused = False
        self.isGameOver = False
        self.tboard.score = 0
        BOARD_DATA.clear()
        BOARD_DATA.createNewPiece()
        self.timer.start(self.speed, self)
        self.updateWindow()


class SidePanel(QFrame):
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * BOARD_DATA.height)
        self.move(gridSize * BOARD_DATA.width, 0)
        self.gridSize = gridSize

        # Add buttons to the side panel
        self.initButtons()

    def paintEvent(self, event):
        painter = QPainter(self)
        minX, maxX, minY, maxY = BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 3 * self.gridSize
        dx = int((self.width() - (maxX - minX) * self.gridSize) / 2)

        val = BOARD_DATA.nextShape.shape
        for x, y in BOARD_DATA.nextShape.getCoords(0, 0, -minY):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize, "NA")
    
    def initButtons(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Reduce spacing between buttons
        layout.setContentsMargins(10, 300, 10, 10)  # Adjust margin to lower buttons

        # Start Button
        self.startButton = QPushButton("Start")
        self.startButton.setEnabled(False)  # Disabled by default
        self.startButton.clicked.connect(self.parent().start)
        self.startButton.setStyleSheet("""
            QPushButton {
                background-color: magenta;
                color: white;
                border: 1px solid black;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #ffccff;  /* Light magenta for disabled state */
                color: gray;
            }
        """)
        layout.addWidget(self.startButton)

        # AI Play Button
        self.aiTrueButton = QPushButton("AI On")
        self.aiTrueButton.clicked.connect(lambda: self.toggleButtonState(self.aiTrueButton, True))  # Enable Start on click
        self.aiTrueButton.clicked.connect(self.setAIPlayingTrue)
        self.aiTrueButton.setStyleSheet("""
            QPushButton {
                background-color: magenta;
                color: white;
                border: 1px solid black;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.aiTrueButton)

        # AI Pause Button
        self.aiFalseButton = QPushButton("AI Off")
        self.aiFalseButton.clicked.connect(lambda: self.toggleButtonState(self.aiFalseButton, False))  # Enable Start on click
        self.aiFalseButton.clicked.connect(self.setAIPlayingFalse)
        self.aiFalseButton.setStyleSheet("""
            QPushButton {
                background-color: magenta;
                color: white;
                border: 1px solid black;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.aiFalseButton)

        # Set translucent when Start button is clicked
        self.startButton.clicked.connect(self.makeStartButtonTranslucent)

    def toggleButtonState(self, button, isAIPlaying):
        print(f"Button {button.text()} clicked, isAIPlaying: {isAIPlaying}")  # Debug statement
        global AIplaying
        AIplaying = isAIPlaying

        # Reset all buttons
        self.aiTrueButton.setStyleSheet("opacity: 1.0;")
        self.aiFalseButton.setStyleSheet("opacity: 1.0;")

        # Set the pressed button translucent
        button.setStyleSheet("opacity: 0.5;")

        # Enable the Start button
        self.enableStartButton()


    def enableStartButton(self):
        """Enable the Start button when AI On or AI Off is clicked."""
        self.startButton.setEnabled(True)
        self.startButton.setStyleSheet("opacity: 1.0;")  # Reset opacity to normal

    def setAIPlayingTrue(self):
        global AIplaying
        AIplaying = True
        self.parent().statusbar.showMessage("AI is now playing.")

    def setAIPlayingFalse(self):
        global AIplaying
        AIplaying = False
        self.parent().statusbar.showMessage("AI has been paused.")

    def makeStartButtonTranslucent(self):
        self.startButton.setEnabled(False)
        self.startButton.setStyleSheet("opacity: 0.5;")
        
    
    def updateData(self):
        self.update()

class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)
    speed = 10

    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * BOARD_DATA.width, gridSize * BOARD_DATA.height)
        self.gridSize = gridSize
        self.initBoard()

    def initBoard(self):
        self.score = 0
        BOARD_DATA.clear()

    def gameOver(self):
        spawn_x, spawn_y = self.width // 2, self.height - 1  
        for x, y in self.getCurrentShapeCoord(spawn_x, spawn_y):
            if self.getValue(x, y) != 0: 
                return True
        return False    


    def paintEvent(self, event):
        painter = QPainter(self)

        for x in range(BOARD_DATA.width):
            for y in range(BOARD_DATA.height):
                val = BOARD_DATA.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize, "NA")

        for x, y in BOARD_DATA.getCurrentShapeCoord():
            val = BOARD_DATA.currentShape.shape
            drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize, "NA")

        for x, y in BOARD_DATA.highlightShape.getCoords(BOARD_DATA.highlightDirection, 
                                                        BOARD_DATA.highlightX, 
                                                        BOARD_DATA.highlightY):
            drawSquare(painter, x * self.gridSize, y * self.gridSize, BOARD_DATA.highlightShape.shape, 
                       self.gridSize, highlight="best")

        for x, y in BOARD_DATA.worstHighlightShape.getCoords(BOARD_DATA.worstHighlightDirection, 
                                                        BOARD_DATA.worstHighlightX, 
                                                        BOARD_DATA.worstHighlightY):
            drawSquare(painter, x * self.gridSize, y * self.gridSize, BOARD_DATA.worstHighlightShape.shape, 
                       self.gridSize, highlight="worst")

        if self.parent().isGameOver: 
            self.drawGameOverMessage(painter)

        painter.setPen(QColor(0x777777))
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())

    def drawGameOverMessage(self, painter):
        painter.setPen(QColor(255, 0, 0))
        painter.setFont(QFont('Arial', 20, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "Game Over!")

    def updateData(self):
        self.msg2Statusbar.emit(str(self.score))
        self.update()


def drawSquare(painter, x, y, val, s, highlight):
    colorTable = [0x000000, 0xFFFFFF, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

    if val == 0:
        return

    #for different colour blocks
    #color = QColor(colorTable[val])
    #Making all blocks white
    color = QColor(0xFFFFFF)
    if highlight == "best":
        color.setAlpha(80)  # Make the highlight translucent
    elif highlight == "worst":
        color = QColor(0xCC6666)
        color.setAlpha(80)  # Make the highlight translucent


    painter.fillRect(x + 1, y + 1, s - 2, s - 2, color)

    painter.setPen(color.lighter())
    painter.drawLine(x, y + s - 1, x, y)
    painter.drawLine(x, y, x + s - 1, y)

    painter.setPen(color.darker())
    painter.drawLine(x + 1, y + s - 1, x + s - 1, y + s - 1)
    painter.drawLine(x + s - 1, y + s - 1, x + s - 1, y + 1)



if __name__ == '__main__':
    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())