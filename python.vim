"============================================================================
"File:        python.vim
"Description: Syntax checking plugin for syntastic.vim
"
"Authors:     Martin Grenfell <martin.grenfell@gmail.com>
"             kstep <me@kstep.me>
"             Parantapa Bhattacharya <parantapa@gmail.com>
"Authors2:    Jack Lindamood
"
"============================================================================

if exists("loaded_python_syntax_checker")
    finish
endif
let loaded_python_syntax_checker = 1

if !exists('g:syntastic_python_checker_args')
    let g:syntastic_python_checker_args = ''
endif

function! SyntaxCheckers_python_Term(item)
    let unexpected = matchstr(a:item['text'], "unexpected '[^']\\+'")
    if len(unexpected) < 1 | return '' | end
    return '\V'.split(unexpected, "'")[1]
endfunction

function! SyntaxCheckers_python_GetLocList()
    let makeprg="syntasticarc ".shellescape(expand('%'))
    let errorformat='%f:%l:%c:%t:%m'
 
    let errors = SyntasticMake({ 'makeprg': makeprg, 'errorformat': errorformat })

    call SyntasticHighlightErrors(errors, function('SyntaxCheckers_python_Term'))

    return errors
endfunction
