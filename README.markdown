Wrapper to add arc lint support to vim.

INSTALL
=======

VIM
---

1. add syntacticarc to your path.
2. Inside vim(or just add to your vimrc)

         :set makeprg=syntasticarc
         :set errorformat=%f:%l:%c:%t:%m

3. Inside vim, you can now build and navigate errors

         :make  """ Runs lint
         :copen """ Open quickfix window
         :cf    """ Goto first lint error
         :cn    """ Goto next error

EMACS
-----

1. add syntacticarc to your emacs path
2. Inside emacs

          ESC-x compile
          syntacticarc -m

3.  Navigate compile errors with

          C-x `

For more help documents, check out the emacs help documents for
[compilation](http://www.delorie.com/gnu/docs/emacs/emacs_317.html)
and [compilation mode](http://www.delorie.com/gnu/docs/emacs/emacs_319.html)

OPTIONS
=======

You can change the arc path by setting SYNTASTIC_ARC in your env


SYNTASTIC
=========

Can also support syntastic (https://github.com/scrooloose/syntastic).
Just replace syntastic/syntax_checkers/php.vim with the provided one here.
