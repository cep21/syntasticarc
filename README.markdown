Wrapper to add arc lint support to vim.

INSTALL
=======

(1) add syntacticarc to your path.
(2) Inside vim

    :set makeprg=syntasticarc
    :set errorformat=%f:%l:%c:%t:%m

(3) Inside vim, you can now type build with

    :make

SYNTASTIC
=========

Can also support syntastic (https://github.com/scrooloose/syntastic).
Just replace syntastic/syntax_checkers/php.vim with the provided one here.
