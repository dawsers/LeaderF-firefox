" ============================================================================
" File:        Firefox.vim
" Description:
" Author:      dawsers <dawsers@gmx.com>
" Website:     https://github.com/dawsers
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0
    finish
endif

exec g:Lf_py "import vim, sys, os.path"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "sys.path.insert(0, os.path.join(cwd, 'python'))"
exec g:Lf_py "from firefoxExpl import *"

function! leaderf#Firefox#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "firefoxExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "firefoxExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "firefoxExplManager.accept()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "firefoxExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "firefoxExplManager.clearSelections()"<CR>
    nnoremap <buffer> <silent> w             :exec g:Lf_py "firefoxExplManager.accept('w')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "firefoxExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> y             :exec g:Lf_py "firefoxExplManager.accept('y')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "firefoxExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "firefoxExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "firefoxExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "firefoxExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "Firefox")
        for i in g:Lf_NormalMap["Firefox"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Firefox#managerId()
    " pyxeval() has bug
    if g:Lf_PythonVersion == 2
        return pyeval("id(firefoxExplManager)")
    else
        return py3eval("id(firefoxExplManager)")
    endif
endfunction
