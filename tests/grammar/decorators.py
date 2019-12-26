#
# Copyright 2019 Chris MacMackin <cmacmackin@gmail.com>
#
# This file is part of Fortify
#
# Fortify is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Fortify is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Fortify.  If not, see
# <https://www.gnu.org/licenses/>.
#

from hypothesis import strategies as st

from parse_node import ParseNode
from utils import comments, inline_whitespace, end_stmts, \
    comments_and_whitespace, case_insensitive


def empty_strings(n):
    """Returns a list of n empty strings."""
    return [""] * n


def empty_filler(children):
    """Returns an empty list of filler elements of appropriate length for
the supplied children.

    """
    return empty_strings(len(children) + 1)


# Define various decorators to perform common tasks when generating
# Fortran code (e.g., adding random comments and white space)

def with_inline_whitespace(f, min_space=0, max_space=12):
    """A decorator which inserts random ammount of inline whitespace into
a ParseNode.

    """

    @st.composite
    def inline_whitespace_strategy(draw, *args, **kwargs):
        node = draw(f(*args, **kwargs))
        node.filler = list(map(lambda f:
                               draw(inline_whitespace(min_space,
                                                      max_space)) +
                               " ".join([token +
                                         (draw(inline_whitespace(min_space,
                                                                 max_space))
                                          if token else "")
                                         for token in f.split(" ")]) +
                               draw(inline_whitespace(min_space,
                                                      max_space)),
                               node.filler))
        return node

    return inline_whitespace_strategy


def insert_line_continuation(f):
    """A decorator which will randomly insert line-continuation between
tokens in Fortran ParseNodes.

    """

    @st.composite
    def continuations_or_spaces(draw):
        if draw(st.booleans()):
            string = "&"
            if draw(st.booleans()):
                string += draw(comments())
            string += draw(st.sampled_from(("\n", "\r")))
        else:
            string = ""
        return string

    @st.composite
    def line_continuation(draw, *args, **kwargs):
        node = draw(f(*args, **kwargs))

        def insert_ampersand(string):
            if not isinstance(string, str):
                return string
            tokens = []
            is_comment = False
            for token in string.split(" "):
                is_comment = is_comment or "!" in token
                if is_comment or token.endswith("\n") or token.endswith("\r") \
                   or token.endswith(";") or token == "":
                    tokens.append(token)
                    continue
                tokens.append(token + draw(continuations_or_spaces()))
            return " ".join(tokens)

        node.filler = list(map(insert_ampersand, node.filler))
        return node

    return line_continuation


def continuation_and_whitespace(f, min_space=0, max_space=12):
    """A decorator which applies insert_line_continuation and then
with_inline_whitespace to a strategy for generating Fortran parse
nodes.

    """
    return with_inline_whitespace(insert_line_continuation(f), min_space,
                                  max_space)


def add_end_stmt(f):
    """A decorator which will add a statement-ending character if one is
not already present.

    """

    @st.composite
    def add_end(draw, *args, **kwargs):
        statement = draw(f(*args, **kwargs))
        last = statement.filler[-1]
        if not (last.endswith("\n") or last.endswith("\r") or
                last.endswith(";")):
            statement.filler[-1] = last + draw(end_stmts())
        return statement

    return add_end


def statement(f):
    """A decorator to be used on functions producing strategies for
Fortran statements. It will ensure the statement terminates
appropriately, inserts some inline whitespace, and insert a random
ammount (possibly none) of comments and whitespace before and after
it.

    """

    func = continuation_and_whitespace(add_end_stmt(f))

    @st.composite
    def add_whitespace(draw, *args, **kwargs):
        statement = draw(func(*args, **kwargs))
        statement.filler[0] = (draw(comments_and_whitespace()) +
                               draw(inline_whitespace()) +
                               statement.filler[0])
        statement.filler[-1] += draw(comments_and_whitespace())
        return statement

    return add_whitespace


def case_insensitive_result(f):
    """A decorator to be used on other strategy-producing functions which
will make them produce case-insensitive output (i.e., it will
randomise the case of any letters).

    """

    @st.composite
    def insensitive_strategy(draw, *args, **kwargs):
        string = draw(f(*args, **kwargs))
        return draw(case_insensitive(string))

    return insensitive_strategy


def in_source_file(f):
    """Decorator to place the list of program units returned by a
    function within a fortran_file node.

    """
    @st.composite
    def source_file(draw, *args, **kwargs):
        program_units = draw(f(*args, **kwargs))
        if not isinstance(program_units, list):
            program_units = [program_units]
        return ParseNode("fortran_file", program_units,
                         [""]*(len(program_units)+1))

    return source_file
