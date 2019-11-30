# Fortify

Fortify seeks to provide a set of tools for parsing Fortran code and
analysing the resulting parse-tree. It is currently still in
development and very far from complete. Tasks include:

- [x] Write a draft grammar for the parser (using
  [Lark](https://github.com/lark-parser/lark))
- [ ] Write a comprehensive set of unit tests for the parser/grammar
- [ ] Write custom lexers which can handle fixed-form code and line
  continuations mid-token in free-form code
- [ ] Write a class to represent a pre-processor
- [ ] Provide a means to map locations in the pre-processed code to
  locations in the original source file(s)
- [ ] Add some static analysis tools (call-graphs, inheritance
  hierarchies, etc.)
- [ ] Make the parse tree (and any information derived from it)
  serializable
- [ ] Add a validator for the source tree, checking it against the
  standard.

Where possible, logic will be taken from
[FORD](https://github.com/Fortran-FOSS-Programmers/ford) to implement
these features. Potential uses for this library will include

- Refactoring FORD to provide a more powerful and robust parser
- Writing an extension for
  [Sourcetrail](https://github.com/CoatiSoftware/Sourcetrail) so it
  can support Fortran
- Providing a language server for Fortran for use with IDEs and text
  editors
- Development of static analysis tools

Collaboration on this project is welcome! Once basic functionality has
been achieved and there have been a few releases I  would be looking
to move it into community-control. In the meantime, I will be acting
as the (hopefully) benevolent dictator.

When writing fortify, please keep the following the design principals
in mind:

- **Modularity:** Users should be able to utilise as many or as few
  of the Fortify features as desired, depending on what sort of
  information they need.
- **Generality:** When adding new features, they should be implemented
  in as general a way as possible. This will make it easier for others
  to use Fortify for their own purposes without requiring changes to
  the core library. Similarly, code should be portable across
  operating systems.
- **Robustness:** Wherever possible, endeavour to allow Fortify to
  provide some sort of meaningful output, even if the Fortran code it
  is analysing is invalid. As such, as few language requirements as
  possible should be enforced during parsing.
- **Reliability:** Futility will use Test Driven Development. All
  features _must_ be unit tested and these tests should be written
  immediately after the class/function interfaces have been defined
  (before they have been implemented). Pull requests will not be
  accepted if they lead to a decrease in code coverage.
- **Descriptiveness:** All classes, functions, and variables should
  have descriptive names and all code must be documented. All classes
  and functions will have docstrings. User-facing features will
  provide additional documentation/tutorials describing their use.
- **Tidiness:** All code must conform to PEP8 standards. Pull request
  will be rejected if this is not the case.
- **Freedom:** All code contributions must be under the GNU Lesser
  General Public License. This will allow Fortify to be called from
  code under other licenses, but ensures the core source code remains
  free software.

