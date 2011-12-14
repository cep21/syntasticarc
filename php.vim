"============================================================================
"File:        php.vim
"Description: Syntax checking plugin for syntastic.vim.  This is a near copy
"             of the original checker, but with syntacticarc support
"Maintainer:  Martin Grenfell <martin.grenfell at gmail dot com>
"Maintainer2: Jack Lindamood
"License:     This program is free software. It comes without any warranty,
"             to the extent permitted by applicable law. You can redistribute
"             it and/or modify it under the terms of the Do What The Fuck You
"             Want To Public License, Version 2, as published by Sam Hocevar.
"             See http://sam.zoy.org/wtfpl/COPYING for more details.
"
"============================================================================
if exists("loaded_php_syntax_checker")
    finish
endif
let loaded_php_syntax_checker = 1

"bail if the user doesnt have php installed
if !executable("php")
    finish
endif

"Support passing configuration directives to phpcs
if !exists("g:syntastic_phpcs_conf")
    let g:syntastic_phpcs_conf = "--standard=Zend"
endif

if !exists("g:syntastic_phpcs_disable")
    let g:syntastic_phpcs_disable = 0
endif

function! SyntaxCheckers_php_Term(item)
    let unexpected = matchstr(a:item['text'], "unexpected '[^']\\+'")
    if len(unexpected) < 1 | return '' | end
    return '\V'.split(unexpected, "'")[1]
endfunction

function! SyntaxCheckers_php_GetLocList()

    let errors = []

    let makeprg="syntasticarc ".shellescape(expand('%'))
    let errorformat='%f:%l:%c:%t:%m'
    let errors = errors + SyntasticMake({ 'makeprg': makeprg, 'errorformat': errorformat })

    call SyntasticHighlightErrors(errors, function('SyntaxCheckers_php_Term'))

    return errors
endfunction

