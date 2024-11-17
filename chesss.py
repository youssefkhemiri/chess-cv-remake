import chess
import chess.engine

class StockfishBestMove:
    def __init__(self, stockfish_path, skill_level=10):
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.engine.configure({"Skill Level": skill_level})  # Set Stockfish skill level

    def get_best_move(self, fen, time_limit=1.0):
        """
        Get the best move for a given FEN string.
        
        :param fen: The FEN string representing the board position.
        :param time_limit: Time limit for Stockfish to think (in seconds).
        :return: Best move in UCI format.
        """
        board = chess.Board(fen)
        result = self.engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move

    def close_engine(self):
        """Close the Stockfish engine."""
        self.engine.quit()

# Example usage
if __name__ == "__main__":
    # Set the path to your Stockfish executable
    stockfish_path = r"C:\Users\Razer\Documents\ChessProject\stockfish\stockfish-windows-x86-64-avx2.exe"
    stockfish = StockfishBestMove(stockfish_path, skill_level=10)

    # Example FEN string
    fen = "rnbqkb1r/pppppppp/8/6N1/8/8/PPPPPPPP/RNBQKB1R b KQkq - 0 1"  # Sample position
    fen = "2R5/8/8/2k2P2/4K3/3r1N2/8/8 w KQkq - 0 1"
    best_move = stockfish.get_best_move(fen)
    print(f"Best move for the given position: {best_move}")

    stockfish.close_engine()
