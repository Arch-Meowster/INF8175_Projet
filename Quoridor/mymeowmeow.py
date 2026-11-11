"""
Code produit dans le cadre du cours INF8175. 
Réalisation d'un agent pour le jeu Quoridor.

Réalisé par:
Jordan Valiquette (2280857)
Philippe Clermont (2290116)
"""


from seahorse.game.game_state import StatelessAction
import actions_quoridor
import game_state_quoridor
from player_quoridor import PlayerQuoridor
from seahorse.game.action import Action
from game_state_quoridor import GameStateQuoridor
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time
from collections import deque

#===== Heuristique =====

POIDS = {"distance": 1, "walls": 0.5, "turns": 0.5}

def evaluer(state, inverse):

    score = 0
    
    if inverse == 1:
        moi = state.players[0]
    else:
        moi = state.players[1]

    adv = state._opponent(moi)

    d_moi = state._shortest_path(moi)
    d_adv = state._shortest_path(adv)

    moi_murs = state.rep.remaining_walls[moi.id]
    adv_murs = state.rep.remaining_walls[adv.id]

    heuristique = {
        "distance": d_adv - d_moi,
        "walls": moi_murs - adv_murs,
        "turns": 1 if state.active_player == moi else -1
    }

    # S'il n'y as plus de mur, c'est juste le plus court chemin qui compte
    if moi_murs == 0 and adv_murs == 0:
        if d_moi < d_adv or (d_moi == d_adv and state.active_player == moi):
            score += 50
        else:
            score += -50

    for nom, valeur in heuristique.items():
        score += valeur * POIDS[nom]
        
    return score


def chemin_le_plus_court(state, joueur):
    debut = state.rep.pawn_positions[joueur.id]
    parent = {debut: None}
    file = deque([debut])
    while file:
        case = file.popleft()
        if case[0] == joueur.get_goal_row():
            chemin = []
            while case is not None:
                chemin.append(case)
                case = parent[case]
            return chemin[::-1]
        for voisin in state._reachable_neighbours(case):
            if voisin not in parent:
                parent[voisin] = case
                file.append(voisin)
    return None

# def shortest_path(state, player):
#     start = problem.getStartState()
#     states = [(start, [])]
#     visited = set()


#     while states:
#         position, directions = states.pop(0)

#         if problem.isGoalState(position):
#             return directions

#         else:
#             if position not in visited:
#                 visited.add(position)
#                 for successor, action, cost in problem.getSuccessors(position):
#                     if successor not in visited:
#                         states.append((successor, directions + [action]))
#     return []

"""
Only compute walls that are sticked to player or other wall + 1 space and 1 space further for less possible outcomes
"""

"""
    ***Cette boucle à été partiellement écrite par IA pour réduire l'engorgement de l'écran, la section touchée est ilustrée par des commentaires #***(), à noter 
    que des modifications ont tout de même étées apporter à ces sections.
    
    Cette section proviens d'une boucle de la V2 passant au travers des "legal wall" avec la condition que les murs touchent ou soient a distance de 1 des autres,
    faisant que le nombre ditération venaient rallonger le code donc une version écrite a la main est venue, au lieu de passer par "_legal_moves", vérifier
    les états possibles avec "_is_wall_legal". La version humaine faisant des lignes de codes trop longues et invoquait a plusieurs reprises des méthodes ".append"
    qui étaient inneficace et illisible donc l'ia s'est occupé de générer la même logique sous forme de "set".
"""

#***(
H, V = actions_quoridor.Orientation.HORIZONTAL, actions_quoridor.Orientation.VERTICAL
#***)

def gen_actions_utiles(state, player, remaining_time, time_start, strat):

    time_left = remaining_time - (time.perf_counter() - time_start)
    mouvements = tuple(state._legal_moves())
    candidats = set()
    Wall = actions_quoridor.Wall

    #***(
    if state.rep.remaining_walls[state.active_player.id] != 0 and time_left > 5 and strat == False: # S'il reste des murs et s'il reste plus de 5 secondes
        
        cible = state._opponent(state.active_player)
        chemin = chemin_le_plus_court(state, cible)
        for a, b in zip(chemin, chemin[1:]):
            for w in state._candidate_blocking_walls(a, b):
                candidats.add((w.row, w.col, w.orientation))

        for w in state.rep.walls:
            r, c = w.row, w.col
            if w.orientation == H:
                candidats.update([
                    (r, c - 2, H), (r, c + 2, H), 
                    (r, c + 2, V), (r - 2, c + 2, V), (r, c + 1, V),
                    (r - 2, c + 1, V), (r, c, V), (r - 2, c, V),
                ])
            else:
                candidats.update([
                    (r + 2, c, H), (r + 2, c - 2, H), (r + 1, c, H),
                    (r + 1, c - 2, H), (r, c, H), (r, c - 2, H),
                    (r - 2, c, V), (r + 2, c, V), 
                ])

    murs = []

    if len(candidats) != 0:
        
        for r, c, o in candidats:
            
            if o == V and (c==0 or c==9):
                continue
            if o == H and (r==0 or r==9):
                continue

            wall = Wall(r, c, o)
            if state._is_wall_legal(wall):
                murs.append(StatelessAction({
                    "type": "vertical" if o == V else "horizontal",
                    "destination": (r, c),
                }))
    #***)
    return mouvements + tuple(murs)



#Minimax avec alpha-beta churning

def minimax(state, my_player : bool, alpha, beta, depth, inverse, player, remaining_time, time_start, start):

    #Winner?

    if state._goal_reached(state.rep, state.players[0]):
        if inverse == -1:
            return (-100, None)
        else:
            return (100, None)

    elif state._goal_reached(state.rep, state.players[1]):
        if inverse == 1:
            return (-100, None)
        else:
            return (100, None)


    #Depth reached?

    elif depth == 0:
        return (evaluer(state, inverse), None)
    

    #Iterate

    elif my_player :
        maximum = -1000
        actions = gen_actions_utiles(state, player, remaining_time, time_start, start)

        for action in actions :
            impact = minimax(state.apply_action(action), False, alpha, beta, depth-1, inverse, player, remaining_time, time_start, start)[0]
            if maximum < impact:
                maximum = impact
                meilleure_action = action
            alpha = max(alpha, impact)
            if beta <= alpha:
                break
        return (maximum, meilleure_action)

    else :
        minimum = 1000
        actions = gen_actions_utiles(state, player, remaining_time, time_start, start)
        for action in actions :
            impact = minimax(state.apply_action(action), True, alpha, beta, depth-1, inverse, player, remaining_time, time_start, start)[0]
            if minimum > impact:
                minimum = impact
                meilleure_action = action
            beta = min(beta, impact)
            if beta <= alpha:
                break
        return (minimum, meilleure_action)



class MyPlayer(PlayerQuoridor):
    """
    Player class for Quoridor game

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, goal_row: int=0, name: str = "Meowster", *args, **kwargs) -> None:
        """
        Initialize the PlayerQuoridor instance.

        Args:
            piece_type (str): Type of the player's game piece
            goal_row (int): The row the player wants to reach
            name (str, optional): Name of the player (default is "bob")
        """
        # dans __init__

        super().__init__(piece_type, goal_row, name)


    def compute_action(self, current_state: GameStateQuoridor, remaining_time: float = 15*60, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameStateQuoridor): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """
        
        """
        Quantifier la valeur d'un pas comme 1/(dist_restante+nbr_de_mur_adv) et valeur d'un placement de mur minimax rallongement adversaire en calc la valeurde ces pas, donc
        """
        start_time = time.perf_counter()

        #agencement des formules
        if current_state.active_player.id == current_state.players[1].id :
            inverse = -1
            player = current_state.players[1].id
        else : 
            inverse = 1
            player = current_state.players[0].id

        
        '''
        #Opening
        if current_state.get_step()/2 < 3:

            moves = tuple(current_state._legal_moves())
            for move in moves:
                newstate = current_state.apply_action(move)
                if newstate._shortest_path(current_state.active_player) < current_state._shortest_path(current_state.active player):
                    meilleure_action = move
            
            

        elif current_state.get_step()/2 == 3 or current_state()/2 == 3.5:
            if inverse == 1:
                if 



        #Minimax
        else:
        '''
        start = False
        if current_state.get_step()/2 < 3:
            start = True

        
        Poids = {"distance": 1, "walls": 0.5, "turns": 0.5}

        beta = 1000
        alpha = -1000


        if remaining_time>600:
            depth = 5
        elif remaining_time>150:
            depth = 4
        else:
            depth = 3

        #Minimax
        resultat = minimax(current_state, True, alpha, beta, depth, inverse, player, remaining_time, start_time, start)
        meilleure_action = resultat[1]
 

        return meilleure_action

