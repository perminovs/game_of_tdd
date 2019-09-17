from typing import List

import pytest

from game.board import Board, Point, is_empty, CeilState, get_next_board, filter_alive


@pytest.fixture()
def board(faker):
    return Board(
        width=faker.pyint(min_value=4, max_value=100),
        height=faker.pyint(min_value=4, max_value=100),
    )


@pytest.fixture()
def point(board, faker):
    return Point(x=faker.pyint(min_value=0, max_value=board._width - 1),
                 y=faker.pyint(min_value=0, max_value=board._height - 1))


def test_create_instance(board):
    assert board


def test__check_geometry(faker):
    width = faker.pyint(min_value=1, max_value=100)
    height = faker.pyint(min_value=1, max_value=100)
    array = Board(width=width, height=height).to_array()
    assert len(array) == height
    assert all(len(line) == width for line in array)


def test_get_empty_ceils(board):
    assert is_empty(board.to_array())


def test_mark_alive(board, faker):
    point = Point(x=faker.pyint(min_value=0, max_value=board.width - 1),
                  y=faker.pyint(min_value=0, max_value=board.height - 1))
    board.mark_alive(point=point)
    assert not is_empty(board.to_array())
    assert board.get(point) is CeilState.ALIVE


@pytest.mark.parametrize('mark_point', [
    Point(-1, 0),
    Point(0, -1),
    Point(-1, -1),
])
def test_mark_out_of_range_left(board, mark_point):
    board.mark_alive(mark_point)
    assert board.get(mark_point) is CeilState.ALIVE


@pytest.mark.parametrize('dx, dy', [
    (0, 1),
    (1, 0),
    (1, 1),
])
def test_mark_out_of_range_right(board, dx, dy):
    point = Point(board._width + dx, board._height + dy)
    board.mark_alive(point)
    assert board.get(point) is CeilState.ALIVE


def test_mark_dead(board, point):
    board.mark_alive(point=point)
    board.mark_dead(point=point)
    assert is_empty(board.to_array())


def test_double_mark_alive(board, point):
    board.mark_alive(point=point)
    board.mark_alive(point=point)
    assert not is_empty(board.to_array())
    assert board.get(point) is CeilState.ALIVE


def test_dobule_mark_dead(board, point):
    board.mark_alive(point=point)
    board.mark_dead(point=point)
    board.mark_dead(point=point)
    assert is_empty(board.to_array())


def test_neighbors(board, point):
    neighbors = list(board.get_neighbors(point))
    assert len(neighbors) == 8
    assert all(isinstance(ceil, CeilState) for ceil in neighbors)


def test_neighbors_detail(board, point):
    count_neighbors = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            board.mark_alive(Point(point.x + dx, point.y + dy))
            count_neighbors += 1
            assert_count_neighbors(board, point, count_neighbors)


def assert_count_neighbors(board, point, count):
    assert len(filter_alive(board.get_neighbors(point))) == count


def test_type_of_next_board(board):
    assert isinstance(get_next_board(board), Board)


def test_new_board_is_new_instance(board):
    new_board = get_next_board(board)
    assert new_board is not board


@pytest.mark.parametrize('initial, expected', [
    (
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ],
    ),
    (
        [
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 1],
        ],
        [
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 1],
        ],
    ),
    (
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ],
    ),
    (
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
    ),
])
def test_get_next_board(initial, expected):
    board = generate_board(initial)
    next_state = get_next_board(board)

    assert next_state == generate_board(expected)


def generate_board(array: List[List[int]]) -> Board:
    h, w = len(array), len(array[0])
    board = Board(width=w, height=h)
    for point in board.iter_points():
        if array[point.y][point.x]:
            board.mark_alive(point)
    return board
