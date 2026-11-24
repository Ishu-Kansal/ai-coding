import pytest

from tennis1 import TennisGame1
from tennis2 import TennisGame2
from tennis3 import TennisGame3
from tennis4 import TennisGame4
from tennis5 import TennisGame5
from tennis6 import TennisGame6
from tennis7 import TennisGame7
from tennis_unittest import play_game, test_cases


@pytest.mark.parametrize(
    "TennisGameClass",
    [
        TennisGame1,
        TennisGame2,
        TennisGame3,
        TennisGame4,
        TennisGame5,
        TennisGame6,
    ],
)
@pytest.mark.parametrize(
    "p1_points p2_points score p1_name p2_name".split(), test_cases
)
def test_get_score_most_games(
    TennisGameClass, p1_points, p2_points, score, p1_name, p2_name
):
    game = play_game(TennisGameClass, p1_points, p2_points, p1_name, p2_name)
    assert score == game.score()


@pytest.mark.parametrize(
    "p1_points p2_points score p1_name p2_name".split(), test_cases
)
def test_get_score_game7(p1_points, p2_points, score, p1_name, p2_name):
    game = play_game(TennisGame7, p1_points, p2_points, p1_name, p2_name)
    assert "Current score: " + score + ", enjoy your game!" == game.score()


def test_game1_score_with_custom_player_names():
    game = TennisGame1("Serena", "Venus")
    for player in (
        "Serena",
        "Venus",
        "Serena",
        "Venus",
        "Serena",
        "Venus",
        "Serena",
        "Serena",
    ):
        game.won_point(player)

    assert game.score() == "Win for Serena"


def test_game3_score_with_custom_player_names():
    game = TennisGame3("Serena", "Venus")
    for player in (
        "Serena",
        "Venus",
        "Serena",
        "Venus",
        "Serena",
        "Venus",
        "Serena",
        "Serena",
    ):
        game.won_point(player)

    assert game.score() == "Win for Serena"


def test_game1_high_deuce_scores_with_custom_player_names():
    for p1_points, p2_points, expected_score in (
        (15, 15, "Deuce"),
        (16, 15, "Advantage Serena"),
    ):
        game = play_game(TennisGame1, p1_points, p2_points, "Serena", "Venus")
        assert game.score() == expected_score


def test_game3_high_deuce_scores_with_custom_player_names():
    for p1_points, p2_points, expected_score in (
        (15, 15, "Deuce"),
        (16, 15, "Advantage Serena"),
    ):
        game = play_game(TennisGame3, p1_points, p2_points, "Serena", "Venus")
        assert game.score() == expected_score


def test_game1_rejects_points_after_game_is_won():
    initial_game = TennisGame1("Serena", "Venus")
    assert initial_game.isActive is True
    assert initial_game.winner is None

    game = play_game(TennisGame1, 6, 4, "Serena", "Venus")
    assert game.score() == "Win for Serena"
    assert game.isActive is False
    assert game.winner == "Serena"

    with pytest.raises(ValueError, match="^Game is already over$"):
        game.won_point("Venus")

    assert game.score() == "Win for Serena"
    assert game.winner == "Serena"


def test_game3_rejects_points_after_game_is_won():
    initial_game = TennisGame3("Serena", "Venus")
    assert initial_game.isActive is True
    assert initial_game.winner is None

    game = play_game(TennisGame3, 6, 4, "Serena", "Venus")
    assert game.score() == "Win for Serena"
    assert game.isActive is False
    assert game.winner == "Serena"

    with pytest.raises(ValueError, match="^Game is already over$"):
        game.won_point("Venus")

    assert game.score() == "Win for Serena"
    assert game.winner == "Serena"


@pytest.mark.parametrize(
    "p1_points,p2_points,expected_score",
    [
        (6, 4, "6-4"),
        (7, 6, "7-6"),
        (7, 5, "Win for Serena"),
    ],
)
def test_game1_tie_break_scores(p1_points, p2_points, expected_score):
    game = TennisGame1("Serena", "Venus", is_tie_break=True)

    for point in range(max(p1_points, p2_points)):
        if point < p1_points:
            game.won_point("Serena")
        if point < p2_points:
            game.won_point("Venus")

    assert game.score() == expected_score
