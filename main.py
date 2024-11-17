# This script uses the CNN architecture defined in train.py to analyze
# the given image (can be used autonomously, i.e. without explicitly running
# train.py). Given an image path or multiple image paths separated by space,
# turns it/them into a chess position/positions and outputs the FEN string.

import numpy as np
import os
from pathlib import Path
from preprocess import preprocess_image
from train import create_model
import tensorflow as tf
import io


PIECES = ['Empty', 'Rook_White', 'Rook_Black', 'Knight_White', 'Knight_Black', 'Bishop_White',
          'Bishop_Black', 'Queen_White', 'Queen_Black', 'King_White', 'King_Black', 'Pawn_White', 'Pawn_Black']
PIECES.sort()
LABELS = {
    'Empty': '.',
    'Rook_White': 'R',
    'Rook_Black': 'r',
    'Knight_White': 'N',
    'Knight_Black': 'n',
    'Bishop_White': 'B',
    'Bishop_Black': 'b',
    'Queen_White': 'Q',
    'Queen_Black': 'q',
    'King_White': 'K',
    'King_Black': 'k',
    'Pawn_White': 'P',
    'Pawn_Black': 'p',
}

def classify_image(img):
    '''Given an image of a single piece, classifies it into one of the classes
    defined in PIECES.'''
    y_prob = model.predict(img.reshape(1, 300, 150, 3))
    y_pred = y_prob.argmax()
    return PIECES[y_pred]


def analyze_board(img):
    '''Given an image of an entire board, returns an array representing 
    the predicted chess position. Note that the first row of the array
    corresponds to the 8th rank of the chess board (i.e. where all the 
    black non-pawn pieces are located initially).'''
    arr = []
    M = img.shape[0]//8
    N = img.shape[1]//8
    # for y in range(img.shape[0]-1, -1, -M):
    for y in range(M-1, img.shape[1], M):
        row = []
        for x in range(0, img.shape[1], N):
            sub_img = img[max(0, y-2*M):y, x:x+N]
            if y-2*M < 0:
                sub_img = np.concatenate(
                    (np.zeros((2*M-y, N, 3)), sub_img))
                sub_img = sub_img.astype(np.uint8)

            piece = classify_image(sub_img)
            row.append(LABELS[piece])
        arr.append(row)

    # If there is a Queen but not a King then replace it with a King since
    # the King was probably misclassified as a Queen because the two look
    # very similar.
    blackKing = False
    whiteKing = False
    whitePos = (-1, -1)
    blackPos = (-1, -1)
    for i in range(8):
        for j in range(8):
            if arr[i][j] == 'K':
                whiteKing = True
            if arr[i][j] == 'k':
                blackKing = True
            if arr[i][j] == 'Q':
                whitePos = (i, j)
            if arr[i][j] == 'q':
                blackPos = (i, j)
    if not whiteKing and whitePos[0] >= 0:
        arr[whitePos[0]][whitePos[1]] = 'K'
    if not blackKing and blackPos[0] >= 0:
        arr[blackPos[0]][blackPos[1]] = 'k'

    return arr


def board_to_fen(board):
    '''Given an array representing a board position (from analyze_board()),
    converts it to FEN representation with default additional parameters
    (white to move, can castle both ways, etc).
    Returns a string representing a FEN position.'''
    # Use StringIO to build string more efficiently than concatenating
    with io.StringIO() as s:
        for row in board:
            empty = 0
            for cell in row:
                if cell != '.':
                    if empty > 0:
                        s.write(str(empty))
                        empty = 0
                    s.write(cell)
                else:
                    empty += 1
            if empty > 0:
                s.write(str(empty))
            s.write('/')
        # Move one position back to overwrite last '/'
        s.seek(s.tell() - 1)
        # If you do not have the additional information choose what to put
        s.write(' w KQkq - 0 1')
        return s.getvalue()

import chess
import chess.engine
# import ssl
def get_best_move(fen):
    """Get the best move using Stockfish"""
    with chess.engine.SimpleEngine.popen_uci(r"C:\Users\Razer\Documents\ChessProject\stockfish\stockfish-windows-x86-64-avx2.exe") as engine:
        board = chess.Board(fen)
        print(board)
        print("--------------------------------")
        # result = engine.play(board, chess.engine.Limit(time=0.1))
        result = engine.play(board, chess.engine.Limit(depth=10))
        return result.move

if __name__ == '__main__':
    IMAGE_PATH = "./Ex3.jpg"
    
    # Create a CNN architecture and load pre-trained weights
    try:
        model = create_model()
        model.load_weights('model_weights.h5')
    except Exception as e:
        print(f"Error loading model: {e}")
        raise
        
    # Load image and convert it to array, then to FEN
    img = preprocess_image(IMAGE_PATH, save=False)
    arr = analyze_board(img)
    fen = board_to_fen(arr)
    print("FEN string:", fen)
    print('Done!')
    best_move = get_best_move(fen)
    print("Best move:", best_move)


