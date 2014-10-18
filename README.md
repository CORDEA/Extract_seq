Extract from sequences by python
===============

The repository contains a program for extracting a specific area specified by the file from multiple chromosomal sequence.

Features
---------------
* supports multi-core processing.

Use library
---------------
* xlwt (Not required)

Version (recommended)
---------------
* python 2.7.6
* xlwt 0.7.5

Change Log
---------------
* 0.1.1
    * Add extension and strand options.
        * extension
             \- Extend the specified area. (ex. 200) [default: 0]
        * strand
             \- Do not carry out reverse complement when this option is specified.
    * If the strand is negative, run the Reverse Complement by default.

* 0.1.3
    * Add extension and strand options.
        * silent
             \- Reduce the print statement when this option is specified.
    * Fixed the bug in linkFileCreate function.
