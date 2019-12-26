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


# Define Hypothesis strategies able to generate some of the terminals
# in the Fortran grammar

@st.composite
def case_insensitive(draw, string):
    """Returns the input string with cases of letters randomly changed."""
    return "".join(map(lambda c: c.lower() if draw(st.booleans()) else
                       c.upper(), string))


@st.composite
def letters(draw):
    """Produces an upper- or lower-case letter."""
    return draw(st.one_of(st.characters(min_codepoint=ord("a"),
                                        max_codepoint=ord("z")),
                          st.characters(min_codepoint=ord("A"),
                                        max_codepoint=ord("Z"))))


@st.composite
def digits(draw):
    """Produces a digit character."""
    return draw(st.characters(min_codepoint=ord("0"), max_codepoint=ord("9")))


@st.composite
def binary_digits(draw):
    """Produces a digit character corresponding to a binary digit."""
    return draw(st.characters(min_codepoint=ord("0"), max_codepoint=ord("1")))


@st.composite
def octal_digits(draw):
    """Produces a digit character corresponding to an octal digit."""
    return draw(st.characters(min_codepoint=ord("0"), max_codepoint=ord("7")))


@st.composite
def hex_digits(draw):
    """Produces a digit character corresponding to a hex digit."""
    return draw(st.one_of(st.characters(min_codepoint=ord("0"),
                                        max_codepoint=ord("9")),
                          st.characters(min_codepoint=ord("a"),
                                        max_codepoint=ord("f")),
                          st.characters(min_codepoint=ord("A"),
                                        max_codepoint=ord("F"))))


@st.composite
def alphanumerics(draw):
    """Produces anything Fortran considers an "alphanumeric": a letter,
number, or underscore.

    """
    return draw(st.one_of(letters(), digits(), st.just("_")))


@st.composite
def fortran_names(draw):
    """Returns a valid name for an entity in Fortran."""
    return (draw(st.text(letters(), 1, 1)) +
            draw(st.text(alphanumerics(), 0, 31)))


@st.composite
def wrap_white(draw, string):
    return draw(inline_whitespace()) + string + draw(inline_whitespace())


@st.composite
def commas(draw, n, wrap_white=True):
    if n < 1:
        return []
    if wrap_white:
        return draw(st.lists(wrap_white("n"), n, n))
    else:
        return [","] * n


@st.composite
def inline_whitespace(draw, min_space=0, max_space=12):
    """Returns an whitespace to place between tokens."""
    return " " * draw(st.integers(min_space, max_space))


@st.composite
def comments(draw, min_len=0, max_len=132):
    """Returns an arbitrary comment."""
    return "!" + draw(st.text(st.characters(blacklist_categories=('Cs', ),
                                            blacklist_characters=("\r", "\n",
                                                                  "!", "*",
                                                                  ">", "|")),
                              min_size=min_len, max_size=max_len))


@st.composite
def end_stmts(draw):
    """A character or comment indicating the end of a statement."""
    if draw(st.booleans()):
        return draw(comments()) + draw(st.sampled_from(("\n", "\r")))
    return draw(st.sampled_from(("\n", "\r", ";")))


@st.composite
def comments_and_whitespace(draw, min_lines=0, max_lines=4,
                            min_inline_whitespace=0, max_inline_whitespace=20):
    """Generate random lines of whitespace and comments."""
    return "".join(map(lambda tup: "".join(tup), draw(st.lists(
        st.tuples(inline_whitespace(min_inline_whitespace,
                                    max_inline_whitespace), end_stmts()),
        min_lines, max_lines))))
