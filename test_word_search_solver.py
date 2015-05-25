import unittest
import word_search_solver as wss

# os is used to create a test_file.txt, so it
# can easily be altered as part of testing.
import os

TEST_KEYS = ['AAOA', 'OOOO']
TEST_GRAPH = [
    'AAAO',
    'AAOA',
    'AOAA',
    'OAAA'
]

KEY_FILE_PATH = 'word_list.txt'
GRAPH_FILE_PATH = 'word_search.txt'

TEST_KEYS_PATH = 'test_keys_file.txt'
TEST_GRAPH_PATH = 'test_graph_file.txt'


def write_list_to_txt_file(file_name, what_to_write):
    with open(file_name, 'w+') as the_file:
        for each_line in what_to_write:
            the_file.write('{}\n'.format(each_line))


def uses_test_files(original_function):
    '''
    Before executing the decorated function, create a test file using
    the TEST_GRAPH constant, and another using the TEST_KEYS constant.

    Remove both created files when the decorated function finishes,
    even if the decorated function raises an exception.
    '''

    def decorated_function(*args, **kwargs):
        try:
            write_list_to_txt_file(TEST_KEYS_PATH, TEST_KEYS)
            write_list_to_txt_file(TEST_GRAPH_PATH, TEST_GRAPH)

            original_function(*args, **kwargs)

        # Using a try:finally block ensures the test file is deleted
        # after the function is over, even if the function raises an
        # exception (since test files aren't supposed to have side effects).
        finally:
            os.remove(TEST_KEYS_PATH)
            os.remove(TEST_GRAPH_PATH)

    return decorated_function


class TestWordSearchSolver(unittest.TestCase):

    def setUp(self):
        real_files = (KEY_FILE_PATH, GRAPH_FILE_PATH)
        test_files = (TEST_KEYS_PATH, TEST_GRAPH_PATH)

        # The stars are unpacking operands.
        # One star unpacks a tuple, two stars unpacks a dictionary.
        self.real_solver = wss.WordSearchSolver(*real_files, no_output=True)
        self.test_solver = wss.WordSearchSolver(*test_files, no_output=True)

    @uses_test_files
    def test_load_list_from_text_file(self):

        real_file_as_list = wss.load_list_from_text_file(GRAPH_FILE_PATH)
        assert len(real_file_as_list) == 18
        assert len(real_file_as_list[0]) == 18
        assert len(real_file_as_list[17]) == 18

        test_file_as_list = wss.load_list_from_text_file(TEST_GRAPH_PATH)
        assert len(test_file_as_list) == 4
        assert len(test_file_as_list[0]) == 4
        assert len(test_file_as_list[3]) == 4

    @uses_test_files
    def test_build_dictionary_of_coordinates(self):

        self.setUp()

        self.test_solver.build_dictionary_of_coordinates()
        assert len(self.test_solver.coordinates.keys()) == 2
        assert len(self.test_solver.coordinates['A']) == 12
        assert len(self.test_solver.coordinates['O']) == 4

        self.real_solver.build_dictionary_of_coordinates()
        # The alphabet, minus Q and Z:
        assert len(self.real_solver.coordinates.keys()) == 24

        assert len(self.real_solver.coordinates['A']) == 29
        assert len(self.real_solver.coordinates['O']) == 26

        assert len(self.real_solver.coordinates['W']) == 7
        assert len(self.real_solver.coordinates['I']) == 23
        assert len(self.real_solver.coordinates['R']) == 33
        assert len(self.real_solver.coordinates['E']) == 32
        assert len(self.real_solver.coordinates['L']) == 16
        assert len(self.real_solver.coordinates['S']) == 15
        assert len(self.real_solver.coordinates['C']) == 13

    @uses_test_files
    def test_check_for_word_in_direction(self):

        self.setUp()

        self.test_solver.build_dictionary_of_coordinates()
        result = self.test_solver.check_for_word_in_direction('AAOA', 'LR')
        assert len(result) == 1
        assert result[0] == (0, 1)

        result = self.test_solver.check_for_word_in_direction('OOOO', 'DDL')
        assert len(result) == 1
        assert result[0] == (3, 0)

        self.real_solver.build_dictionary_of_coordinates()
        result = self.real_solver.check_for_word_in_direction('WIRE', 'DUR')
        assert result[0] == (3, 12)

        result = self.real_solver.check_for_word_in_direction('LESC', 'DUR')
        assert result[0] == (7, 8)

    def test_solve_puzzle(self):

        self.setUp()

        result = self.real_solver.solve_puzzle()

        assert len(result) == 53

        assert 'Binary' in result
        assert 'LCD' in result
        assert 'Disk drive' in result
        assert 'Wireless' in result

        assert result['Binary'] == {'DUR': [(2, 11)]}
        assert result['LCD'] == {'D': [(0, 1)]}
        assert result['Disk drive'] == {'DUR': [(2, 17)]}
        assert result['Wireless'] == {}  # but 'WIRELESC' is {'DUR': [(3, 12)]}

    def test_write_solution_to_file(self):

        self.setUp()

        result = self.real_solver.solve_puzzle()

        wss.write_solution_to_file(result, file_name='tested.txt')

        try:
            written_file = wss.load_list_from_text_file('tested.txt')
            assert 'Binary:' in written_file
            assert 'LCD:' in written_file
            assert 'Disk drive:' in written_file
            assert 'Wireless:' in written_file
            assert '    DUR:' in written_file
            assert '        (2, 11)' in written_file
            assert '    Not found.' in written_file
        finally:
            os.remove('tested.txt')


unittest.main()
