" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      dawsers <dawsers@gmx.com>
" Website:     https://github.com/dawsers
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

" Definition of 'arguments' is similar to
" https://github.com/Yggdroot/LeaderF/blob/master/autoload/leaderf/Any.vim#L85-L140
let s:extension = {
            \   "name": "firefox",
            \   "help": "navigate Firefox history and bookmarks",
            \   "manager_id": "leaderf#Firefox#managerId",
            \   "arguments": [
            \       {"name": ["--bookmarks"], "nargs":0},
            \       {"name": ["--history"], "nargs":0}
            \   ]
            \ }
" To make `Leaderf firefox` available
call g:LfRegisterPythonExtension(s:extension.name, s:extension)

command! -bar -nargs=0 LeaderfFirefox Leaderf firefox --bookmarks --history
command! -bar -nargs=0 LeaderfFirefoxBookmarks Leaderf firefox --bookmarks
command! -bar -nargs=0 LeaderfFirefoxHistory Leaderf firefox --history

" To be listed by :LeaderfSelf
call g:LfRegisterSelf("LeaderfFirefox", "navigate Firefox history and bookmarks")
call g:LfRegisterSelf("LeaderfFirefoxBookmarks", "navigate Firefox bookmarks")
call g:LfRegisterSelf("LeaderfFirefoxHistory", "navigate Firefox history")
