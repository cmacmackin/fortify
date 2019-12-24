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

from hypothesis import strategies as st, assume

INTRINSICS = ['abort','abs','abstract','access','achar','acos','acosh','adjustl',
              'adjustr','aimag','aint','alarm','all','allocatable','allocate',
              'allocated','and','anint','any','asin','asinh','assign','associate',
              'associated','asynchronous','atan','atan2','atanh','atomic_add',
              'atomic_and','atomic_cas','atomic_define','atomic_fetch_add',
              'atomic_fetch_and','atomic_fetch_or','atomic_fetch_xor','atomic_or',
              'atomic_ref','atomic_xor','backtrace','backspace','bessel_j0',
              'bessel_j1','bessel_jn','bessel_y0','bessel_y1','bessel_yn','bge',
              'bgt','bind','bit_size','ble','blt','btest',
              'c_associated','c_f_pointer','c_f_procpointer','c_funloc','c_loc',
              'c_sizeof','cabs','cdabs','ceiling',
              'char','chdir','chmod','cmplx',
              'co_broadcast','co_max','co_min','co_reduce','co_sum',
              'command_argument_count','compiler_options',
              'compiler_version','complex','conjg',
              'cos','cosh','count','cpu_time',
              'cshift','ctime','dabs','date_and_time','dble',
              'dcmplx','digits','dim',
              'dlog','dlog10','dmax1','dmin1',
              'dot_product','dprod','dreal','dshiftl','dshiftr',
              'dsqrt','dtime',
              'eoshift','epsilon',
              'equivalence','erf','erfc','erfc_scaled','etime',
              'execute_command_line','exp','exponent',
              'extends_type_of','external','fget','fgetc','findloc',
              'fdate','floor','flush','fnum','fput','fputc',
              'fraction','free','fseek','fstat','ftell','gamma',
              'gerror','getarg','get_command','get_command_argument',
              'getcwd','getenv','get_environment_variable','getgid',
              'getlog','getpid','getuid','gmtime','hostnm','huge','hypot','iabs',
              'iachar','iall','iand','iany','iargc','ibclr','ibits','ibset','ichar',
              'idate','ieee_class','ieee_copy_sign','ieee_get_flag',
              'ieee_get_halting_mode','ieee_get_rounding_mode','ieee_get_status',
              'ieee_get_underflow_mode','ieee_is_finite','ieee_is_nan',
              'ieee_is_negative','ieee_is_normal','ieee_logb','ieee_next_after',
              'ieee_rem','ieee_rint','ieee_scalb','ieee_selected_real_kind',
              'ieee_set_flag','ieee_set_halting_mode','ieee_set_rounding_mode',
              'ieee_set_status','ieee_support_datatype','ieee_support_denormal',
              'ieee_support_divide','ieee_support_flag','ieee_support_halting',
              'ieee_support_inf','ieee_support_io','ieee_support_nan',
              'ieee_support_rounding','ieee_support_sqrt','ieee_support_standard',
              'ieee_support_underflow_control','ieee_unordered','ieee_value',
              'ieor','ierrno','imag','image_index','index','int',
              'int2','int8','ior','iparity',
              'irand','is_contiguous','is_iostat_end','is_iostat_eor',
              'isatty','ishft','ishftc','isnan','itime','kill','lbound',
              'lcobound','leadz','len','len_trim','lge','lgt','link','lle','llt',
              'lock','lnblnk','loc','log','log_gamma','log10','logical','long',
              'lshift','lstat','ltime','malloc','maskl','maskr','matmul','max',
              'max0','maxexponent','maxloc','maxval','mclock','mclock8','merge',
              'merge_bits','min','min0','minexponent','minloc','minval','mod',
              'modulo','move_alloc','mvbits',
              'nearest','new_line','nint','norm2',
              'null','num_images',
              'pack','parity'
              'perror','popcnt','poppar',
              'product','radix',
              'ran','rand','random_number','random_seed','range','rank',
              'real','rename','repeat','reshape',
              'rrspacing','rshift','same_type_as',
              'scale','scan','secnds','second',
              'selected_char_kind','selected_int_kind','selected_real_kind',
              'set_exponent','shape','shifta','shiftl','shiftr','sign',
              'signal','sin','sinh','size','sizeof','sleep','spacing','spread',
              'sqrt','srand','stat','stop','storage_size',
              'sum','symlnk','system',
              'system_clock','tan','tanh','this_image','time',
              'time8','tiny','trailz','transfer','transpose','trim','ttynam',
              'type_as','ubound','ucobound','umask','unlock','unlink',
              'unpack','verify','volatile','xor','zabs']


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
def fortran_labels(draw):
    """Returns a valid line label."""
    return draw(st.text(digits(), 1, 5))


@case_insensitive_result
@st.composite
def fortran_operators(draw, name):
    """Places name in between two dots."""
    return "."+draw(inline_whitespace())+name+draw(inline_whitespace())+"."


@st.composite
def digit_strings(draw):
    """Returns a digit string (unsigned integer) literal."""
    return draw(st.text(digits(), 1))


@st.composite
def signs(draw):
    """Returns a positive or negative sign."""
    return draw(st.sampled_from(("+", "-")))


@st.composite
def significands(draw):
    """Returns significands for real literals."""
    if (draw(st.booleans())):
        sig = draw(digit_strings()) + draw(inline_whitespace()) + "."
        if (draw(st.booleans())):
            sig += draw(inline_whitespace()) + draw(digit_strings())
    else:
        sig = "." + draw(inline_whitespace()) + draw(digit_strings())
    return sig


@st.composite
def exponent_letters(draw):
    """Returns exponent letters for real literals."""
    return draw(st.sampled_from(("D", "d", "E", "e")))


@st.composite
def kind_params(draw):
    """Returns a valid kind parameter in Fortran."""
    return draw(st.one_of(fortran_names(), digit_strings()))


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


@case_insensitive_result
@st.composite
def module_nature(draw):
    """Returns INTRINSIC or NON_INTRINSICT attribute."""
    return draw(st.sampled_from(("intrinsic", "non_intrinsic")))


# Define Hypothesis strategies for generating different types of
# statements and constructs in Fortran code.

@statement
@st.composite
def program_stmts(draw, names=fortran_names()):
    return ParseNode("program_stmt", [draw(names)],
                     [draw(case_insensitive("program ")), ""])


@statement
@st.composite
def end_program_stmts(draw, names=fortran_names()):
    has_program = draw(st.booleans())
    filler = draw(case_insensitive("end" +
                                   (" program" if has_program else "")))
    has_name = has_program and draw(st.booleans())
    if has_name:
        return ParseNode("end_program_stmt", [draw(names)], [filler + " ", ""])
    else:
        return ParseNode("end_program_stmt", [], [filler])


@statement
@st.composite
def use_stmts(draw):
    return


# Define Hypothesis strategies to generate complete Fortran programs
# for testing purpose.

@in_source_file
@st.composite
def empty_programs(draw):
    if draw(st.booleans()):
        return ParseNode("main_program", [draw(program_stmts()),
                                          draw(end_program_stmts())],
                         ["", "", ""])
    else:
        return ParseNode("main_program", [draw(end_program_stmts())],
                         ["", ""])


#############################

@st.composite
def program_units(draw):
    return draw(st.one_of(main_programs(), external_subprograms(), modules(),
                          submodules(), block_datas()))


def main_programs(draw):
    return


@st.composite
def external_subprograms(draw):
    return draw(st.one_of(function_subprograms(), subroutine_subprograms()))


@st.composite
def function_subprograms(draw):
    return


@st.composite
def subroutine_subprograms(draw):
    return


@st.composite
def modules(draw):
    return


@st.composite
def submodules(draw):
    return


@st.composite
def block_datas(draw):
    return


################################################

@st.composite
def specification_parts(draw):
    """Returns a list of specification constructs. Does not create a
ParseNode, as there is none for specification-parts in the grammar.

    """
    children = draw(st.lists(use_stmts())) + draw(st.lists(import_stmts())) + \
               (draw(implicit_parts()) if draw(st.booleans()) else []) + \
               draw(st.lists(declaration_constructs()))
    return children


@st.composite
def implicit_parts(draw):
    """Returns a list of implicit-part constructs. Does not create a
ParseNode, as there is none for implicit-parts in the grammar.

    """
    return draw(st.lists(implicit_part_stmts())) + draw(implicit_stmts())


@st.composite
def implicit_part_stmts(draw):
    return draw(st.one_of(implicit_stmts(), parameter_stmts(), format_stmts(),
                          entry_stmts()))


@st.composite
def declaration_constructs(draw):
    return draw(st.one_of(specification_constructs(), data_stmts(),
                          format_stmts(), entry_stmts(),
                          stmt_function_stmts()))


@st.composite
def specification_constructs(draw):
    return draw(st.one_of(derived_type_defs(), enum_defs(), generic_stmts(),
                          interface_blocks(), parameter_stmts(),
                          procedure_declaration_stmts(),
                          other_specification_stmts(),
                          type_declaration_stmts()))


@statement
@st.composite
def implicit_stmts(draw):
    if draw(st.booleans()):
        children = draw(st.lists(implicit_specs(), 1))
        n = len(children) - 1
        filler = [draw(case_insensitive("implicit"))] + draw(commas(n, False))
    else:
        filler = [draw(case_insensitive("implicit none"))]
        parens = draw(st.booleans())
        if parens:
            filler.append("(")
        if parens and draw(st.booleans()):
            name_specs = draw(st.lists(implicit_name_specs(), 1))
            children.extend(name_specs)
            filler.extend(draw(commas(len(name_specs) - 1, False)))
            filler.append(")")
        else:
            filler[-1] += draw(inline_whitespace()) + ")"
    return ParseNode("implicit_stmt", children, filler)


@case_insensitive_result
@st.composite
def implicit_name_specs(draw):
    return st.sample_from(("external", "type"))


@st.composite
def implicit_specs(draw):
    children = [draw(declaration_type_specs())] + \
               draw(st.lists(letter_specs(), 1))
    filler = ["", draw(wrap_white("("))] + draw(commas(len(children) - 2))
    filler.append(draw(wrap_white(")")))
    return ParseNode("implicit_spec", children, filler)


@st.composite
def letter_specs(draw):
    filler = [""]
    children = [draw(letters())]
    if draw(st.booleans()):
        filler.append(draw(wrap_white("-")))
        children.append(draw(letters()))
    filler.append("")
    return ParseNode("letter_spec", children, filler)


def parameter_stmts():
    return


def format_stmts():
    return


def entry_stmts():
    return


def data_stmts():
    return


def stmt_function_stmts():
    return


def derived_type_defs():
    return


def enum_defs():
    return


def generic_stmts():
    return


def interface_blocks():
    return


@statement
@st.composite
def type_declaration_stmts(draw):
    children = [draw(declaration_type_specs())]
    filler = [""]
    if draw(st.booleans()):
        attrs = draw(st.lists(attr_specs()))
        filler.extend([","] * len(attrs))
        children.extend(attrs)
        filler.append("::")
    decls = draw(st.lists(entity_decls(), 1))
    children.extend(decls)
    filler.extend([","] * (len(decls) - 1))
    filler.append("")
    return


@st.composite
def attr_specs(draw):
    return draw(st.one_of(bracket_attr_specs(), paren_attr_specs(),
                          language_binding_specs(), simple_attr_specs()))


@st.composite
def bracket_attr_specs(draw):
    return ParseNode("bracket_attr_spec",
                     [draw(case_insensitive("codimension")),
                      draw(coarray_specs())],
                     ["", draw(wrap_white("[")), draw(wrap_white("]"))])


@st.composite
def paren_attr_specs(draw):
    if draw(st.booleans()):
        return ParseNode("paren_attr_spec",
                         [draw(case_insensitive("dimension")),
                          draw(array_specs())], ["", draw(wrap_white("(")),
                                                 draw(wrap_white(")"))])
    else:
        return ParseNode("paren_attr_spec",
                         [draw(case_insensitive("intent")),
                          draw(intent_specs())], ["", draw(wrap_white("(")),
                                                  draw(wrap_white(")"))])


@st.composite
def array_specs(draw):
    children = draw(st.one_of(st.lists(explicit_shape_specs(), 1),
                              st.lists(assumed_shape_specs(), 1),
                              st.lists(deferred_shape_specs(), 1),
                              assumed_size_specs(), implied_shape_specs(),
                              implied_shape_or_assumed_size_specs(),
                              assumed_rank_specs()))
    if not isinstance(children, list):
        children = [children]
    filler = [draw(inline_whitespace())] + draw(commas(len(children) - 1)) + \
             [draw(inline_whitespace())]
    return ParseNode("array_specs", children, filler)


@st.composite
def coarray_specs(draw):
    children = draw(st.one_of(st.lists(deferred_coshape_specs(), 1),
                              explicit_coshape_specs()))
    if not isinstance(children, list):
        children = [children]
    filler = commas(len(children) - 1)
    return ParseNode("coarray_spec", children, filler)


@st.composite
def deferred_coshape_specs(draw):
    return ParseNode("deferred_coshape_spec", [], [draw(wrap_white(":"))])


@st.composite
def explicit_coshape_specs(draw):
    children = []
    filler = [draw(inline_whitespace())]
    for i in range(draw(st.integers(0))):
        if draw(st.booleans()):
            children.append(draw(lower_cobounds()))
            filler.append(draw(wrap_white(":")))
        children.append(draw(upper_cobounds()))
        filler.append(draw(wrap_white(",")))
    if draw(st.booleans()):
        children.append(draw(lower_cobounds()))
        filler.append(draw(wrap_white(":")))
    filler[-1] += draw(wrap_white("*"))
    return ParseNode("explicit_coshape_spec", children, filler)


@st.composite
def explicit_shape_specs(draw):
    children = [draw(upper_bounds())]
    filler = [""]
    if draw(st.booleans()):
        children.insert(draw(lower_bounds()), 0)
        filler.append(draw(wrap_white(":")))
    filler.append("")
    return ParseNode("explicit_shape_spec", children, filler)


@st.composite
def assumed_shape_specs(draw):
    if draw(st.booleans()):
        return draw(assumed_or_deferred_shape_specs())
    else:
        return ParseNode("assumed_shape_spec", [draw(lower_bounds())],
                         ["", draw(wrap_white(":"))])


@st.composite
def assumed_or_deferred_shape_specs(draw):
    return ParseNode("assumed_or_deferred_shape_spec", [],
                     [draw(wrap_white(":"))])


deferred_shape_specs = assumed_or_deferred_shape_specs


@st.composite
def assumed_implied_specs(draw):
    filler = [""]
    children = []
    if draw(st.booleans()):
        children.append(draw(lower_bounds()))
        filler.append(draw(wrap_white(":")))
    filler[-1] += draw(wrap_white("*"))
    return ParseNode("assumed_implied_spec", children, filler)


@st.composite
def assumed_size_specs(draw):
    children = draw(st.lists(explicit_shape_specs(), 1))
    n = len(children)
    filler = [""] + draw(commas(n))
    children.append(draw(assumed_implied_specs()))
    filler.append("")
    return ParseNode("assumed_size_spec", children, filler)


@st.composite
def implied_shape_specs(draw):
    children = draw(st.lists(assumed_implied_specs(), 2))
    filler = draw(commas(len(children) - 1))
    return ParseNode("implied_shape_spec", children, filler)


implied_shape_or_assumed_size_specs = assumed_implied_specs


@st.composite
def assumed_rank_specs(draw):
    return ParseNode("assumed_rank_spec", [], [draw(wrap_white(".."))])


@case_insensitive_result
@st.composite
def intent_specs(draw):
    return draw(st.sample_from(("in", "out", "inout")))


@st.composite
def language_binding_specs(draw):
    filler = [draw(inline_whitespace()) + draw(case_insensitive("bind")) +
              draw(wrap_white("("))]
    children = [draw(case_insensitive("c"))]
    if draw(st.booleans()):
        filler.append(draw(wrap_white(",")) + draw(case_insensitive("name")) +
                      draw(wrap_white("=")))
        children.append(draw(exprs()))
    filler.append(draw(wrap_white(")")))
    return ParseNode("language_binding_spec", children, filler)


@st.composite
def simple_attr_specs(draw):
    attr = draw(st.one_of(
        st.sample_from(("allocatable", "asynchronous", "contiguous",
                        "external", "intrinsic", "optional", "parameter",
                        "pointer", "protected", "save", "target", "value",
                        "volatile")),
        access_specs()))
    attr = draw(case_insensitive(attr))
    return ParseNode("simple_attr_spec", [attr], ["", ""])


@case_insensitive_result
@st.composite
def access_specs(draw):
    return draw(st.sampled_from(("publilc", "private")))


@st.composite
def entity_decls(draw):
    children = [draw(fortran_names())]
    filler = [""]
    if draw(st.booleans()):
        filler.append(draw(wrap_white("(")))
        children.append(draw(array_specs()))
        filler.append(draw(wrap_white(")")))
    if draw(st.booleans()):
        filler.append(draw(wrap_white("[")))
        children.append(draw(coarray_specs()))
        filler.append(draw(wrap_white("]")))
    if draw(st.booleans()):
        filler.append(draw(wrap_white("*")))
        children.append(char_lengths())
        filler.append(draw(inline_whitespace()))
    if draw(st.booleans()):
        filler.append(draw(inline_whitespace()))
        children.append(draw(initializations()))
        filler.append(draw(inline_whitespace()))
    filler.append("")
    return ParseNode("entity_decl", children, filler)


@st.composite
def type_param_values(draw):
    return draw(st.one_of(scalar_int_exprs()), st.just("*"), st.just(":"))


@st.composite
def char_lengths(draw):
    if draw(st.booleans()):
        children = [draw(type_param_values())]
        filler = [draw(wrap_white("(")), draw(wrap_white(")"))]
    else:
        children = [draw(digit_strings())]
        filler = ["", ""]
    return ParseNode("char_length", children, filler)


@st.composite
def initializations(draw):
    if draw(st.booleans()):
        name = "assignment_init"
        filler = ["=" + draw(inline_whitespace())]
    else:
        name = "pointer_init"
        filler = ["=>" + draw(inline_whitespace())]
    children = [draw(exprs())]
    filler.append("")
    return ParseNode(name, children, filler)


@st.composite
def other_specification_stmts(draw):
    return draw(st.one_of(access_stmts(), allocatable_stmts(),
                          asynchronous_stmts(), bind_stmts(),
                          codimension_stmts(), contiguous_stmts(),
                          dimension_stmts(), external_stmts(),
                          intent_stmts(), intrinsic_stmts(),
                          namelist_stmts(), optional_stmts(),
                          pointer_stmts(), protected_stmts(),
                          save_stmts(), target_stmts(), volatile_stmts(),
                          value_stmts(), common_stmts(), equivalence_stmts()))


def procedure_declaration_stmts():
    return


@st.composite
def internal_subprogram_parts(draw):
    contents = [draw(contains_stmts())] + \
               draw(st.lists(internal_subprograms()))
    filler = empty_filler(contents)
    return ParseNode("internal_subprogram_part", contents, filler)


@st.composite
def internal_subprograms(draw):
    return draw(st.sample_from((function_subprograms(),
                                subroutine_subprograms())))


@st.composite
def generic_spec(draw):
    return draw(st.one_of(fortran_names(), defined_operators(),
                          defined_assignments(), defined_io_generic_specs()))


#############################
# R513 - Other specification statement
#############################

@statement
@st.composite
def access_stmts(draw):
    children = [draw(access_specs())]
    filler = [""]
    ids = draw(st.lists(access_ids()))
    if len(ids) > 0 and draw(st.booleans()):
        filler.append(draw(wrap_white("::")))
    filler.extend(draw(commas(len(ids) - 1, False)))
    return ParseNode("attribute_stmt", children, filler)


@st.composite
def access_ids(draw):
    return


def simple_attribute_stmts(attribute, id_strategy):
    @st.statement
    @st.composite
    def attribute_stmts(draw):
        children = [draw(case_insensitive(attribute))] + \
                   draw(st.lists(id_strategy, 1))
        filler = [(draw(wrap_white("::")) if draw(st.booleans()) else
                   draw(inline_whitespace(1)))] + draw(commas(len(children)-2, False))
        return ParseNode("attribute_stmt", children, filler)

    return attribute_stmts


@st.composite
def allocatable_decls(draw):
    children = [draw(fortran_names())]
    filler = [""]
    if draw(st.booleans()):
        filler.append(draw(wrap_white("(")))
        children.append(draw(array_specs()))
        filler.append(draw(wrap_white(")")))
    if draw(st.booleans()):
        filler.append(draw(wrap_white("[")))
        children.append(draw(coarray_specs()))
        filler.append(draw(wrap_white("]")))
    return ParseNode("name_spec", children, filler)


object_names = fortran_names


@st.composite
def bind_or_saved_entities(draw):
    children = [draw(fortran_names())]
    if draw(st.booleans()):
        filler = ["/" + draw(inline_whitespace()),
                  draw(inline_whitespace()) + "/"]
        node_type = "old_variable_spec"
    else:
        filler = ["", ""]
        node_type = "name_spec"
    return ParseNode(node_type, children, filler)


bind_entities = bind_or_saved_entities


@st.composite
def codimension_decls(draw):
    children = [draw(fortran_names()), draw(coarray_specs())]
    filler = [draw(wrap_white("[")), draw(wrap_white("]"))]
    return ParseNode("name_spec", children, filler)


@st.composite
def array_decls(draw):
    children = [draw(fortran_names()), draw(array_specs())]
    filler = [draw(wrap_white("(")), draw(wrap_white(")"))]
    return ParseNode("name_spec", children, filler)


external_names = fortran_names
dummy_arg_names = fortran_names


@st.composite
def intrinsic_procedure_names(draw):
    return ParseNode("name_spec",
                     [draw(case_insensitive(draw(st.sampled_from(INTRINSICS))))],
                     ["", ""])


@st.composite
def pointer_decls(draw):
    children = [draw(fortran_names())]
    filler = [""]
    if draw(st.booleans()):
        filler.append(draw(wrap_white("(")))
        children.append(draw(deferred_shape_specs()))
        filler.append(draw(wrap_white(")")))
    return ParseNode("name_spec", children, filler)


entity_names = fortran_names
saved_entities = bind_or_saved_entities
target_decls = allocatable_decls


@st.composite
def equivalence_sets(draw):
    children = draw(st.lists(exprs(), 2))
    filler = [draw(wrap_white("("))] + draw(commas(len(children) - 1)) + \
             draw(wrap_white(")"))
    return ParseNode("equivalence_set", children, filler)


@st.composite
def data_stmt_sets(draw):
    children = draw(st.lists(data_stmt_objects(), 1))
    filler = [""] + draw(commas(len(children) - 1)) + [draw(wrap_white("/"))]
    values = draw(st.lists(data_stmt_values(), 1))
    filler.extend(draw(commas(len(values) - 1)))
    children.extend(values)
    filler.append(draw(wrap_white("/")))
    return ParseNode("data_stmt_set", children, filler)


@st.composite
def data_stmt_objects(draw):
    return draw(st.one_of(exprs(), data_implied_dos()))


@st.composite
def data_implied_dos(draw):
    children = draw(st.lists(data_i_do_objects(), 1))
    filler = [draw(wrap_white("("))] + draw(commas(len(children)))
    if draw(st.booleans()):
        c, f = draw(integer_type_specs())
        children.append(c)
        filler.append(f[1:-1])
        filler.append(draw(wrap_white("::")))
    children.append(draw(data_i_do_variables()))
    filler.append(draw(wrap_white("=")))
    children.append(draw(scalar_int_exprs()))
    filler.append(draw(wrap_white(",")))
    children.append(draw(scalar_int_exprs()))
    if draw(st.booleans()):
        filler.append(draw(wrap_white(",")))
        children.append(draw(scalar_int_exprs()))
    filler.append(draw(wrap_white(")")))
    return ParseNode("dat_implied_do", children, filler)


@st.composite
def data_i_do_objects(draw):
    return draw(st.one_of(primary_exprs(), data_implied_dos()))


@st.composite
def data_i_do_variables(draw):
    return draw(do_variables())


@st.composite
def data_stmt_values(draw):
    children = []
    filler = [""]
    if draw(st.booleans()):
        children.append(draw(data_stmt_repeats()))
        filler.append(draw(wrap_white("*")))
    children.append(draw(data_stmt_constants()))
    filler.append("")
    return Parseode("data_stmt_value", children, filler)


@st.composite
def data_stmt_constants(draw):
    return draw(exprs())

allocatable_stmts = simple_attribute_stmts("allocatble", allocatable_decls())
asynchronous_stmts = simple_attribute_stmts("asynchronous", object_names())


@statement
@st.composite
def bind_stmts(draw):
    children = [draw(language_binding_specs())] + draw(st.lists(bind_entities(), 1))
    filler = ["", ("::" if draw(st.booleans()) else "")] + draw(commas(len(children - 2), False))
    filler.append("")
    return ParseNode("attribute_stmt", children, filler)


codimension_stmts = simple_attribute_stmts("codimension", codimension_decls())
contiguous_stmts = simple_attribute_stmts("codimension", object_names())
dimension_stmts = simple_attribute_stmts("dimension", array_decls())
external_stmts = simple_attribute_stmts("external", external_names())


@statement
@st.composite
def intent_stmts():
    children = [draw(case_insensitive("intent")), draw(intent_specs())] + \
               draw(st.lists(dummy_arg_names()))
    filler = ["", "(", ")" + ("::" if draw(st.booleans()) else "")] + \
              draw(commas(len(children) - 2, False))
    return ParseNode("attribute_stmt", children, filler)


intrinsic_stmts = simple_attribute_stmts("intrinsic",
                                         intrinsic_procedure_names())


@statement
@st.composite
def namelist_stmts(draw):
    children = []
    filler = [draw(case_insensitive("namelist /"))]
    n = range(draw(st.integers(1)))
    for i in n:
        children.append(draw(fortran_names()))
        fill.append("/")
        varnames = draw(st.lists(fortran_names()))
        children.extend(varnames)
        filler.extend(draw(commas(len(varnames)-1, False)))
        if i != n and draw(st.booleans()):
            filler.append(",")
        else:
            filler.append(inline_whitespace())
    return ParseNode("namelist_stmt", children, filler)


optional_stmts = simple_attribute_stmts("optional", dummy_arg_names())
pointer_stmts = simple_attribute_stmts("pointer", pointer_decls())
protected_stmts = simple_attribute_stmts("protected", entity_names())


@statement
@st.composite
def save_stmts():
    children = draw(st.lists(saved_entities()))
    filler = [draw(case_insensitive("save"))] + draw(commas(len(children) - 1)) + [""]
    if len(children) > 0 and draw(st.booleans()):
        filler[0] += draw(inline_whitespace(0, 1)) + "::"
    return ParseNode("attr_stmt", children, filler)


target_stmts = simple_attribute_stmts("target", target_decls())
value_stmts = simple_attribute_stmts("value", dummy_arg_names())
volatile_stmts = simple_attribute_stmts("volatiles", object_names())


@statement
@st.composite
def common_stmts():
    children = []
    filler = [draw(case_insensitive("common"))]
    n = draw(st.integers(1))
    for i in range(n):
        if i > 0 and draw(st.booleans()):
            filler[-1] += draw(inline_whitespace(0, 1)) + ","
        slashes = i > 1 or draw(st.booleans())
        if slashes:
            filler[-1] += draw(inline_whitespace(0, 1)) + "/"
        if draw(st.booleans()):
            children.append(draw(fortran_names()))
            if slashes:
                filler.append("/")
        elif slashes:
            filler[-1] += draw(inline_whitespace(0, 1)) + "/"
        block_contents = st.lists(primary_exprs(), 1)
        filler.extend(draw(commas(len(block_contents) - 1, False)))
        children.extend(block_contents())
        filler.append("")
    return ParseNode("common_stmt", children, filler)


@statement
@st.composite
def equivalence_stmts(draw):
    children = draw(st.lists(equivalence_sets(), 1))
    filler = [draw(case_insensitive("equivalence"))] + \
             draw(commas(len(children) - 1)) + [""]
    return ParseNode("equivalence_stmt", children, filler)


@statement
@st.composite
def data_stmts(draw):
    children = draw(st.lists(data_stmt_sets(), 1))
    filler = [draw(case_insensitive("data"))] + \
             draw(commas(len(children) - 1)) + [""]
    return ParseNode("data_stmt", children, filler)


#############################
@st.composite
def executable_constructs(draw):
    return draw(st.one_of(action_stmts(), associate_constructs(),
                          block_constructs(), case_constructs(),
                          change_team_constructs(),
                          critical_constructs(), do_constructs(),
                          if_constructs(), select_rank_constructs(),
                          select_type_constructs(),
                          where_constructs(), forall_constructs()))


@st.composite
def action_stmts(draw):
    return draw(st.one_of(allocate_stmts(), assignment_stmts,
                          backspace_stmts(), call_stmts(),
                          close_stmts(), continue_stmts(),
                          cycle_stmts(), deallocate_stmts(),
                          endfile_stmts(), error_stop_stmts(),
                          event_post_stmts(), event_wait_stmts(),
                          exit_stmts(), fail_image_stmts(),
                          flush_stmts(), form_team_stmts(),
                          goto_stmts(), if_stmts(), inquire_stmts(),
                          lock_stmts(), nullify_stmts(), open_stmts(),
                          pointer_assignment_stmts(), print_stmts(),
                          read_stmts(), return_stmts(),
                          rewind_stmts(), stop_stmts(),
                          sync_all_stmts(), sync_images_stmts(),
                          sync_memory_stmts(), sync_team_stmts(),
                          unlock_stmts(), wait_stmts(), where_stmts(),
                          write_stmts(), computed_goto_stmts(),
                          forall_stmts()))


def associate_construct():
    return


def block_construct():
    return


def case_construct():
    return


def change_team_construct():
    return


def critical_construct():
    return


def do_construct():
    return


def if_construct():
    return


def select_rank_construct():
    return


def select_type_construct():
    return


def where_construct():
    return


def forall_construct():
    return


#############################
# R515 - Action statement
#############################

@statement
@st.composite
def allocate_stmts():
    return


@statement
@st.composite
def assignment_stmts():
    return ParseNode("assignment_stmt", [draw(exprs()), draw(exprs())],
                     ["", "=", ""])


@statement
@st.composite
def backspace_stmts():
    return


@statement
@st.composite
def call_stmts():
    return


@statement
@st.composite
def close_stmts():
    return


@statement
@st.composite
def continue_stmts():
    return


@statement
@st.composite
def cycle_stmts():
    return


@statement
@st.composite
def deallocate_stmts():
    return


@statement
@st.composite
def endfile_stmts():
    return


@statement
@st.composite
def error_stop_stmts():
    return


@statement
@st.composite
def event_post_stmts():
    return


@statement
@st.composite
def event_wait_stmts():
    return


@statement
@st.composite
def exit_stmts():
    return


@statement
@st.composite
def fail_image_stmts():
    return


@statement
@st.composite
def flush_stmts():
    return


@statement
@st.composite
def form_team_stmts():
    return


@statement
@st.composite
def goto_stmts():
    return


@statement
@st.composite
def if_stmts():
    return


@statement
@st.composite
def inquire_stmts():
    return


@statement
@st.composite
def lock_stmts():
    return


@statement
@st.composite
def nullify_stmts():
    return


@statement
@st.composite
def open_stmts():
    return


@statement
@st.composite
def pointer_assignment_stmts():
    return


@statement
@st.composite
def print_stmts():
    return


@statement
@st.composite
def read_stmts():
    return


@statement
@st.composite
def return_stmts():
    return


@statement
@st.composite
def rewind_stmts():
    return


@statement
@st.composite
def stop_stmts():
    return


@statement
@st.composite
def sync_all_stmts():
    return


@statement
@st.composite
def sync_images_stmts():
    return


@statement
@st.composite
def sync_memory_stmts():
    return


@statement
@st.composite
def sync_team_stmts():
    return


@statement
@st.composite
def unlock_stmts():
    return


@statement
@st.composite
def wait_stmts():
    return


@statement
@st.composite
def where_stmts():
    return


@statement
@st.composite
def write_stmts():
    return


@statement
@st.composite
def computed_goto_stmts():
    return


@statement
@st.composite
def forall_stmts():
    return


###############################################################

@st.composite
def constants(draw):
    return draw(st.one_of(literal_constants(), named_constants()))


@st.composite
def literal_constants(draw):
    return draw(st.one_of(int_literal_constants(), real_literal_constants(),
                          complex_literal_constants(),
                          logical_literal_constants, char_literal_constants,
                          boz_literal_constants()))


named_constants = fortran_names


@st.composite
def signed_digit_strings(draw):
    """Returns a signed digit string (integer) literal."""
    children = [draw(digit_strings())]
    filler = ["", ""]
    if draw(st.booleans()):
        children.insert(0, draw(signs()))
        filler.append("")
    return ParseNode("signed_digit_string", children, filler)


@st.composite
def int_literal_constants(draw):
    contents = [draw(digit_strings())]
    filler = ["", ""]
    if draw(st.booleans()):
        contents.extend(["_", draw(kind_params())])
        filler.extend(["", ""])
    return ParseNode("int_literal_constant", contents, filler)


@st.composite
def signed_int_literal_constants(draw):
    return ParseNode("signed_int_literal_constant",
                     [draw(signs()), draw(int_literal_constants())],
                     ["", "", ""])


@st.composite
def real_literal_constants(draw):
    if draw(st.booleans()):
        children = [draw(significands())]
        filler = ["", ""]
        if (draw(st.booleans())):
            children.extend([draw(exponent_letters()),
                             draw(signed_digit_strings())])
            filler.extend(["", ""])
    else:
        children = [draw(digit_strings()), draw(exponent_letters()),
                    draw(signed_digit_strings())]
        filler = ["", "", "", ""]
    if draw(st.booleans()):
        children.append("_" + draw(inline_whitespace()) + draw(kind_params()))
        filler.append("")
    return ParseNode("real_literal_constant", children, filler)


@st.composite
def signed_real_literal_constants(draw):
    return ParseNode("signed_real_literal_constant",
                     [draw(signs()), draw(real_literal_constants())],
                     ["", "", ""])


@st.composite
def complex_literal_constants(draw):
    return ParseNode("complex_literal_constant",
                     [draw(exprs()), draw(exprs())],
                     [draw(wrap_white("(")), draw(wrap_white(",")),
                      draw(wrap_white(")"))])


@st.composite
def logical_literal_constants(draw):
    children = ["." + draw(inline_whitespace()) +
                draw(case_insensitive(draw(st.sample_from(("true", "false",
                                                           "t", "f"))))) +
                + draw(inline_whitespace()) + "."]
    filler = ["", ""]
    if (st.booleans()):
        children.append("_" + draw(inline_whitespace()) + draw(kind_params()))
        filler.append("")
    return ParseNode("logical_literal_constant", children, filler)


@st.composite
def char_literal_constants(draw):
    children = []
    filler = ["", ""]
    if draw(st.booleans()):
        children.append(draw(kind_params()) + draw(inline_whitespace()) + "_")
        filler.append("")
    mark = draw(st.sample_from(("\"", "'")))
    quote = st.text(st.characters(blacklist_categories=('Cs', ),
                                  blacklist_characters=("\r", "\n")),
                    min_size=0, max_size=120),
    quote = (mark * 2).join(quote.split(mark))
    children.append(mark + quote + mark)
    return ParseNode("char_literal_constant", children, filler)


@st.composite
def binary_constants(draw):
    mark = draw(st.sample_from(("\"", "'")))
    b = draw(case_insensitive("b"))
    val = st.text(binary_digits(), min_size=1, max_size=20)
    return ParseNode("binary_constant",
                     [b + draw(inline_whitespace()) + mark +
                      draw(inline_whitespace()) + val +
                      draw(inline_whitespace()) + mark],
                     ["", ""])


@st.composite
def octal_constants(draw):
    mark = draw(st.sample_from(("\"", "'")))
    b = draw(case_insensitive("o"))
    val = st.text(octal_digits(), min_size=1, max_size=20)
    return ParseNode("octal_constant",
                     [b + draw(inline_whitespace()) + mark +
                      draw(inline_whitespace()) + val +
                      draw(inline_whitespace()) + mark],
                     ["", ""])


@st.composite
def hex_constants(draw):
    mark = draw(st.sample_from(("\"", "'")))
    b = draw(case_insensitive("h"))
    val = st.text(hex_digits(), min_size=1, max_size=20)
    return ParseNode("hex_constant",
                     [b + draw(inline_whitespace()) + mark +
                      draw(inline_whitespace()) + val +
                      draw(inline_whitespace()) + mark],
                     ["", ""])


@st.composite
def boz_literal_constants(draw):
    return draw(st.one_of(binary_constants(), octal_constants(),
                          hex_constants()))


#############################
# R608 - Intrinsic operator
#############################

@st.composite
def power_ops(draw):
    """Exponentiation operator."""
    return ParseNode("power_op", [draw(st.just("**"))],
                     ["", ""])


@st.composite
def mult_ops(draw):
    """Multiplication and division operators."""
    return ParseNode("mult_op", [draw(st.sampled_from(("*", "/")))], ["", ""])


@st.composite
def add_ops(draw):
    """Addition and subtraction operators."""
    return ParseNode("mult_op", [draw(st.sampled_from(("+", "-")))], ["", ""])


@st.composite
def concat_ops(draw):
    """Concatenation operator."""
    return ParseNode("mult_op", [draw(st.just("//"))], ["", ""])


@st.composite
def eq_ops(draw):
    """Equality operator."""
    return ParseNode("eq_op", [draw(st.one_of(fortran_operators("eq"),
                                              st.just("==")))], ["", ""])


@st.composite
def ne_ops(draw):
    """Not equals operator."""
    return ParseNode("ne_op", [draw(st.one_of(fortran_operators("ne"),
                                              st.just("/=")))], ["", ""])


@st.composite
def lt_ops(draw):
    """Less than operator."""
    return ParseNode("lt_op", [draw(st.one_of(fortran_operators("lt"),
                                              st.just("<")))], ["", ""])


@st.composite
def le_ops(draw):
    """Less than or equals operator."""
    return ParseNode("le_op", [draw(st.one_of(fortran_operators("le"),
                                              st.just("<=")))], ["", ""])


@st.composite
def gt_ops(draw):
    """Greater than operator."""
    return ParseNode("gt_op", [draw(st.one_of(fortran_operators("gt"),
                                              st.just(">")))], ["", ""])


@st.composite
def ge_ops(draw):
    """Greater than or equals operator."""
    return ParseNode("ge_op", [draw(st.one_of(fortran_operators("ge"),
                                              st.just(">=")))], ["", ""])


@st.composite
def rel_ops(draw):
    """Comparison operators."""
    return draw(st.one_of(eq_ops(), ne_ops(), lt_ops(), le_ops(), gt_ops(),
                          ge_ops()))


@st.composite
def not_ops(draw):
    """The not operator."""
    return ParseNode("not_op", [draw(fortran_operators("not"))], ["", ""])


@st.composite
def and_ops(draw):
    """The and operator."""
    return ParseNode("and_op", [draw(fortran_operators("and"))], ["", ""])


@st.composite
def or_ops(draw):
    """The or operator."""
    return ParseNode("or_op", [draw(fortran_operators("or"))], ["", ""])


@st.composite
def equiv_ops(draw):
    """Equivalent and not equivalent operators."""
    op = draw(st.sampled_from(("eqv", "neqv")))
    return ParseNode("equiv_op", [draw(fortran_operators(op))], ["", ""])


#############################
# R609 - Defined operator
#############################

@st.composite
def defined_unary_ops(draw):
    name = draw(st.text(letters(), 1, 32))
    assume(name.lower() != "not")
    assume(name.lower() != "and")
    assume(name.lower() != "or")
    assume(name.lower() != "eqv")
    assume(name.lower() != "neqv")
    assume(name.lower() != "eq")
    assume(name.lower() != "ne")
    assume(name.lower() != "le")
    assume(name.lower() != "ge")
    assume(name.lower() != "lt")
    assume(name.lower() != "gt")
    return ParseNode("defined_op", [name], ["."+draw(inline_whitespace()),
                                            draw(inline_whitespace())+"."])


@st.composite
def defined_binary_ops(draw):
    name = draw(st.text(letters(), 1, 32))
    assume(name.lower() != "not")
    assume(name.lower() != "and")
    assume(name.lower() != "or")
    assume(name.lower() != "eqv")
    assume(name.lower() != "neqv")
    assume(name.lower() != "eq")
    assume(name.lower() != "ne")
    assume(name.lower() != "le")
    assume(name.lower() != "ge")
    assume(name.lower() != "lt")
    assume(name.lower() != "gt")
    return ParseNode("defined_op", name, ["."+draw(inline_whitespace()),
                                          draw(inline_whitespace())+"."])


@st.composite
def intrinsic_operators(draw):
    """One of the intrinsic Fortran operators."""
    return draw(st.one_of(power_ops(), mult_ops(), add_ops(), concat_ops(),
                          rel_ops(), not_ops(), and_ops(), or_ops(),
                          equiv_ops()))


@st.composite
def defined_operators(draw):
    """Generic defined operator, including extended intrinsic ones."""
    return draw(st.one_of(defined_unary_ops(), defined_binary_ops(),
                          extended_intrinsic_ops()))


extended_intrinsic_ops = intrinsic_operators


@st.composite
def defined_assignments(draw):
    return


@st.composite
def defined_io_generic_specs(draw):
    return


##################

@st.composite
def exprs(draw, allow_literals=True):
    if allow_literals and draw(st.booleans()):
        return draw(literal_constants())
    return


@st.composite
def primary_exprs(draw):
    return


@st.composite
def scalar_int_exprs(draw):
    return draw(st.one_of(exprs(False), int_literal_constants(),
                          boz_literal_constants()))


data_stmt_repeats = scalar_int_exprs


@st.composite
def lower_cobounds(draw):
    return ParseNode("lower_cobound", [draw(exprs())], ["", ""])


@st.composite
def upper_cobounds(draw):
    return ParseNode("upper_cobound", [draw(exprs())], ["", ""])


@st.composite
def lower_bounds(draw):
    return ParseNode("lower_bound", [draw(exprs())], ["", ""])


@st.composite
def upper_bounds(draw):
    return ParseNode("upper_bound", [draw(exprs())], ["", ""])


@st.composite
def strides(draw):
    return ParseNode("stride", [draw(exprs())], ["", ""])


@statement
@st.composite
def contains_stmts(draw):
    return ParseNode("contains_stmt", [],
                     [draw(case_insensitive("contains"))])


@statement
@st.composite
def import_stmts(draw):
    case = draw(st.integers(0, 3))
    if case == 0:
        filler = [draw(case_insensitive("import"))]
        children = draw(st.lists(fortran_names()))
        if len(children) > 0 and draw(st.booleans()):
            filler[0] += draw(wrap_white("::"))
        filler.extend(draw(commas(len(children) - 1, False)))
        return ParseNode("import_stmt", children, filler)
    elif case == 1:
        filler = [draw(case_insensitive("import")) + draw(wrap_white(",")) +
                  draw(case_insensitive("only")) + draw(wrap_white(":"))]
        children = draw(st.lists(fortran_names(), 1))
        filler.extend(draw(commas(len(children) - 1, False)))
        return ParseNode("import_stmt", children, filler)
    elif case == 2:
        return ParseNode("import_stmt", [],
                         [draw(case_insensitive("import")) +
                          draw(wrap_white(",")) +
                          draw(case_insensitive("none"))])
    else:
        return ParseNode("import_stmt", [],
                         [draw(case_insensitive("import")) +
                          draw(wrap_white(",")) +
                          draw(case_insensitive("all"))])


@st.composite
def declaration_type_specs(draw):
    if draw(st.booleans()):
        children, filler = draw(intrinsic_type_specs())
    else:
        children = [draw(intrinsic_type_specs())]
        filler = [""]
        if children[0].lower().startswith("char"):
            if draw(st.booleans()):
                children.append(draw(char_selectors()))
                filler.append(draw(inline_whitespace()))
        elif not children[0].lower().startswith("double"):
            if draw(st.booleans()):
                children.append(draw(kind_selectors()))
                filler.append(draw(inline_whitespace()))
    return ParseNode("declaration_type_spec", children, filler)


@case_insensitive_result
@st.composite
def intrinsic_type_specs(draw):
    """Returns one of the intrinsic variable types in Fortran."""
    return draw(st.sampled_from(("integer", "real", "double precision",
                                 "complex", "character", "logical",
                                 "double complex")))


@st.composite
def integer_type_specs(draw):
    children = [draw(case_insensitive("integer"))]
    filler = [""]
    if draw(st.booleans()):
        children.append(draw(kind_selectors()))
        filler.append(draw(inline_whitespace()))
    filler.append("")
    return children, filler


@st.composite
def kind_selectors(draw):
    children = [draw(scalar_int_exprs())]
    if draw(st.booleans()):
        filler = ["(" + draw(inline_whitespace()),
                  draw(inline_whitespace()) + ")"]
        if draw(st.booleans()):
            filler[0] += draw(case_insensitive("kind")) + draw(wrap_white("="))
    else:
        filler = ["", ""]
    return ParseNode("kind_selector", children, filler)


@st.composite
def char_selectors(draw):
    form = draw(st.integers(0, 4))
    if form != 0:
        filler = [draw(wrap_white("("))]
    elif form == 0:
        children = draw(char_lengths())
        filler = [draw(wrap_white("*")), draw(wrap_white(",")) if
                  draw(st.booleans()) else draw(inline_whitespace())]
    if form == 1:
        children = [draw(type_param_values())]
        filler[0] += draw(case_insensitive("len")) + draw(wrap_white("="))
    elif form == 2:
        children = [draw(case_insensitive("len")), draw(type_param_values()),
                    draw(case_insensitive("kind")), draw(exprs())]
        filler.append(draw(wrap_white("=")))
        filler.append(draw(wrap_white(",")))
        filler.append(draw(wrap_white("=")))
    elif form == 3:
        children = [draw(type_param_values())]
        filler.append(draw(wrap_white(",")))
        if draw(st.booleans()):
            children.append(draw(case_insensitive("kind")))
            filler.append(draw(wrap_white("=")))
        children.append(draw(exprs()))
    else:
        children = [draw(case_insensitive("kind")), draw(exprs())]
        filler.append(draw(wrap_white("=")))
        if draw(st.booleans()):
            children.extend([draw(case_insensitive("len")),
                             draw(type_param_values())])
            filler.extend([draw(wrap_white(",")), draw(wrap_white("="))])
    if form != 0:
        filler = [draw(wrap_white("("))]
    return ParseNode("char_selector", children, filler)


@st.composite
def do_variables(draw):
    return ParseNode("do_variable", [draw(fortran_names())], ["", ""])
