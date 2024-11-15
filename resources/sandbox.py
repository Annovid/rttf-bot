from parsers.tournament_parser import TournamentParser
from parsers.tournaments_parser import TournamentsParser


def main():
    path = "static/htmls/2024-11-02/t/passed_pers.html"
    with open(path, "r") as f:
        page = f.read()
    ts = TournamentParser().parse_data(page)
    print(ts)


if __name__ == "__main__":
    main()
