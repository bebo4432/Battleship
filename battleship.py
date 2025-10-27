def clear_screen():
    print("\n" * 100)

BOARD_SIZE = 9
SHIP_SIZES = {"Carrier": 5, "Battleship": 4, "Submarine": 3, "Patrol Boat": 2}

def create_board():
    return [["~"] * BOARD_SIZE for _ in range(BOARD_SIZE)]

def get_coords(prompt):
    while True:
        coord = input(prompt).strip().upper()
        if len(coord) != 2:
            print("Invalid Coordinate. Try again.")
            continue
        col = ord(coord[0])-ord("A")
        row = int(coord[1]) - 1
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        print("Invalid Coordinate. Try again.")

def place_ship(board, name, size):
    print_board(board, True)
    print(f"Place your {name} (size {size}).") 
    while True:
        nose = get_coords(f"Enter starting coordinate for {name} (A1, B2, etc.): ")
        direction = input("Horizontal (H) or Vertical (V)?").strip().upper()
        if direction not in ("H","V"):
            print("Invalid orientation. Try Again.")
            continue
        row, col = nose
        ship = []
        for i in range(size):
            tempRow, tempCol = (row, col +i) if direction == "H" else (row+i, col)
            if not (0 <= tempRow < BOARD_SIZE and 0 <= tempCol < BOARD_SIZE):
                print("Invalid Orientation. Ship would go off the board. Try again.")
                break
            ship.append((tempRow,tempCol))
        else:
            overlap = False
            for i in range(size):
                if board[ship[i][0]][ship[i][1]] != "~":
                    print("Invalid Orientation. Ships cannot overlap. Try Again.")
                    overlap = True
                    break
            if overlap == True:
                continue
            for i in range(size):    
                if name == "Carrier":
                    board[ship[i][0]][ship[i][1]] = "C"
                elif name == "Battleship":
                    board[ship[i][0]][ship[i][1]] = "B"
                elif name == "Submarine":
                    board[ship[i][0]][ship[i][1]] = "S"
                elif name == "Patrol Boat":
                    board[ship[i][0]][ship[i][1]] = "P"
            clear_screen()
            print(f"{name} placed. \n")
            break

def print_board(board, showShips = False):
    print("    A   B   C   D   E   F   G   H   I")
    for i in range(BOARD_SIZE):
        row = [f" {i+1} "]
        for j in range(BOARD_SIZE):
            if board[i][j] != "~" and showShips == False:
                row.append(" ~  ")
            elif board[i][j] in ("CX", "BX", "SX", "PX"):
                row.append(f" {board[i][j]} ")
            else:
                row.append(f" {board[i][j]}  ")
        print("".join(row))
        

def all_ships_sunk(board):
    for row in board:
        for cell in row:
            if cell in ("S", "P", "C", "B"):
                return False
    return True

def take_turn(player, target, own, opp, health):
    print(f"{player}'s Turn")
    print("Target Grid:")
    print_board(target, True)
    print("Your Board")
    print_board(own, True)

    while True:
        row, col = get_coords("Enter coordinates to attack (A1, B2, etc.):")
        if target[row][col] in ("O", "BX", "CX", "PX", "SX"):
            print("You have already attacked here. Try again.")
            continue
        if opp[row][col] == "C":
            print("You've hit a Carrier!")
            target[row][col] = "CX"
            opp[row][col] = "CX"
            health[0] = health[0] -1
            if health[0] == 0:
                print("You've sunk the Carrier!")
        elif opp[row][col] == "B":
            print("You've hit a Battleship!")
            target[row][col] = "BX"
            opp[row][col] = "BX"
            health[1] = health[1] -1
            if health[1] == 0:
                print("You've sunk the Battleship!")
        elif opp[row][col] == "S":
            print("You've hit a Submarine!")
            target[row][col] = "SX"
            opp[row][col] = "SX"
            health[2] = health[2] -1
            if health[2] == 0:
                print("You've sunk the Submarine!")
        elif opp[row][col] == "P":
            print("You've hit a Patrol Boat!")
            target[row][col] = "PX"
            opp[row][col] = "PX"
            health[3] = health[3] -1
            if health[3] == 0:
                print("You've sunk the Patrol Boat!")
        elif opp[row][col] == "~":
            print("Miss.")
            target[row][col] = "O"
        break
    input("Press Enter to end your turn:")
    clear_screen()


def setup_player(name):
    clear_screen()
    print(f"{name}, please set up your board. Turn the computer so your opponent cannot see.")
    board = create_board()
    for ship_name, ship_size in SHIP_SIZES.items():
        place_ship(board, ship_name, ship_size)
    print(f"Thank you for setting up, {name}.")
    input("Press Enter to continue:")
    clear_screen()
    return board
    
def main():
    clear_screen()
    print("Welcome to Battleship!")
    input("Press Enter to begin setup:")

    p1 = input("Player 1, please enter your name:")
    p2 = input("Player 2, please enter your name:")
    p1_board = setup_player(p1)
    p2_board = setup_player(p2)
    p1_health = [5,4,3,2]
    p2_health = [5,4,3,2]
    # Attack tracking boards
    p1_target = create_board()
    p2_target = create_board()

    # Main game loop
    while True:
        clear_screen()
        input(f"{p1}, please turn the computer so that {p2} cannot see. Press Enter when you have done so:")
        take_turn(p1, p1_target, p1_board, p2_board, p2_health)
        if all_ships_sunk(p2_board):
            print(f"{p1} wins! All enemy ships sunk!")
            break
        clear_screen()
        input(f"{p2}, please turn the computer so that {p1} cannot see. Press Enter when you have done so:")
        take_turn(p2, p2_target, p2_board, p1_board, p1_health)
        if all_ships_sunk(p1_board):
            print(f"{p2} wins! All enemy ships sunk!")
            break

    print("Game Over!")

if __name__ == "__main__":
    main()
