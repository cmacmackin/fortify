#
# Copyright 2019 Chris MacMackin <cmacmackin@gmail.com>
#
# This file is part of Fortify
#
# Foobar is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Foobar.  If not, see
# <https://www.gnu.org/licenses/>.
#

import os

import pytest
import lark

import fortify

FORTIFY_PATH = os.path.dirname(fortify.__file__)
GRAMMAR_FILE = os.path.join(FORTIFY_PATH, "f2018-grammar.lark")


@pytest.fixture(scope="session")
def fortran_parser():
    """Fixture to dynamically generate a Fortran parser from the grammar
    file.

    """
    grammar = open(GRAMMAR_FILE, "r").read()
    return lark.Lark(grammar, parser="lalr")
