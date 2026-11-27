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

#==== Heuristique =====

POIDS = {"distance": 1, "walls": 1}

def evaluer(state, inverse):

    score = 0
    
    if inverse == 1:
        moi = state.players[0]
    else:
        moi = state.players[1]

    adv = state._opponent(moi)

    d_moi = distance_reel(state, moi)
    d_adv = distance_reel(state, adv)

    moi_murs = state.rep.remaining_walls[moi.id]
    adv_murs = state.rep.remaining_walls[adv.id]

    heuristique = {
        "distance": d_adv - d_moi,
        "walls": moi_murs - adv_murs
    }

    # Déterminer si c'est le tour du joueur actif
    if state.active_player.id == moi.id:
        mon_tour = True
    else:
        mon_tour = False

    # Détermine si le joueur actif est en position de gagner
    if d_moi < d_adv or (d_moi == d_adv and mon_tour):
        je_gagne = True
    else:
        je_gagne = False

    # Si le joueur actif est en position de gagner boost le score, sinon le diminue
    if adv_murs == 0 and je_gagne:
        score += 50

    elif moi_murs == 0 and not je_gagne:
        score += -50


    for nom, valeur in heuristique.items():
        score += valeur * POIDS[nom]
        
    return score

def chemin_adversaire(state, joueur):
    depart = state.rep.pawn_positions[joueur.id]
    etats = deque([(depart, [depart])])
    visitees = {depart}

    while etats:
        position, chemin = etats.popleft()

        if position[0] == joueur.get_goal_row():
            return chemin

        for voisin in state._reachable_neighbours(position):
            if voisin not in visitees:
                visitees.add(voisin)
                etats.append((voisin, chemin + [voisin]))
    return []

def distance_reel(state, joueur):
    # Calcule la distance du joueur à la fin en prenant en compte le saut par dessus l'autre
    # pion quand ils sont collées et que c'est au joueur actif de jouer.

    distance = state._shortest_path(joueur)

    if state.active_player.id != joueur.id:
        return distance

    adversaire = state._opponent(joueur)
    r1, c1 = state.rep.pawn_positions[joueur.id]
    r2, c2 = state.rep.pawn_positions[adversaire.id]

    # pion pas collées
    if abs(r1 - r2) + abs(c1 - c2) != 1:
        return distance

    # pion collées
    for action in state._legal_moves():
        nouvel_etat = state.apply_action(action)
        reste = nouvel_etat._shortest_path(joueur)
        if 1 + reste < distance:
            distance = 1 + reste

    return distance


"""
Trouver la distance estimée restante a parcourir en ce moment moyenne sur nombre de murs restants, plus tard ML ou modélisation probabiliste.
Utiliser le tours, donc si égale, fois 0.5 pour le joeur en deuxième à jouer, pour favoriser le joueur en premier.
"""


"""
    ***Cette boucle à été partiellement écrite par IA pour réduire l'engorgement de l'écran, la section touchée est ilustrée par des commentaires #***(), à noter 
    que des modifications ont tout de même étées apporter à ces sections.
    
    Cette section proviens d'une boucle de la V2 passant au travers des "legal wall" avec la condition que les murs touchent ou soient a distance de 1 des autres,
    faisant que le nombre ditération venaient rallonger le code donc une version écrite a la main est venue, au lieu de passer par "_legal_moves", vérifier
    les états possibles avec "_is_wall_legal". La version humaine faisant des lignes de codes trop longues et invoquait a plusieurs reprises des méthodes ".append"
    qui étaient inneficace et illisible donc l'ia s'est occupé de générer la même logique sous forme de "set".
"""

H, V = actions_quoridor.Orientation.HORIZONTAL, actions_quoridor.Orientation.VERTICAL

# combien de pas du chemin adverse on essaie de bloquer
NB_PAS = 4 
def gen_actions_utiles(state, remaining_time, time_start, opening):

    time_left = remaining_time - (time.perf_counter() - time_start)
    mouvements = tuple(state._legal_moves())
    candidats = set()
    Wall = actions_quoridor.Wall

    #***(
    if state.rep.remaining_walls[state.active_player.id] != 0 and time_left > 5 and opening == False: # S'il reste des murs et s'il reste plus de 5 secondes

        victime = state._opponent(state.active_player)
        r, c = state.rep.pawn_positions[victime.id]
        chemin = chemin_adversaire(state, victime)

        # Regarder les murs autour du joueur adverse pour générer des candidats de placement de murs
        for dr, dc in state.DIRECTIONS:
            voisine = (r + dr, c + dc)
            if not (0 <= voisine[0] < state.rep.dimension and 0 <= voisine[1] < state.rep.dimension):
                continue
            for w in state._candidate_blocking_walls((r, c), voisine):
                candidats.add((w.row, w.col, w.orientation))

        # Regarde le chemin de l'adversaire et génère des candidats de placement de murs pour bloquer le chemin
        for i in range(min(NB_PAS, len(chemin) -1)):
            depart = chemin[i]
            arrivee = chemin[i+1]
            for w in state._candidate_blocking_walls(depart, arrivee):
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

            dim = state.rep.dimension
            
            if o == V and not (1 <= c <= dim - 1):
                continue
            if o == H and not (1 <= r <= dim - 1):
                continue

            wall = Wall(r, c, o)
            if state._is_wall_legal(wall):
                murs.append(StatelessAction({
                    "type": "vertical" if o == V else "horizontal",
                    "destination": (r, c),
                }))
    #***)
    return mouvements + tuple(murs)

def minimax(self, state, my_player : bool, alpha, beta, depth, inverse, remaining_time, time_start, start, etats_finaux):

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
        actions = gen_actions_utiles(state, remaining_time, time_start, start)
        
        for action in actions :
            applied_action = state.apply_action(action)
            impact = minimax(self, applied_action, False, alpha, beta, depth-1, inverse, remaining_time, time_start, start, etats_finaux)[0]
            if maximum < impact:
                maximum = impact
                meilleure_action = action
            alpha = max(alpha, impact)
            if beta <= alpha:
                break
        if depth == 2:
            self._cache[state] = etats_finaux

        return (maximum, meilleure_action)

    else :
        minimum = 1000
        actions = gen_actions_utiles(state, remaining_time, time_start, start)
        for action in actions :
            applied_action = state.apply_action(action)
            impact = minimax(self, applied_action, True, alpha, beta, depth-1, inverse, remaining_time, time_start, start, etats_finaux)[0]
            if depth == 1:
                etats_finaux.append((applied_action, impact))
            if minimum > impact:
                minimum = impact
                meilleure_action = action
            beta = min(beta, impact)

            if beta <= alpha:
                break

        return (minimum, meilleure_action)


#Minimax avec alpha-beta churning



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
        self._cache = {}
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
        liste_score = []

        # Opening pour live, calcule juste le plus court chemin
        start = False
        if current_state.get_step()/2 < 3:
            start = True


        liste_etats = self._cache.get(current_state)
        if liste_etats != None:
            liste_etats.sort(key=lambda x:x[1], reverse=True)
            for t in liste_etats:
                liste_score.append(t[1])

        self._cache = {}

        beta = 1000
        alpha = -1000
        if remaining_time>600:
            depth = 4
        elif remaining_time>150:
            depth = 4
        else:
            depth = 3
        etats_finaux = []

        #Minimax
        resultat = minimax(self, current_state, True, alpha, beta, depth, inverse, remaining_time, start_time, start, etats_finaux)
        meilleure_action = resultat[1]
 
        print(f"{len(liste_score)}\n\n")
        return meilleure_action

