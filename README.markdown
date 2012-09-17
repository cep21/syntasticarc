Wrapper to add arc lint support to vim and emacs

![syntasticarc animated demo](http://i.imgur.com/mfz0h.gif)

Example view

![syntasticarc example view](http://i.imgur.com/lrmVb.png)

INSTALL
=======

VIM
---

1. add syntasticarc to your path.
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

1. add syntasticarc to your emacs path
2. Inside emacs.  Note, the '-m' produces 'make' compatible output

          ESC-x compile
          syntasticarc -m

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

Can also support syntastic for vim (https://github.com/scrooloose/syntastic).
Just replace syntastic/syntax_checkers/php.vim with the provided one here.
