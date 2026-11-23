from board_quoridor import BoardQuoridor
from game_state_quoridor import GameStateQuoridor
from player_quoridor import PlayerQuoridor
from actions_quoridor import Wall, Orientation
from meow import chemin_adversaire

blanc = PlayerQuoridor("W", goal_row=0, name="blanc")
noir = PlayerQuoridor("B", goal_row=8, name="noir")

def etat(murs=frozenset()):
    rep = BoardQuoridor({blanc.get_id(): (8, 4), noir.get_id(): (0, 4)}, murs,
                        {blanc.get_id(): 10, noir.get_id(): 10})
    return GameStateQuoridor({blanc.get_id(): 0, noir.get_id(): 0}, blanc,
                             players=[blanc, noir], rep=rep, step=0)

print("Blanc, départ :", chemin_adversaire(etat(), blanc))
print("Noir,  départ :", chemin_adversaire(etat(), noir))

mur = frozenset({Wall(4, 3, Orientation.HORIZONTAL)})
print("Blanc, avec un mur :", chemin_adversaire(etat(mur), blanc))