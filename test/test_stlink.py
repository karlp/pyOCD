
from pyOCD.board import DiscoBoard
import logging

logging.basicConfig(level=logging.DEBUG)
board = DiscoBoard.chooseBoard()
