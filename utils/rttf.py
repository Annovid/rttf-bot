from clients.client import RTTFClient
from parsers.player_parser import PlayerParser
from utils.models import Player


def get_player_info(player_id: int) -> Player:
    player_page = RTTFClient().get_player(player_id)
    player = PlayerParser.parse_data(player_page)
    return player


def main():
    player = get_player_info(163280)
    print(player)


if __name__ == '__main__':
    main()
