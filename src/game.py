from typing import List, Tuple, Literal
from starlette.websockets import WebSocket


class Player:

    def __init__(self, ws: WebSocket, state: Literal['X'] | Literal['O'] = 'X') -> None:
        self.__ws = ws
        self.__state = state

    async def get_state(self) -> Literal['X'] | Literal['O']:
        return self.__state

    async def get_ws(self) -> WebSocket:
        return self.__ws

    async def check_ws(self, ws: WebSocket) -> bool:
        return ws == self.__ws


class Game:

    winning_conditions: Tuple[tuple] = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    )
    game_state: List[Literal['X'] | Literal['O']] = ["", "", "", "", "", "", "", "", ""]

    __number: int = 0
    player_1: Player | None = None
    player_2: Player | None = None
    current_player: Literal['X', 'O'] = ''
    active_game: bool = False

    @classmethod
    async def create(cls, ws: WebSocket, number: int):
        self = cls()
        self.__number = number
        player = await self.create_player(ws)
        self.player_1 = player
        self.current_player = await player.get_state()
        return self

    @property
    def number(self) -> int:
        return self.__number

    async def create_player(self, ws: WebSocket) -> Player:
        return Player(ws, 'X')

    async def join_player(self, ws: WebSocket) -> None:
        player = Player(ws, 'O')
        if player != self.player_1 and player != self.player_2:
            self.player_2 = player
            self.active_game = True

    async def check_player_ws(self, ws: WebSocket) -> bool:
        is_ws = False
        if self.player_1 is not None:
            is_ws = await self.player_1.check_ws(ws)
        if not is_ws and self.player_2 is not None:
            is_ws = await self.player_2.check_ws(ws)
        return is_ws

    async def result_validation(self) -> str:
        won = False

        for i in self.winning_conditions:
            a = self.game_state[i[0]]
            b = self.game_state[i[1]]
            c = self.game_state[i[2]]

            if a == "" and b == "" and c == "":
                continue

            if a == b and b == c:
                won = True
                break

        if won:
            self.active_game = False
            return await self.winning_message()

        if "" not in self.game_state:
            self.active_game = False
            return await self.draw_message()

        await self.change_current_player()

        return await self.move_message()

    async def cell_played(self, cell_index) -> tuple:
        self.game_state[cell_index] = self.current_player
        return self.current_player, await self.result_validation(), self.active_game

    async def change_current_player(self) -> None:
        self.current_player = "X" if self.current_player != "X" else "O"

    async def winning_message(self) -> str:
        return f"?????????????? ?????????? {self.current_player}"

    async def draw_message(self) -> str:
        return f"??????????!!!"

    async def move_message(self) -> str:
        return f"?????? ???????????? {self.current_player}"

