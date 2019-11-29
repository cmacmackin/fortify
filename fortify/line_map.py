"""Provides classes which can be used to map between lines in a piece
of preprocessed source code and the original source file(s).

"""

import copy
import re


class LineDirective(object):
    """A representation of a #line directive in source code. The location
    in the original source files is represented by `position_stack`,
    an array of (file_name, line_number) tuples with each successive
    entry representing a file which has been inserted into the
    previous one using an include statement. The line number in the
    final, amalgamated source code is given by `source_line`.

    """

    def __init__(self, source_line, position_stack):
        self.source_line = source_line
        self.position_stack = position_stack

    def map_line(self, source_line):
        """A function which takes a position in the final, amalgamated source
        code, and returns a position_stack indicating its position in
        the original source file(s).

        """
        position = copy.copy(self.position_stack[:-1])
        position_line = self.position_stack[-1][1]
        position.append((self.position_stack[-1][0],
                         source_line - self.source_line + position_line - 1))
        return position

    def __eq__(self, source_line):
        return self.source_line == source_line

    def __ge__(self, source_line):
        return self.source_line >= source_line

    def __gt__(self, source_line):
        return self.source_line > source_line

    def __le__(self, source_line):
        return self.source_line <= source_line

    def __lt__(self, source_line):
        return self.source_line < source_line

    def __ne__(self, source_line):
        return self.source_line != source_line


class PivotNode(object):
    """Nodes in a tree representing the mapping between lines in an
    original file and line numbers after running some sort of
    preprocessor.

    """

    def __init__(self, pivot, start_line, end_line, left_nodes, right_nodes):
        self.pivot = pivot
        self.start_line = start_line  # These variables (and the
                                      # assertions) are for debugging
                                      # and can be removed once I'm
                                      # confident this works properly
        self.end_line = end_line
        assert self.start_line < self.pivot
        assert self.pivot <= self.end_line
        self.left = None
        self.right = None

        if len(left_nodes) > 1:
            left_divide = len(left_nodes) // 2
            left_pivot = left_nodes[left_divide].source_line
            self.left = PivotNode(left_pivot, self.start_line, self.pivot,
                                  left_nodes[:left_divide],
                                  left_nodes[left_divide:])
        elif len(left_nodes) == 1:
            assert self.start_line == left_nodes[0].source_line
            self.left = left_nodes[0]

        if len(right_nodes) > 1:
            right_divide = len(right_nodes) // 2
            right_pivot = right_nodes[right_divide].source_line
            self.right = PivotNode(right_pivot, self.pivot, self.end_line,
                                   right_nodes[:right_divide],
                                   right_nodes[right_divide:])
        elif len(right_nodes) == 1:
            assert self.pivot == right_nodes[0].source_line
            self.right = right_nodes[0]

    def map_line(self, source_line):
        """A function which takes a position in the final, amalgamated and
        precompiled source code, and returns a position_stack
        indicating its position in the original source file(s).

        """
        assert source_line >= self.start_line
        assert source_line < self.end_line
        return (self.left.map_line(source_line) if source_line < self.pivot
                else self.right.map_line(source_line))


def create_line_map(source, filename="<anonymous>",
                    regex=r'#(?=\s*line)?\s+(\d+)\s+("[^"]+")?\s*$'):
    """Analyse the provided preprocessed source code for line directive,
    creating a tree structure which can be used to map between line
    numbers in the source code and the original source file(s) from which
    it was generated.
    """
    position_stack = []
    line_directives = []
    ex = re.compile(regex)
    lines = source.splitlines()
    if not ex.match(lines[0]):
        position_stack.push((filename, -1))
        line_directives.append(0, copy.copy(position_stack))
    for i, line in enumerate(lines):
        match = ex.match(line)
        if match:
            lineno = match.group(1)
            fname = match.group(2)
            if not fname:
                fname = position_stack[-1][0]
            for j, position in reversed(enumerate(position_stack)):
                if (fname == position[0]):
                    del position_stack[j:]
                    break
            position_stack.append((fname, lineno))
            line_directives.append(0, copy.copy(position_stack))
    pivot_index = len(line_directives)//2
    pivot = line_directives[pivot_index].source_line
    return PivotNode(pivot, line_directives[0].source_line, i,
                     line_directives[:pivot_index],
                     line_directives[pivot_index:])
