from seahorse.game.game_state import StatelessAction
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
    """
    remaining_walls = state.rep.remaining_walls

    if player == state.players[0]:
        murs_restants_adv = remaining_walls[state.players[1].id]
    else :
        murs_restants_adv = remaining_walls[state.players[0].id]
    """
    return chemin
# 2.5 a revérifier par regression linéaire et ajuster avec gamestate par ML


"""
Only compute walls that are sticked to player or other wall + 1 space and 1 space further for less possible outcomes
"""

"""
    ***Cette boucle à été partiellement écrite par IA pour réduire l'engorgement de l'écran, la section touchée est ilustrée par des commentaires #***(), à noter 
    que des modifications ont tout de même étées apporter à ces sections.
    
    Cette section proviens d'une boucle de la V2 passant au travers des "legal wall" avec la condition que les murs toucehnt ou soient a distance de 1 des autres,
    faisant que le nombre ditération venaient rallonger le code donc une version écrite a la main est venue, au lieu de passer par "_legal_moves", vérifier
    les états possibles avec "_is_wall_legal". La version humaine faisant des lignes de codes trop longues et invoquant a plusieurs reprises des méthodes ".append"
    étaient inneficace et illisible donc l'ia s'est occupé de générer la même logique sous forme de "set".
"""

#***(
H, V = actions_quoridor.Orientation.HORIZONTAL, actions_quoridor.Orientation.VERTICAL
#***)

def gen_actions_utiles(state, inverse):
    mouvements = tuple(state._legal_moves())
    candidats = set()
    Wall = actions_quoridor.Wall

    #***(
    if state.rep.remaining_walls[state.active_player.id] != 0 and delta_dist(state, inverse) < 4:
        
        for r, c in state.rep.pawn_positions.values():
            candidats.update([
                (r, c - 1, H), (r, c - 2, H), (r - 1, c - 1, H), (r - 1, c - 2, H),
                (r - 1, c, V), (r - 2, c, V), (r - 1, c - 1, V), (r - 2, c - 1, V),
            ])

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
            
            if o == V and ((r>=8 or r<0) or (c==0 or c==9)):
                continue
            if o == H and ((c>=8 or c<0) or (r==0 or r==9)):
                continue

            wall = Wall(r, c, o)
            if state._is_wall_legal(wall):
                murs.append(StatelessAction({
                    "type": "vertical" if o == V else "horizontal",
                    "destination": (r, c),
                }))
    #***
    return mouvements + tuple(murs)


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

    elif state._goal_reached(state.rep, state.players[1]):
        if inverse == 1:
            return (-100, None)
        else:
            return (100, None)


    #Depth reached?

    elif depth == 0:
        return (delta_dist(state, inverse), None)
    

    #Iterate

    elif my_player :
        maximum = -1000
        actions = gen_actions_utiles(state, inverse)

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
        actions = gen_actions_utiles(state, inverse)
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
        beta = 1000
        alpha = -1000
        depth = 4
        #Minimax
        resultat = minimax(current_state, True, alpha, beta, depth, inverse)
        meilleure_action = resultat[1]
 

        return meilleure_action
            
        



        
        #minimax
            
