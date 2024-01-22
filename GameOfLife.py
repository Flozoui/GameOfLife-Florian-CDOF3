import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QMainWindow, QAction
from PyQt5.QtCore import QTimer
import numpy as np
from scipy import signal


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)

        self.game = GameOfLife()
        menubar.addAction(self.game.clear_action)
        menubar.addAction(self.game.start_action)
        menubar.addAction(self.game.stop_action)            

        self.setCentralWidget(self.game)

        self.show()


class GameOfLife(QWidget):
    def __init__(self):
        super().__init__()

        self.cell_size = 10
        self.grid_width = 80
        self.grid_height = 80
        self.old_grid = np.zeros((self.grid_width, self.grid_height))
        self.grid = np.random.choice([0, 1], size=(self.grid_width, self.grid_height), p=[0.9, 0.1])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_grid)

        self.clear_action = QAction('Clear', self)
        self.clear_action.triggered.connect(self.clear_game)

        self.start_action = QAction('Start', self)
        self.start_action.triggered.connect(self.start_game)

        self.stop_action = QAction('Stop', self)
        self.stop_action.triggered.connect(self.stop_game)

        self.grid_layout = QGridLayout(self)

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                button = QPushButton('', self)
                button.setFixedSize(self.cell_size, self.cell_size)
                button.clicked.connect(lambda _, x=x, y=y: self.toggle_cell(x, y))
                self.grid_layout.addWidget(button, x, y)

        self.grid_layout.setSpacing(0)

        self.setWindowTitle('Game of Life')
        self.show()
        self.update_ui()

    def set_game(self, arr):
        self.old_grid = -np.ones((self.grid_width, self.grid_height))
        self.grid = np.copy(arr)

    def clear_game(self):
        self.stop_game()
        self.grid = np.zeros((self.grid_width, self.grid_height))
        self.update_ui()

    def start_game(self):
        self.timer.start(100)  # Update every 100 milliseconds

    def stop_game(self):
        self.timer.stop()

    def update_grid(self):
        self.old_grid = np.copy(self.grid)
        neighbors = signal.convolve2d(self.grid, np.array([[1,1,1], [1,0,1], [1,1,1]]), mode='same', boundary='fill', fillvalue=0)
        self.grid = ((neighbors==3) | ((self.grid==1) & (neighbors==2)))*1
        self.update_ui()

    def toggle_cell(self, x, y):
        self.grid[x, y] = 1 - self.grid[x, y]
        self.old_grid[x, y] = self.grid[x, y]
        self.update_ui_cell(x, y)

    def update_ui(self):
        onchangegrid = self.old_grid != self.grid
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if(onchangegrid[x, y]):
                    self.update_ui_cell(x, y)

    def update_ui_cell(self, x, y):
        button_index = x * self.grid_height + y
        button = self.grid_layout.itemAt(button_index).widget()
        if self.grid[x, y] == 1:
            button.setStyleSheet('background-color: black;')
        else:
            button.setStyleSheet('background-color: white;')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = MainWindow()
    sys.exit(app.exec_())
