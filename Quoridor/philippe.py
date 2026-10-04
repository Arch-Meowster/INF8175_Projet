import actions_quoridor
import game_state_quoridor
from player_quoridor import PlayerQuoridor
from seahorse.game.action import Action
from game_state_quoridor import GameStateQuoridor
from seahorse.utils.custom_exceptions import MethodNotImplementedError


"""
Trouver la distance estimée restante a parcourir en ce moment moyenne sur nombre de murs restants, plus tard ML ou modélisation probabiliste.
"""
def dist_estimee (state: GameStateQuoridor, player):

    chemin = state._shortest_path(player)
    remaining_walls = state.rep.remaining_walls

    if player == state.players[0]:
        murs_restants_adv = remaining_walls[state.players[1].id]
    else :
        murs_restants_adv = remaining_walls[state.players[0].id]
    return chemin + murs_restants_adv
# 2.5 a revérifier par regression linéaire et ajuster avec gamestate par ML


"""
Only compute walls that are sticked to player or other wall + 1 space and 1 space further for less possible outcomes
"""

def actions_utiles(state: GameStateQuoridor, eloigne):
    murs_possibles = tuple(state._legal_walls())
    mouvements = tuple(state._legal_moves())
    murs_present = state.rep.walls
    positions = state.rep.pawn_positions
    murs_valides = []
    for mur in murs_possibles:
        for objet in murs_present:
            if mur.data["destination"][0] < objet.row + eloigne + 1 and mur.data["destination"][0] > objet.row - eloigne - 1 and mur.data["destination"][1]  < objet.col + eloigne + 1 and mur.data["destination"][1] > objet.col - eloigne - 1:
                murs_valides.append(mur)
                break
        for objet in positions:
            pos = positions[objet]
            if mur.data["destination"][0] < pos[0] + eloigne and mur.data["destination"][0] > pos[0] - eloigne - 1 and mur.data["destination"][1] < pos[1] + eloigne and mur.data["destination"][1] > pos[1] - eloigne - 1:
                murs_valides.append(mur)
                break
    return tuple(murs_valides) + mouvements



#Delta dist_estimee

def delta_dist(state : GameStateQuoridor, inverse):
    delta = inverse * (dist_estimee(state, state.players[1]) - dist_estimee(state, state.players[0]))
    return delta

#Minimax avec alpha-beta churning

def minimax(state, my_player : bool, alpha, beta, depth, inverse):

    #Winner?

    if state._goal_reached(state.rep, state.players[0]):
        if inverse == -1:
            return (-100, None)
        else:
            return (100, None)

    if state._goal_reached(state.rep, state.players[1]):
        if inverse == 1:
            return (-100, None)
        else:
            return (100, None)


    #Depth reached?

    if depth == 0:
        return (delta_dist(state, inverse), None)
    

    #Iterate

    if my_player :
        maximum = -1000
        actions = actions_utiles(state, 1)

        for action in actions :
            impact = minimax(state.apply_action(action), False, alpha, beta, depth-1, inverse)[0]
            if maximum < impact:
                maximum = impact
                meilleure_action = action
            alpha = max(alpha, impact)
            if beta <= alpha:
                break
        return (maximum, meilleure_action)

    else :
        minimum = 1000
        actions = actions_utiles(state, 0)
        for action in actions :
            impact = minimax(state.apply_action(action), True, alpha, beta, depth-1, inverse)[0]
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
        #agencement des formules
        if current_state.active_player.id == current_state.players[1].id :
            inverse = -1
        else : 
            inverse = 1
        

        #Coups initiaux

        beta = 1000
        alpha = -1000
        depth = 3
        #Minimax
        resultat = minimax(current_state, True, alpha, beta, depth, inverse)
        meilleure_action = resultat[1]
        return meilleure_action
        
        



        
        #minimax
            
