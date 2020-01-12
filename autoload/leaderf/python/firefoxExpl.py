#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import shutil, tempfile, sqlite3, glob, webbrowser
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *

import ptvsd
#*****************************************************
# FirefoxExplorer
#*****************************************************
class FirefoxExplorer(Explorer):
    def __init__(self):
        self._db_file = lfEval("get(g:, 'Lf_FirefoxDb', '~/.mozilla/firefox/*.default*/places.sqlite')")
        self._bookmarks_sql_query = "SELECT c.title AS Parent, a.title AS Title, b.url AS URL, DATETIME(a.dateAdded/1000000,'unixepoch') AS DateAdded FROM moz_bookmarks AS a JOIN moz_places AS b ON a.fk = b.id, moz_bookmarks AS c WHERE a.parent = c.id"
        self._history_sql_query = "SELECT b.title AS Title, b.url AS URL, DATETIME(a.visit_date/1000000,'unixepoch') AS DateAdded FROM moz_historyvisits AS a JOIN moz_places AS b ON b.id = a.place_id ORDER BY DateAdded DESC"

    def getContent(self, *args, **kwargs):
        result = []
        arguments_dict = kwargs.get("arguments", {})
        if "--bookmarks" in arguments_dict:
            result.extend(self._make_sources(self._bookmarks_sql_query,
                self._transform_bookmarks_sql_result))
        if "--history" in arguments_dict:
            result.extend(self._make_sources(self._history_sql_query,
                    self._transform_history_sql_result))

        return result

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return "Firefox"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    class temporary_copy(object):
        def __init__(self, original_path):
            self.original_path = original_path

        def __enter__(self):
            temp_dir = tempfile.gettempdir()
            base_path = os.path.basename(self.original_path)
            self.path = os.path.join(temp_dir, base_path)
            shutil.copy2(self.original_path, self.path)
            return self.path

        def __exit__(self,exc_type, exc_val, exc_tb):
            os.remove(self.path)

    def _format_field(self, field, length):
        return field.replace('\n', '').replace('\r', '').replace('\t', '').ljust(length)[0:length]

    def _transform_bookmarks_sql_result(self, cursor):
        return ["{0}  {1}\t{2}\t{3}".format(str(date)[0:10], self._format_field(str(parent), 20), self._format_field(str(title), 70), str(url)) for parent, title, url, date in cursor.fetchall()]
        
    def _transform_history_sql_result(self, cursor):
        return ["{0}\t{1}\t{2}".format(str(date)[0:10], self._format_field(str(title), 70), str(url)) for title, url, date in cursor.fetchall()]

    def _make_sources(self, sql_query, transformer):
        db_path = os.path.normpath(os.path.expandvars(os.path.expanduser(self._db_file)))
        db = glob.glob(db_path)
        if len(db) == 0:
            lfPrintError("Cannot find Firefox database in " + self._db_file)
            return []

        # Copy database to temp directory
        with FirefoxExplorer.temporary_copy(db[0]) as db_copy:
            # Call sqlite3 and return
            conn = sqlite3.connect(db_copy)
            c = conn.cursor()
            c.execute(sql_query)

            result = transformer(c)
            
            return result

        return []



#*****************************************************
# FirefoxExplManager
#*****************************************************
class FirefoxExplManager(Manager):
    def __init__(self):
        super(FirefoxExplManager, self).__init__()

    def _getExplClass(self):
        return FirefoxExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Firefox#Maps()")

    def _getTitle(self, line):
        return line.rsplit('\t', 2)[1]

    def _getUrl(self, line):
        return line.rsplit('\t', 1)[1]

    def accept(self, mode=''):
        lines = []
        if len(self._selections) > 0:
            for i in sorted(self._selections.keys()):
                lines.append(self._getInstance().buffer[i-1])
        else:
            lines.append(self._getInstance().currentLine)
        
        self._getInstance().exitBuffer()

        urls = [self._getUrl(line) for line in lines]
        if mode == 'y':
            yank = '\n'.join(urls)
            lfCmd("let @+ = '{}'".format(yank))
            return

        for i in range(len(urls)):
            url = urls[i]
            if i == 0:
                if mode == 'w':
                    webbrowser.open(url, new=1)
                else:
                    webbrowser.open(url, new=2)
            else:
                webbrowser.open(url, new=2)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0 return full line, 1 return title, 2 return url
        """
        if not line:
            return ''
        if mode == 0:
            return line
        elif mode == 1:
            # return title
            return self._getTitle(line)
        else:
            # return url
            return self._getUrl(line)

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0 return full line, 1 return title, 2 return url
        """
        if not line:
            return 0
        if mode == 0:
            return 0
        elif mode == 1:
            # return title pos
            return line.find('\t')
        else:
            # return url
            return line.rfind('\t')
        return 1

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open URL in default browser')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" s : toggle selection')
        help.append('" c : clear selections')
        help.append('" t : open selection(s) in browser tab')
        help.append('" w : open selection(s) in a new browser window')
        help.append('" y : yank selection(s) url(s)')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(FirefoxExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid =
                    matchadd(''Lf_hl_firefoxDate'', ''^[^ ]*'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid =
                    matchadd(''Lf_hl_firefoxTitle'', ''\s\zs.*\t'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid =
                    matchadd(''Lf_hl_firefoxUrl'', ''\t\zs.*\t\zs.*'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval('''matchadd('Lf_hl_firefoxDate', '^[^ ]*')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_firefoxTitle', '\s\zs.*\t')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_firefoxUrl', '\t\zs.*\t\zs.*')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(FirefoxExplManager, self)._beforeExit()

    def _previewInPopup(self, *args, **kwargs):
        return
    

#*****************************************************
# firefoxExplManager is a singleton
#*****************************************************
firefoxExplManager = FirefoxExplManager()

__all__ = ['firefoxExplManager']
