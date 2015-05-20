
# Word Search Solver by Ben Friedland

# The goal of this program is to solve word search puzzles.

# Specifications:
# "Given a collection of letters which contain hidden words
# (in the file 'word_search.txt'), find all of the words in
# the word list (in the file 'word_list.txt') within the puzzle.
# Remember, the words may be hidden left to right, right to left,
# up, down or diagonally."

# Initial procedure, considered while trying to reduce
# my reliance on iterating over the board:
# 1. find the first letter in the word inside the word grid
#       -- 1a save x+y coords of this letter position
# 2. for each of the eight letters around it, if inside the grid:
# 3. check if one of them is a match to the second letter in the word
#       -- 3a save x+y offset of this letter position
# 4. continue checking tiles in the direction of this offset,
#       until match failure or grid edge is reached,
#       or until the word runs out of letters
# 5. save resulting location and direction in solutions dictonary
# 6. iterate 1-5 until system is out of words

# While starting down this path, I realized this was similar to
# the graph problems I'd worked on at Code Fellows, where I read
# about Guido van Rossum's suggestion on how to implement graphs with
# dictionaries. I thought it would be a good idea to load coordinates
# for all the letters into a dictionary so I could check small subsets
# of the tiles for each word.

# The following algorithm will:
# 1. load the file as a list of strings, one string per row
# 2. build a lookup table relating all of the letters to a list containing
#       tuples of all the coordinates at which each letter can be found,
#       in the format (y, x), which was chosen because that's the simplest
#       way to iterate over the grid when it's broken into rows before columns.
# 3. for each word, for each direction, the algorithm will iterate through
#       each location the first letter in that word can be found at
#       (using the lookup table).
# 4. For each location of the word's first letter, the algorithm
#       will iterate through each letter of the word, comparing all
#       coordinate tuples in the lookup table that are filed under
#       that letter, to see if their coordinates match the next step
#       in that direction. Stepping is handled by incrementing or
#       decrementing from the first letter's coordinates using the
#       direction values in the directions dictionary.
# 5. If at any point in step 4 a letter cannot be found in the lookup
#       table, it will prevent the algorithm from saving the combination
#       of word, first letter coordinates, and direction, which would
#       otherwise be inserted into the found_words dictionary and returned
#       as the output of the algorithm.

# While in the later stages of implementing this, I thought it would be
# a good idea to make the first value in each coordinate tuple a dictionary
# as well. This means the algorithm would never have to iterate over every
# single location a letter was found -- it could instead execute the 'dy'
# part of its directional stepping and use that to select the appropriate
# row in the dictionary of row indices inside the dictionary of letters,
# potentially reducing the number of list iterations that
# check_for_word_in_direction had to do to its square root
# (assuming letters are evenly distributed).

# But that seemed unnecessary for the size of the word search graph
# provided with the puzzle, and might make it harder to explain and debug.
# I decided to heed the instructions' advice that "solid, well performing
# code always wins out over clever code," and settle with not having to
# scan every letter in the graph for every word in the word list.


import os
import sys
import collections


class WordSearchSolver(object):  # Subclassing object is a Py2 best practice.
    '''
    Create a WordSearchSolver instance using a key_file_path and a
    grid_file_path, accepting an optional no_output boolean to disable
    writing the solution to a file if True (defaults to False).

    Contains a class attribute named directions, which contains
    a dictionary mapping direction code strings to step increments.
    '''

    # Directions are stored as (dy, dx) tuples in a class attribute.
    # They represent the change (ie delta, or d) in y and x coordinates
    # as the solver attempts to construct paths between nodes in the graph.
    directions = {
        'LR':  (0,   1),  # Left to right
        'RL':  (0,  -1),  # Right to left
        'U':   (-1,  0),  # Up
        'D':   (1,   0),  # Down
        'DUL': (-1, -1),  # Diagonal up left
        'DUR': (-1,  1),  # Diagonal up right
        'DDL': (1,  -1),  # Diagonal down left
        'DDR': (1,   1)   # Diagonal down right
    }

    def __init__(self, key_file_path, grid_file_path, no_output=False):

        self.key_file_path = key_file_path
        self.grid_file_path = grid_file_path
        self.no_output = no_output

        # Instance state variables, to hold the results of calling
        # build_dictionary_of_coordinates and load_list_from_text_file
        # during the execution of solve_puzzle.
        self.coordinates = {}
        self.keys = []
        self.grid = []

    def build_dictionary_of_coordinates(self):
        '''
        Take in a list of equal-length lists and return
        a dictionary using each element found in the list
        as keys, each of which uses a list of all the (x, y)
        coordinate pairs where each element was found as values.

        This implementation accepts lists of lists composed of
        any type of element that supports the equality operator
        and assignment as a dictionary key. It also works for
        arbitrary lengths of both top-level lists and sub-lists.
        '''

        self.coordinates = collections.defaultdict(list)

        grid = load_list_from_text_file(self.grid_file_path)

        for y_coordinate, each_row in enumerate(grid):
            for x_coordinate, each_column in enumerate(each_row):
                key = grid[y_coordinate][x_coordinate]

                # Using a tuple implies the data is immutable.
                coords = (y_coordinate, x_coordinate)
                self.coordinates[key].append(coords)

    def check_for_word_in_direction(self, word, direction):
        '''
        Uses this WordSearchSolver instance's coordinates dictionary
        to check every occurrence of the first letter in the word in the
        dictionary for matching subsequent letters in the word in the
        dictionary in the supplied direction.

        The word parameter must be a string, and the direction parameter
        must be a key in the WordSearchSolver.directions dictionary.
        '''

        dy, dx = WordSearchSolver.directions[direction]

        # We care about the first letter because words aren't supposed to
        # change direction after we've started finding matching letters.
        first_letter = word[0]

        locations_for_first_letter = self.coordinates[first_letter]

        results_list = []

        # We need to check each instance of the first letter, so
        # iterate over all the locations where that letter can be found:
        for each_location in locations_for_first_letter:

            y, x = initial_y, initial_x = each_location

            letters_match = True

            # Next, for each letter (including the first), retrieve
            # a list of all coordinates where that letter can be found
            # and see if the current letter were're looking at's location
            # matches up with the expected location:
            for each_letter in word:

                if letters_match is True:

                    # A space isn't a letter.
                    # While there are some "words" with spaces
                    # in them in the WordList.txt file, there
                    # are none in the WordSearch.txt file.
                    # This program will assume words with spaces in
                    # the WordList.txt file are included in the
                    # WordSearch.txt file with spaces removed.
                    if each_letter == ' ':
                        continue

                    letter_as_key = each_letter.upper()

                    all_coords_of_this_letter = self.coordinates[letter_as_key]

                    # The following will iterate over every letter
                    # coordinate, which is actually not as good as
                    # checking the letters in each direction around
                    # the first letter (which still benefits from
                    # using a lookup table) and verifying letters by
                    # directly checking list indices in the grid rather
                    # than the lookup table. But that would take more
                    # time to implement, and this is already pretty fast.
                    if (y, x) in all_coords_of_this_letter:
                        # If a match has been found, take
                        # another step in this direction:
                        y += dy
                        x += dx

                        # Note that, because we're not checking grid
                        # indices but instead looking for tuple presence
                        # in a dictionary, there will never be an IndexError
                        # due to iterating outside the grid's boundaries.

                    else:
                        letters_match = False

            if letters_match is True:

                # The (x, y) ordering is intentional for readability.
                word_location = (initial_x, initial_y)

                results_list.append(word_location)

        return results_list

    def solve_puzzle(self):
        '''
        Solve the word search puzzle found at this WordSearchSolver
        instance's grid_file_path and key_file_path by building
        a dictionary of letter coordinates and and finding words
        with it. Faster than iterating over every tile for every
        new word.

        If this WordSearchSolver instance's no_output tag is
        False (defaults to False), the output will be passed
        to the write_solution_to_file function.
        '''

        # Because Python allows me to treat strings as lists,
        # a depth-one list is all we need to model this grid.
        self.grid = load_list_from_text_file(self.grid_file_path)
        self.keys = load_list_from_text_file(self.key_file_path)

        self.build_dictionary_of_coordinates()

        # Subdicts for directions, since one word could conceivably
        # have multiple directions and/or locations.
        found_words = collections.defaultdict(dict)

        for word in self.keys:

            for direction in WordSearchSolver.directions.keys():

                results = self.check_for_word_in_direction(word, direction)

                if results:
                    # {'LCD': {D: [(1, 0) ...] ...}, }
                    found_words[word][direction] = results

        if self.no_output is False:
            write_solution_to_file(found_words)

        return found_words


def write_solution_to_file(results, file_name='fancy_solution.txt'):
    '''
    Write the results of calling solve_puzzle
    to a text file, with pretty printing.
    '''

    explanation = ('\nFormat of this file:'
                   '\n\nEach word found:'
                   '\n\tEach direction the word was found in:'
                   '\n\t\t(X, Y) coordinates of first letter in the word.'
                   '\n\n')

    with open(file_name, 'w+') as solution_file:

        solution_file.write(explanation)

        sorted_keys = sorted(results)

        for each_key in sorted_keys:

            solution_file.write('\n\n{}:'.format(each_key))

            if not results[each_key]:
                    solution_file.write('\n\tNot found.'.format(each_key))

            for each_direction in results[each_key].keys():

                solution_file.write('\n\t{}:'.format(each_direction))

                for each_result in results[each_key][each_direction]:

                    x = each_result[0]
                    y = each_result[1]

                    solution_file.write('\n\t\t({}, {})'.format(x, y))

        solution_file.write('\n')


def load_list_from_text_file(file_name):
    '''
    Load file_name and return a list containing all lines from it.
    '''

    with open(file_name) as opened_file:
        lines = opened_file.read().splitlines()

    return lines


if __name__ == '__main__':

    import sys

    # Rudimentary support for custom word search files.
    if len(sys.argv) > 1:
        key_file_path = sys.argv[2]
        grid_file_path = sys.argv[3]
    else:
        key_file_path = 'word_list.txt'
        grid_file_path = 'word_search.txt'

    solver = WordSearchSolver(key_file_path, grid_file_path)
    solution = solver.solve_puzzle()

    print("fancy_solution.txt file written.")
