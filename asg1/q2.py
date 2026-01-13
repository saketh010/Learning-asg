class TicTacToe:
    def __init__(self):
        self.board = [str(i) for i in range(1, 10)]
        self.current_player = "X"

    def print_board(self):
        print()
        for i in range(3):
            print(" | ".join(self.board[i*3:(i+1)*3]))
            if i < 2:
                print("--+---+--")
        print()

    def make_move(self, position):
        if self.board[position] not in ["X", "O"]:
            self.board[position] = self.current_player
            return True
        else:
            print("Cell already taken, try again.")
            return False

    def check_winner(self):
        b = self.board
        p = self.current_player
        wins = [
            [0,1,2], [3,4,5], [6,7,8],
            [0,3,6], [1,4,7], [2,5,8],
            [0,4,8], [2,4,6]
        ]
        for combo in wins:
            win = True
            for i in combo:
                if b[i] != p:
                    win = False
                    break
            if win:
                return True
        return False

    def is_draw(self):
        for cell in self.board:
            if cell not in ["X", "O"]:
                return False
        return True


    def switch_player(self):
        if self.current_player == "X":
            self.current_player = "O"
        else:
            self.current_player = "X"


    def play(self):
        print("Welcome to Tic-Tac-Toe!")
        print("Enter a number 1-9 to place your mark as shown below:")
        self.print_board()

        while True:
            try:
                move=int(input(f"Player {self.current_player},enter your move(1-9):"))
                if move < 1 or move > 9:
                    print("Invalid number! Enter 1-9.")
                    continue
                if not self.make_move(move - 1):
                    continue
            except ValueError:
                print("Invalid input! Enter a number from 1 to 9.")
                continue

            self.print_board()

            if self.check_winner():
                print(f"Player {self.current_player} won")
                break

            if self.is_draw():
                print("It's a draw")
                break

            self.switch_player()

if __name__=="__main__":
    game=TicTacToe()
    game.play()
