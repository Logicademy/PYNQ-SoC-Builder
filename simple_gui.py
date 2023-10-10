import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Simple GUI Example")
        self.setGeometry(100, 100, 400, 200)  # (x, y, width, height)

        self.label = QLabel("Hello, PySide2!", self)
        self.label.move(150, 80)

        self.button = QPushButton("Click Me!", self)
        self.button.move(150, 120)

        self.button.clicked.connect(self.on_button_click)

    def on_button_click(self):
        self.label.setText("Button Clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleGUI()
    window.show()
    sys.exit(app.exec_())

