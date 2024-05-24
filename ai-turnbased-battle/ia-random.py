import sys
import math
import random

GRID_SIZE = 5

def get_direction(player_pos, opponent_pos):
    dx = opponent_pos[0] - player_pos[0]
    dy = opponent_pos[1] - player_pos[1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return (0, 0)
    return (dx/distance, dy/distance)

def evaluate_state(state, player_index, depth=0, alpha=-float('inf'), beta=float('inf')):
   

    # Check for terminal state (game over)
    if any(life <= 0 for life in state["lifes"]):
        winner = state["lifes"].index(max(state["lifes"]))
        return (100 if winner == player_index else -100, None)

    # Base case: Reached maximum depth
    if depth == MAX_DEPTH:
        return heuristic_score(state, player_index)

    # Initialize variables
    best_action = None
    best_score = -float('inf') if player_index else float('inf')

    # Generate possible actions
    actions = ["up", "down", "left", "right", "attack", "block"]

    # Simulate each action and evaluate the resulting state
    for action in actions:
        simulated_state = simulate_action(state.copy(), player_index, action)
        score, _, _ = evaluate_state(simulated_state, 1 - player_index, depth + 1, alpha, beta)

        # Update best action and score based on player's objective
        if player_index == 0:
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)
        else:
            if score < best_score:
                best_score = score
                best_action = action
            beta = min(beta, score)

        # Prune branches if possible
        if alpha >= beta:
            break

    # Return the best action and score (optionally with simulated state)
    return best_score, best_action, simulated_state

def heuristic_score(state, player_index):
    

    # Prioritize own life, then opponent's life, then bullets, and then distance to opponent
    score = state["lifes"][player_index] - state["lifes"][1 - player_index]
    score += 2 * state["bullets"][player_index]

    player_pos = (
        state["pos_" + str(player_index + 1)] % state["GRID_SIZE"],
        state["pos_" + str(player_index + 1)] // state["GRID_SIZE"],
    )
    opponent_pos = (
        state["pos_" + str(3 - player_index)] % state["GRID_SIZE"],
        state["pos_" + str(3 - player_index)] // state["GRID_SIZE"],
    )
    score -= abs(player_pos[0] - opponent_pos[0]) + abs(player_pos[1] - opponent_pos[1])

    return score


def generate_successors(state, player):
    successors = []
    commands = ["up", "down", "left", "right", "attack", "block", "pickup"]
    opponent_commands = commands.copy()  # Considera as respostas do oponente
    
    # Verifica se o jogador tem balas para atacar
    if state['bullets'][player - 1] == 0:
        commands.remove("attack")
    
    for command in commands:
        for opponent_command in opponent_commands:
            new_state = state.copy()
            player_pos = new_state['positions'][player - 1]
            opponent_pos = new_state['positions'][2 - player]

            # Atualiza o novo estado com base no comando do jogador
            if command == "up":
                new_pos = (player_pos[0], player_pos[1] - 1)
                if new_pos[1] >= 0:
                    new_state['positions'][player - 1] = new_pos
            elif command == "down":
                new_pos = (player_pos[0], player_pos[1] + 1)
                if new_pos[1] < GRID_SIZE:
                    new_state['positions'][player - 1] = new_pos
            elif command == "left":
                new_pos = (player_pos[0] - 1, player_pos[1])
                if new_pos[0] >= 0:
                    new_state['positions'][player - 1] = new_pos
            elif command == "right":
                new_pos = (player_pos[0] + 1, player_pos[1])
                if new_pos[0] < GRID_SIZE:
                    new_state['positions'][player - 1] = new_pos
            elif command == "attack":
                if abs(player_pos[0] - opponent_pos[0]) <= 1 and abs(player_pos[1] - opponent_pos[1]) <= 1:
                    new_state['bullets'][player - 1] -= 1
                    new_state['lifes'][2 - player] -= 1
            elif command == "block":
                pass  # Não faz nada por enquanto
            elif command == "pickup":
                # Verifica se há um item no estado
                if 'item' in new_state:
                    item_pos = new_state['item']['position']
                    # Verifica se o jogador está na mesma posição que o item
                    if player_pos == item_pos:
                        # Verifica o tipo do item e atualiza o estado do jogador
                        if new_state['item']['type'] == 'ammo':
                            new_state['bullets'][player - 1] += 1
                        elif new_state['item']['type'] == 'life':
                            new_state['lifes'][player - 1] += 1
                        # Remove o item do estado
                        new_state.pop('item')
            
            # Atualiza o novo estado com base na resposta do oponente (simétrica para o oponente)
            opponent_pos = new_state['positions'][2 - player]
            if opponent_command == "up":
                new_pos = (opponent_pos[0], opponent_pos[1] - 1)
                if new_pos[1] >= 0:
                    new_state['positions'][2 - player] = new_pos
            elif opponent_command == "down":
                new_pos = (opponent_pos[0], opponent_pos[1] + 1)
                if new_pos[1] < GRID_SIZE:
                    new_state['positions'][2 - player] = new_pos
            elif opponent_command == "left":
                new_pos = (opponent_pos[0] - 1, opponent_pos[1])
                if new_pos[0] >= 0:
                    new_state['positions'][2 - player] = new_pos
            elif opponent_command == "right":
                new_pos = (opponent_pos[0] + 1, opponent_pos[1])
                if new_pos[0] < GRID_SIZE:
                    new_state['positions'][2 - player] = new_pos
            elif opponent_command == "attack":
                if abs(opponent_pos[0] - player_pos[0]) <= 1 and abs(opponent_pos[1] - player_pos[1]) <= 1:
                    new_state['bullets'][2 - player] -= 1
                    new_state['lifes'][player - 1] -= 1
            elif opponent_command == "block":
                pass  # Não faz nada por enquanto
            elif opponent_command == "pickup":
                # Verifica se há um item no estado
                if 'item' in new_state:
                    item_pos = new_state['item']['position']
                    # Verifica se o oponente está na mesma posição que o item
                    if opponent_pos == item_pos:
                        # Verifica o tipo do item e atualiza o estado do oponente
                        if new_state['item']['type'] == 'ammo':
                            new_state['bullets'][2 - player] += 1
                        elif new_state['item']['type'] == 'life':
                            new_state['lifes'][2 - player] += 1
                        # Remove o item do estado
                        new_state.pop('item')
            
            successors.append((command, new_state))
    
    # Ordena os sucessores com base em uma heurística de avaliação
    successors.sort(key=lambda x: evaluate_state(x[1]), reverse=True)
    
    return successors
    
    # Ordena os sucessores com base em uma heurística de avaliação
    successors.sort(key=lambda x: evaluate_state(x[1]), reverse=True)
    
    return successors
# Função Minimax com poda alfa-beta e profundidade de busca variável
def minimax(state, depth, player, alpha, beta):
    def game_over(state):
        return state['lifes'][0] <= 0 or state['lifes'][1] <= 0

    if depth == 0 or game_over(state):
        return evaluate_state(state), None
    if player == 1:
        value = -sys.maxsize
        best_actions = []
        for action, new_state in generate_successors(state, player):
            new_depth = depth - 1
            if new_state['lifes'][0] <= 3 or new_state['lifes'][1] <= 3:
                new_depth += 1
            new_value, _ = minimax(new_state, new_depth, 2, alpha, beta)
            if new_value > value:
                value = new_value
                best_actions = [action]
            elif new_value == value:
                best_actions.append(action)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, random.choice(best_actions)
    else:  # player == 2
        value = sys.maxsize
        best_actions = []
        for action, new_state in generate_successors(state, player):
            new_depth = depth - 1
            if new_state['lifes'][0] <= 3 or new_state['lifes'][1] <= 3:
                new_depth += 1
            new_value, _ = minimax(new_state, new_depth, 1, alpha, beta)
            if new_value < value:
                value = new_value
                best_actions = [action]
            elif new_value == value:
                best_actions.append(action)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, random.choice(best_actions)

# Função para retornar a ação
def return_action(action):
    print(action)

# Obtém o estado a partir dos argumentos da linha de comando
def get_state_from_args(args):
    state_str = args[1]  # Supõe que o estado do jogo é o segundo argumento
    state_list = state_str.split(',')
    state = {
        'lifes': [int(state_list[0]), int(state_list[1])],
        'bullets': [int(state_list[2]), int(state_list[3])],
        'positions': [(int(state_list[4]), int(state_list[5])), (int(state_list[6]), int(state_list[7]))],
        'items': [{'type': state_list[8], 'position': (int(state_list[9]), int(state_list[10]))}],
        'board': [int(x) for x in state_list[11:]]
    }
    return state


# Obtém o estado a partir dos argumentos da linha de comando
state = get_state_from_args(sys.argv)

# Executa o algoritmo Minimax para obter a melhor ação
depth = 3  # Profundidade de busca inicial
_, action = minimax(state, depth, 1, -sys.maxsize, sys.maxsize)

# Retorna a ação
return_action(action) 