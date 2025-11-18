import random
import time
import argparse
from copy import deepcopy
import battleship

HIT_MARKS = {"O", "CX", "BX", "SX", "PX"}

def clone(board):
    """Shortcut for deepcopy, used when copying boards."""
    return deepcopy(board)

def progress(i, total, label):
    """Print 10 progress updates per experiment."""
    if (i + 1) % (total // 10 or 1) == 0:
        print(f"[{label}] Completed {i+1}/{total}")

def mark_attack(board, r, c):
    """Apply hit/miss to the board and return result string."""
    cell = board[r][c]
    hit = cell != "~"
    result = cell if hit else "miss"
    board[r][c] = f"{cell}X" if hit else "O"
    return result

def simulate_clear(attacker, opponent_board):
    """
    Simulate attacker firing until all opponent ships are sunk.
    Returns number of moves used.
    """
    board = clone(opponent_board)
    moves = 0
    max_moves = battleship.BOARD_SIZE ** 2 * 2

    while not battleship.all_ships_sunk(board) and moves < max_moves:
        r, c = attacker.get_next_move()

        # Skip repeated attacks (should not happen normally)
        if board[r][c] in HIT_MARKS:
            #moves += 1         dont increment moves for repeated attacks, just skip
            continue

        result = mark_attack(board, r, c)
        attacker.process_result(r, c, result)
        moves += 1
    return moves

def experiment_trained_vs_boards(trials=1000, show_progress=True):
    """Simulate games between a trained CPU and various board setups."""
    total_moves = 0
    t0 = time.time()

    for i in range(trials):
        opponent = battleship.CPU(None).board
        attacker = battleship.CPU(None)
        attacker.target_board = battleship.create_board()

        moves = simulate_clear(attacker, clone(opponent))
        total_moves += moves
        if show_progress:
            progress(i, trials, "Trained")
    return total_moves / trials, time.time() - t0

def experiment_random_vs_boards(trials=1000, show_progress=True):
    """Simulate games between a random CPU and various board setups."""
    total_moves = 0
    t0 = time.time()

    for i in range(trials):
        opponent = battleship.CPU(None).board
        attacker = battleship.RandomCPU()

        moves = simulate_clear(attacker, clone(opponent))
        total_moves += moves
        if show_progress:
            progress(i, trials, "Random")
    return total_moves / trials, time.time() - t0

def resolve_attack(attacker, board):
    """One attack step; True if defender is fully sunk."""
    r, c = attacker.get_next_move()
    result = mark_attack(board, r, c)
    attacker.process_result(r, c, result)
    return battleship.all_ships_sunk(board)

def experiment_head_to_head(games=100, show_progress=True):
    """ Simulate games between a trained CPU and a random CPU."""
    trained_wins = random_wins = ties = 0
    t0 = time.time()

    N = battleship.BOARD_SIZE
    max_turns = N * N * 4

    for i in range(games):
        # Two independent random boards
        board_A = battleship.CPU(None).board
        board_B = battleship.CPU(None).board

        trained = battleship.CPU(None)
        trained.board = clone(board_A)
        trained.target_board = battleship.create_board()

        rnd = battleship.RandomCPU()
        rnd.board = clone(board_B)
        rnd.target_board = battleship.create_board()

        # Define turn order
        pairs_even = ((trained, rnd.board), (rnd, trained.board))
        pairs_odd  = ((rnd, trained.board), (trained, rnd.board))
        order = pairs_even if i % 2 == 0 else pairs_odd

        turns = 0
        while turns < max_turns:
            for attacker, defender_board in order:
                if resolve_attack(attacker, defender_board):
                    if attacker is trained:
                        trained_wins += 1
                    else:
                        random_wins += 1
                    break
            else:
                turns += 1
                continue  # no winner yet
            break  # winner found

        if turns >= max_turns:
            ties += 1

        if show_progress:
            progress(i, games, "H2H")
    return trained_wins, random_wins, ties, time.time() - t0

def main():
    parser = argparse.ArgumentParser(description="Run CPU efficiency experiments for Battleship")
    parser.add_argument("--trained-trials", type=int, default=1000,
                        help="Boards for trained CPU")
    parser.add_argument("--random-trials", type=int, default=1000,
                        help="Boards for random CPU")
    parser.add_argument("--games", type=int, default=100,
                        help="Head-to-head games")
    args = parser.parse_args()

    # Random seed
    seed = random.randrange(2**32)
    random.seed(seed)
    print(f"Using RNG seed: {seed}")
    print("Running CPU efficiency experiments…")

    avg_trained, time_trained = experiment_trained_vs_boards(args.trained_trials)

    avg_random, time_random = experiment_random_vs_boards(args.random_trials)

    trained_wins, random_wins, ties, time_h2h = experiment_head_to_head(args.games)
    print(f"\nTrained CPU: avg moves = {avg_trained:.2f}, time = {time_trained:.1f}s")
    print(f"Random CPU: avg moves = {avg_random:.2f}, time = {time_random:.1f}s")
    print(f"\nHead-to-head results ({args.games} games):")
    print(f" trained wins  = {trained_wins}")
    print(f" random wins   = {random_wins}")
    print(f" ties          = {ties}")
    print(f" trained win % = {trained_wins/args.games}")
    print(f" time          = {time_h2h:.1f}s")

if __name__ == "__main__":
    main()
