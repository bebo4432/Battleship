import random
class CPU:
    def __init__(self, board):
        self.board = self.setup_board()
        self.target_board = create_board()
        self.search_mode = True
        self.ship_hits = [[],[],[],[]]  # list of confirmed hits not yet sunk
        self.targets = [[],[],[],[]]  # potential targets in target mode
        self.health = [5,4,3,2] #stores opponent ships health so it knows when to clear target lists (ship sunk)
        self.spiral = spiral_in(BOARD_SIZE)
        self.spiral_idx = 0
        self.orientation = [[],[],[],[]]
    def get_next_move(self):
        for i in range(4):
            if self.targets[i]:
                while self.targets[i]:
                    row, col = self.targets[i].pop(0)
                    if self.target_board[row][col] == "~":
                        return row, col
                # and if list emptied, continue to next i

        # Search mode: checkerboard/spiral pattern --> moves through spiral list deterministicallygit 
        while self.spiral_idx < len(self.spiral):
            r, c = self.spiral[self.spiral_idx]
            self.spiral_idx += 1
            # checkerboard spiral pattern first
            if ((r + c) % 2 == 0) and self.target_board[r][c] == "~":
                return r, c

        # If all checkerboard cells exhausted, shoot anywhere unshot (fallback)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.target_board[r][c] == "~":
                    return r, c

    def process_result(self, row, col, result):
        if result == "miss":
            self.target_board[row][col] = "O"
            return

        self.target_board[row][col] = result + "X"

        ship_idx = {"C":0, "B":1, "S":2, "P":3}[result]
        self.ship_hits[ship_idx].append((row, col))
        self.health[ship_idx] -= 1

        if self.health[ship_idx] == 0:
            # Ship sunk: clear targets and hits
            self.targets[ship_idx].clear()
            self.ship_hits[ship_idx].clear()
            self.orientation[ship_idx] = None
            return

        hits = self.ship_hits[ship_idx]

        # Determine orientation if we have at least 2 hits
        if len(hits) >= 2 and not self.orientation[ship_idx]:
            r1, c1 = hits[0]
            r2, c2 = hits[1]
            self.orientation[ship_idx] = "H" if r1 == r2 else "V"

        # Generate new targets
        new_targets = []
        if self.orientation[ship_idx] == "H":
            row = hits[0][0]
            min_c = min(c for _, c in hits) - 1
            max_c = max(c for _, c in hits) + 1
            if 0 <= min_c < BOARD_SIZE and self.target_board[row][min_c] == "~":
                new_targets.append((row, min_c))
            if 0 <= max_c < BOARD_SIZE and self.target_board[row][max_c] == "~":
                new_targets.append((row, max_c))
        elif self.orientation[ship_idx] == "V":
            col = hits[0][1]
            min_r = min(r for r, _ in hits) - 1
            max_r = max(r for r, _ in hits) + 1
            if 0 <= min_r < BOARD_SIZE and self.target_board[min_r][col] == "~":
                new_targets.append((min_r, col))
            if 0 <= max_r < BOARD_SIZE and self.target_board[max_r][col] == "~":
                new_targets.append((max_r, col))
        else:
            # Not enough hits yet, add all adjacent squares
            hr, hc = self.ship_hits[ship_idx][-1]      # last known hit
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                r, c = hr + dr, hc + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.target_board[r][c] == "~":
                        new_targets.append((r, c))

        # Merge new targets with existing ones (avoid duplicates)
        for t in new_targets:
            if t not in self.targets[ship_idx]:
                self.targets[ship_idx].insert(0, t)   # prioritize newest
    
    def setup_board(self):
        board = create_board()
        for ship_name, ship_size in SHIP_SIZES.items():
            while True:
                row = random.randint(0, BOARD_SIZE-1)
                col = random.randint(0, BOARD_SIZE-1)
                direction = random.choice(["H", "V"])
                ship = []
                for i in range(ship_size):
                    r, c = (row, col+i) if direction=="H" else (row+i, col)
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    ship.append((r, c))
                else:
                    if any(board[r][c] != "~" for r,c in ship):
                        continue
                    symbol = {"Carrier":"C", "Battleship":"B", "Submarine":"S", "Patrol Boat":"P"}[ship_name]
                    for r, c in ship:
                        board[r][c] = symbol
                    break
        return board


class RandomCPU:
    """CPU that fires fully at random (no targeting strategy)."""
    def __init__(self):
        self.target_board = create_board()

    def get_next_move(self):
        candidates = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                      if self.target_board[r][c] == "~"]
        return random.choice(candidates)

    def process_result(self, row, col, result):
        if result == "miss":
            self.target_board[row][col] = "O"
        else:
            # result will be a ship symbol like 'C','B','S','P'
            self.target_board[row][col] = result + "X"
        
        
def clear_screen():
    print("\n" * 100)

BOARD_SIZE = 9
SHIP_SIZES = {"Carrier": 5, "Battleship": 4, "Submarine": 3, "Patrol Boat": 2}

def spiral_in(board_size):
    coords = []
    for layer in range((board_size + 1) // 2):
        for c in range(layer, board_size - layer):  # top row
            coords.append((layer, c))
        for r in range(layer + 1, board_size - layer):  # right column
            coords.append((r, board_size - layer - 1))
        for c in range(board_size - layer - 2, layer - 1, -1):  # bottom row
            coords.append((board_size - layer - 1, c))
        for r in range(board_size - layer - 2, layer, -1):  # left column
            coords.append((r, layer))
    return coords

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

def take_turn(player, target, own, opp, health, cpu=None):
    print(f"{player}'s Turn")
    # If cpu is None, this is a human player's turn: show their target grid and own board.
    if cpu is None:
        print("Target Grid:")
        print_board(target, True)
        print("Your Board")
        print_board(own, True)
    else:
        # CPU is taking the turn. Don't reveal the CPU's board.
        print("Computer is taking its turn...")
    

    while True:
        if cpu:
            row, col = cpu.get_next_move()
            print(f"CPU attacks {chr(col+65)}{row+1}")
        else:
            row, col = get_coords("Enter coordinates to attack (A1, B2, etc.):")
        # Determine the actual content on the opponent's board (ship symbol or empty)
        cell = opp[row][col]
        result = "miss" if cell == "~" else cell
    
        if target[row][col] in ("O", "BX", "CX", "PX", "SX"):
            if not cpu:
                print("You have already attacked here. Try again.")
            continue

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
        if cpu:
            cpu.process_result(row, col, result)
        break
    if cpu:
        input("Press Enter to end the turn:")
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
    
    mode = input("Single Player or Two Player? (1/2): ").strip()

    p1 = input("Player 1, please enter your name:")
    p1_board = setup_player(p1)
    p1_health = [5,4,3,2]
    # Attack tracking board
    p1_target = create_board()


    if (mode == "2"):
        p2 = input("Player 2, please enter your name:")
        p2_board = setup_player(p2)
        p2_health = [5,4,3,2]
        # Attack tracking board
        p2_target = create_board()
        cpu = None
    else:
        p2 = "Computer"
        cpu = CPU(p1_board)
        p2_board = cpu.board
        p2_health = [5,4,3,2]
        
        p2_target = cpu.target_board 

    # Main game loop
    while True:
        # Player 1 turn
        clear_screen()
        if mode == "2":
            input(f"{p1}, turn the computer so {p2} cannot see. Press Enter when ready: ")
 
        take_turn(p1, p1_target, p1_board, p2_board, p2_health, cpu=None)
        if all_ships_sunk(p2_board):
            print(f"{p1} wins! All enemy ships sunk!")
            break

        # Player 2 or CPU turn
        if mode == "2":
            clear_screen()
            input(f"{p2}, turn the computer so {p1} cannot see. Press Enter when ready: ")
            take_turn(p2, p2_target, p2_board, p1_board, p1_health)
        else:
            take_turn(p2, p2_target, p2_board, p1_board, p1_health, cpu=cpu)

        if all_ships_sunk(p1_board):
            print(f"{p2} wins! All enemy ships sunk!")
            break

    print("Game Over!")

if __name__ == "__main__":
    main()
