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
# License along with Fortrify.  If not, see
# <https://www.gnu.org/licenses/>.
#

"""Tests that the grammar can correctly parse a main program.

"""


# def test_empty_program(fortran_parser):
#     """Test parsing of the smallest possible Fortran program.
# 
#     """
#     tree = fortran_parser.parse("end\n")
#     program = tree.children[0]
#     assert program.data == "main_program"
#     assert program.children[0].data == "end_program_stmt"
#     assert len(program.children[0].children) == 0
# 
# 
# def test_begin_end_named_program(fortran_parser):
#     """Test parsing a named, empty program.
# 
#     """
#     tree = fortran_parser.parse("""program test
#                                    end program test
#                                 """)
#     program = tree.children[0]
#     assert program.data == "main_program"
#     assert program.children[0].data == "program_stmt"
#     assert program.children[0].children[0] == "test"
#     assert program.children[1].data == "end_program_stmt"
#     assert program.children[1].children[0] == "test"
# 
# 
# def test_begin_end_unnamed_program(fortran_parser):
#     """Test parsing a named, empty program where the END PROGRAM statement
# does not include the program name.
# 
#     """
#     tree = fortran_parser.parse("""program test
#                                    end program
#                                 """)
#     program = tree.children[0]
#     assert program.data == "main_program"
#     assert program.children[0].data == "program_stmt"
#     assert program.children[0].children[0] == "test"
#     assert program.children[1].data == "end_program_stmt"
#     assert len(program.children[1].children) == 0

import hypothesis
import lark

import code_generators


@hypothesis.given(code_generators.empty_programs())
def test_empty_program(fortran_parser, empty_program):
    tree = fortran_parser.parse(str(empty_program))
    empty_program.assert_equivalent(tree)
