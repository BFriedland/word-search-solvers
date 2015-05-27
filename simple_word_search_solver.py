# Simpler Word Search Solver by Ben Friedland

# The goal of this program is to solve word search puzzles.

# Specifications:
# "Given a collection of letters which contain hidden words
# (in the file 'word_search.txt'), find all of the words in
# the word list (in the file 'word_list.txt') within the puzzle.
# Remember, the words may be hidden left to right, right to left,
# up, down or diagonally."

# The word_search_solver.py was written first.
# This is my attempt to implement the "simpler" version
# that doesn't preload the key list into a graph.


# Directions are stored as (dy, dx) tuples in a class attribute.
# They represent the change (ie delta, or d) in y and x coordinates
# as the solver attempts to construct paths between nodes in the graph.
DIRECTIONS = {
    'LR':  (0,   1),  # Left to right
    'RL':  (0,  -1),  # Right to left
    'U':   (-1,  0),  # Up
    'D':   (1,   0),  # Down
    'DUL': (-1, -1),  # Diagonal up left
    'DUR': (-1,  1),  # Diagonal up right
    'DDL': (1,  -1),  # Diagonal down left
    'DDR': (1,   1)   # Diagonal down right
}


def solve_puzzle(words, graph):

    # Naively assume the graph is a rectangle:
    graph_height = len(graph)    # y axis
    graph_width = len(graph[0])  # x axis

    results = {}

    # The following nasty five-level for loop nesting
    # exists because I didn't want to spend much time on
    # the counterexample to my main demonstration program.
    # Sorry about that.
    for each_word in words:

        each_word_upper = each_word.upper()

        for each_row_index in range(graph_height):

            for each_column_index in range(graph_width):

                for each_direction in DIRECTIONS:
                    # Must reset the tracking index to copies
                    # of the current tile's coordinates at
                    # every new direction checked.
                    this_step_y = each_row_index
                    this_step_x = each_column_index

                    word_is_not_here = False

                    for index, each_letter in enumerate(each_word_upper):

                        # Splitting up the failure case for readability.
                        bottom = (this_step_y >= graph_height)
                        top = (this_step_y < 0)
                        right = (this_step_x >= graph_width)
                        left = (this_step_x < 0)

                        # If ANY of these conditions are true, the step
                        # is out_of_bounds. The OR comparison ensures it.
                        out_of_bounds = (bottom or right or left or top)

                        # # Out-of-bounds checking first, so nothing is raised.
                        # if ((this_step_y >= graph_height) or
                        #    (this_step_y < 0) or
                        #    (this_step_x >= graph_width) or
                        #    (this_step_x < 0)):
                        #     continue
                        if out_of_bounds:
                            word_is_not_here = True

                        # A space isn't a letter.
                        # While there are some "words" with spaces
                        # in them in the WordList.txt file, there
                        # are none in the WordSearch.txt file.
                        # This program will assume words with spaces in
                        # the WordList.txt file are included in the
                        # WordSearch.txt file with spaces removed.
                        elif each_letter == ' ':
                            continue

                        elif graph[this_step_y][this_step_x] == each_letter:

                            # At the first step it checks the current tile
                            # against the current letter. On subsequent steps
                            # it properly applies the directional offset.
                            this_step_y += DIRECTIONS[each_direction][0]
                            this_step_x += DIRECTIONS[each_direction][1]

                        else:
                            word_is_not_here = True

                    if word_is_not_here is False:

                        # The (x, y) ordering is intentional for readability.
                        coords = (each_column_index, each_row_index)

                        try:
                            results[each_word][each_direction].append(coords)

                        except KeyError:
                            results[each_word] = {each_direction: [coords]}

        if each_word not in results:
            results[each_word] = {}

    return results


def load_list_from_text_file(file_name):
    '''
    Load file_name and return a list containing all lines from it.
    '''

    with open(file_name) as opened_file:
        lines = opened_file.read().splitlines()

    return lines


def write_solution_to_file(results, solution_file_path):
    '''
    Write the results of calling solve_puzzle
    to a text file, with pretty printing.
    '''

    explanation = ('\nFormat of this file:'
                   '\n\nEach word found:'
                   '\n    Each direction the word was found in:'
                   '\n        (X, Y) coordinates of first letter in the word.'
                   '\n\n')

    with open(solution_file_path, 'w+') as solution_file:

        solution_file.write(explanation)

        sorted_keys = sorted(results)

        for each_key in sorted_keys:

            solution_file.write('\n\n{}:'.format(each_key))

            if not results[each_key]:
                    solution_file.write('\n    Not found.'.format(each_key))

            for each_direction in results[each_key].keys():

                solution_file.write('\n    {}:'.format(each_direction))

                for each_result in results[each_key][each_direction]:

                    x = each_result[0]
                    y = each_result[1]

                    solution_file.write('\n        ({}, {})'.format(x, y))

        solution_file.write('\n')


if __name__ == '__main__':

    words = load_list_from_text_file('word_list.txt')
    graph = load_list_from_text_file('word_search.txt')

    results = solve_puzzle(words, graph)

    # Uncomment for verbose terminal output.
    # for each_key, each_value in sorted(results.iteritems()):
    #     print('{}: {}'.format(each_key, each_value))

    write_solution_to_file(results, 'simple_solution.txt')

    print("\nsimple_solution.txt file written."
          "\nAttempting to check simple_solution.txt"
          " against fancy_solution.txt . . .")

    try:

        loaded_simple_solution = load_list_from_text_file('fancy_solution.txt')
        loaded_fancy_solution = load_list_from_text_file('simple_solution.txt')

        assert loaded_simple_solution == loaded_fancy_solution

        print("The files simple_solution.txt and"
              " fancy_solution.txt have identical contents.")

    except:
        # The error names for determining whether or not
        # the file was found are are different in Py2 and Py3.
        # This call to sys.exc_info will print the error
        # raised regardless of what type it is.
        import sys
        error = sys.exc_info()

        # Specific cases before general cases.
        if isinstance(error[1], AssertionError):
            print("{}".format(str(error)))  # error[1] would print None here.
            print("Use diff to compare the file differences.")
        else:
            print("{}".format(error[1]))
            print("To compare results, run word_search_solver.py.")
