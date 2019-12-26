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


class ParseNode(object):
    """An object corresponding to a node in a Lark parse tree, but with
    sufficient information to be able to generate the source code
    which produced that parse tree.

    """
    def __init__(self, node_type, children, filler):
        assert len(filler) == len(children) + 1
        self.node_type = node_type
        self.children = children
        self.filler = filler

    def __str__(self):
        return self.filler[0] + "".join(map(lambda t: str(t[0]) + t[1],
                                            zip(self.children,
                                                self.filler[1:])))

    def __repr__(self):
        return "ParseNode({}, {}, {})".format(repr(self.node_type),
                                              repr(self.children),
                                              repr(self.filler))

    def check_equivalent(self, lark_node):
        if self.node_type != lark_node.data:
            return False
        for my_child, lark_child in zip(self.children, lark_node.children):
            if isinstance(my_child, ParseNode):
                if not my_child.check_equivalent(lark_child):
                    return False
            else:
                if my_child != lark_child:
                    return False
        return True

    def assert_equivalent(self, lark_node):
        assert self.node_type == lark_node.data, \
            "{} != {}".format(self.node_type, lark_node.data)
        for my_child, lark_child in zip(self.children, lark_node.children):
            if isinstance(my_child, ParseNode):
                my_child.assert_equivalent(lark_child)
            else:
                assert my_child == lark_child
