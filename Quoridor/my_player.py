import actions_quoridor
import game_state_quoridor
from player_quoridor import PlayerQuoridor
from seahorse.game.action import Action
from game_state_quoridor import GameStateQuoridor
from seahorse.utils.custom_exceptions import MethodNotImplementedError

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
        meilleure_action = None
        negatif = 1
        delta = current_state._shortest_path(current_state.players[0]) - current_state._shortest_path(current_state.players[1])
        if current_state.active_player.id == current_state.players[1].id:
            negatif = -1    
            delta *= negatif
        walls = tuple(current_state._legal_walls())
        print(walls)
        moves = tuple(current_state._legal_moves())
        bestwdelta = 100
        bestmdelta = 100
        if delta > 0 and walls != None:
            for wall in walls:
                wstate = current_state.apply_action(wall)
                wdelta = negatif*(wstate._shortest_path(current_state.players[0])-wstate._shortest_path(current_state.players[1])) - 0.5*wstate._shortest_path(wstate.active_player)
                if wdelta < bestwdelta:
                    bestwdelta = wdelta
                    meilleure_action = wall
        else:
            for move in moves:
                mstate = current_state.apply_action(move)
                mdelta = mstate._shortest_path(current_state.players[0])-mstate._shortest_path(current_state.players[1])
                mdelta*= negatif
                if mdelta < bestmdelta:
                    bestmdelta = mdelta
                    meilleure_action = move

        if meilleure_action == None:
            meilleure_action = moves[0]
        return meilleure_action
