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
"""
Trouver la distance estimée restante a parcourir en ce moment moyenne sur nombre de murs restants, plus tard ML ou modélisation probabiliste.
Utiliser le tours, donc si égale, fois 0.5 pour le joeur en deuxième à jouer, pour favoriser le joueur en premier.

"""
# Heuristique 

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

# bfs pour trouver le chemin de l'adversaire, utilisé pour générer des murs bloquants
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

def gen_actions_utiles(state, player, remaining_time, time_start, strat):

    time_left = remaining_time - (time.perf_counter() - time_start)
    candidats = set()
    
    mouvements = tuple(state._legal_moves())
    candidats.update

    #***(
    if state.rep.remaining_walls[state.active_player.id] != 0 and time_left > 5 and strat == False: # S'il reste des murs et s'il reste plus de 5 secondes
        
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

        Wall = actions_quoridor.Wall
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
        
    return mouvements + tuple(murs)



def minimax(self, state, my_player : bool, alpha, beta, depth, inverse, player, remaining_time, time_start, start, max_depth, cache_etats, wallcount):

    #Winner?

    if state._goal_reached(state.rep, state.players[0]):
        if inverse == -1:
            return (-100, None, {})
        else:
            return (100, None, {})

    elif state._goal_reached(state.rep, state.players[1]):
        if inverse == 1:
            return (-100, None, {})
        else:
            return (100, None, {})


    #Depth reached?

    elif depth == 0:
        return (evaluer(state, inverse), None, {})

    

    #Iterate

    else:

        minimum = 1000
        maximum = -1000

        """
            IA générative partiellement utilisée pour écrire le if suivant en gros on match 
            les états du cache avec les actions du gen actions pour ordonner le tout 
            par rapport au score calculé précédement (du cache) 
            soit les actions avec un score désiré passent en premier pour le pruning
        """       
        #(***
        if cache_etats is not None:
            connus = sorted(cache_etats.items(), key=lambda x: x[1][1], reverse=my_player)
            actions_connues = {e[2] for _, e in connus}
            reste = [a for a in gen_actions_utiles(state, player, remaining_time, time_start, start) if a not in actions_connues]
        else:
            connus = []
            actions_connues = []
            reste = gen_actions_utiles(state, player, remaining_time, time_start, start)
        
        actions = [(e[2], s) for s, e in connus] + [(a, None) for a in reste]
        #***)
        cache_tree = {}
        liste_cache_tree = []        
        for action, enfant in actions:
            if enfant is None:                       # not pre-generated: pay for it now, lazily
                enfant = state.apply_action(action)
            if type(action) == actions_quoridor.WallAction:
                adder = 1
            else:
                adder = 0
            if self._flat_cache.get(wallcount+adder).get(enfant) is not None and self._flat_cache.get(wallcount+adder).get(enfant)[2]>=depth-1:
                sous_cache, impact, _ = self._flat_cache[wallcount+adder][enfant]
            else:
                impact, _, sous_cache = minimax(self, enfant, not my_player, alpha, beta, depth-1, inverse, player, remaining_time, time_start, start, max_depth, cache_etats.get(enfant), wallcount+adder)
                self._flat_cache[wallcount+adder][enfant] = (sous_cache, impact, depth-1)

            if my_player:      
                
                # Cache generation
                if max_depth == depth:
                    liste_cache_tree.extend(sous_cache.items())
                else:
                    liste_cache_tree.append((enfant, (sous_cache, impact, action)))
   
                if maximum < impact:
                    maximum = impact
                    meilleure_action = action
                alpha = max(alpha, impact)
                if beta <= alpha:
                    break
            
            else:
                

                if max_depth == depth :
                    liste_cache_tree.extend(sous_cache.items())
                else :
                    liste_cache_tree.append((enfant, (sous_cache, impact, action)))

                if minimum > impact:
                    minimum = impact
                    meilleure_action = action
                beta = min(beta, impact)

                if beta <= alpha :
                    break

        
        cache_tree = dict(liste_cache_tree)

        return (maximum, meilleure_action, cache_tree)





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
        self._flat_cache = {}
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
        wallcount = len(current_state.rep.walls)
        self._flat_cache.pop(wallcount-1, None)
        self._flat_cache.pop(wallcount-2, None)
        #agencement des formules
        if current_state.active_player.id == current_state.players[1].id :
            inverse = -1
            player = current_state.players[1].id
        else : 
            inverse = 1
            player = current_state.players[0].id

        
        start = False
        if current_state.get_step()/2 < 3:
            start = True
        
        liste_etats = self._cache.get(current_state)

            # liste_etats.sort(key=lambda x:x[1], reverse=True)

        self._cache = {}

        beta = 1000
        alpha = -1000
        if remaining_time>600:
            depth = 5
        elif remaining_time>150:
            depth = 4
        else:
            depth = 3

        #Minimax
        _, resultat, cache = minimax(self, current_state, True, alpha, beta, depth, inverse, player, remaining_time, start_time, start, depth, liste_etats, wallcount)
        self._cache = cache
        meilleure_action = resultat


        return meilleure_action

