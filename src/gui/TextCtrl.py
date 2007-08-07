"""\
A module that provide a styled text control that can handle Scheme syntax highlighting
and good stuff like that.

Shamelessly lifted form the wxPython demo StyledTextCtrl2 source code.
"""

import  wx
import  wx.stc  as  stc

class my_obj(object):
    kwlist = None

keyword = my_obj()
keyword.kwlist = ["and", "begin", "call-with-current-continuation", "call-with-input-file", "call-with-output-file", "case", "cond",
                  "define", "define-syntax", "delay", "do", "dynamic-wind", "else", "for-each", "if", "lambda", "let", "let*",
                  "let-syntax", "letrec", "letrec-syntax", "map", "or", "syntax-rules", ";;;", "*", "'", "*", "+", ",", ",@", "-",
                  "...", "/", ";", "<", "<=", "=", "=>", ">", ">=", "`", "abs", "acos", "angle", "append", "apply", "asin", "assoc",
                  "assq", "assv", "atan", "boolean?", "caar", "cadr", "call-with-input-file", "call-with-output-file", "call-with-values",
                  "car", "cdddar", "cddddr", "cdr", "ceiling", "char->integer", "char-alphabetic?", "char-ci<=?", "char-ci<?",
                  "char-ci=?", "char-ci>=?", "char-ci>?", "char-downcase", "char-lower-case?", "char-numeric?", "char-ready?",
                  "char-upcase", "char-upper-case?", "char-whitespace?", "char<=?", "char<?", "char=?", "char>=?", "char>?", "char?",
                  "close-input-port", "close-output-port", "complex?", "cons", "cos", "current-input-port", "current-output-port",
                  "denominator", "display", "eof-object?", "eq?", "equal?", "eqv?", "eval", "even?", "exact->inexact", "exact?", "exp",
                  "expt", "#f", "floor", "force", "gcd", "imag-part", "inexact->exact", "inexact?", "input-port?", "integer->char",
                  "integer?", "interaction-environment", "lcm", "length", "list", "list->string", "list->vector", "list-ref",
                  "list-tail", "list?", "load", "log", "magnitude", "make-polar", "make-rectangular", "make-string", "make-vector",
                  "max", "member", "memq", "memv", "min", "modulo", "negative?", "newline", "not", "null-environment", "null?",
                  "number->string", "number?", "numerator", "odd?", "open-input-file", "open-output-file", "output-port?", "pair?",
                  "peek-char", "port?", "positive?", "procedure?", "quasiquote", "quote", "quotient", "rational?", "rationalize",
                  "read", "read-char", "real-part", "real?", "remainder", "reverse", "round", "scheme-report-environment", "set!",
                  "set-car!", "set-cdr!", "sin", "sqrt", "string", "string->list", "string->number", "string->symbol", "string-append",
                  "string-ci<=?", "string-ci<?", "string-ci=?", "string-ci>=?", "string-ci>?", "string-copy", "string-fill!",
                  "string-length", "string-ref", "string-set!", "string<=?", "string<?", "string=?", "string>=?", "string>?", "string?",
                  "substring", "symbol->string", "symbol?", "#t", "tan", "transcript-off", "transcript-on", "truncate", "values",
                  "vector", "vector->list", "vector-fill!", "vector-length", "vector-ref", "vector-set!", "with-input-from-file",
                  "with-output-to-file", "write", "write-char", "zero?"]
                  
keyword.expr_list = ['*EXPR*', '*TEST*', '*SYMBOL*', '*WHEN-TRUE*', '*WHEN-FALSE*', '*FIRST*', '*SECOND*']


if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'size2': 10,
             }


#----------------------------------------------------------------------

import wx.xrc as xrc

class SchemeSTC(stc.StyledTextCtrl):
    
    def __init__(self, parent, ID, text=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetModEventMask(wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT | wx.stc.STC_PERFORMED_USER)
    
        self.SetLexer(stc.STC_LEX_LISP)
        self.SetKeyWords(0, " ".join(keyword.kwlist))
        self.SetKeyWords(1, " ".join(keyword.expr_list))

        self.SetProperty("fold", "1")
        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        #self.SetBufferedDraw(False)
        #self.SetViewEOL(True)
        #self.SetEOLMode(stc.STC_EOL_CRLF)
        #self.SetUseAntiAliasing(True)
        
        #self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        #self.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        #self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # Like a flattened tree control using circular headers and curved joins
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_CIRCLEMINUS,          "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_CIRCLEPLUS,           "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,                "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNERCURVE,         "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,         "white", "#404040")

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#000000,back:#37fdff,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        # Python styles
        # Default 
        self.StyleSetSpec(stc.STC_LISP_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comments
        self.StyleSetSpec(stc.STC_LISP_COMMENT, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number
        self.StyleSetSpec(stc.STC_LISP_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(stc.STC_LISP_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Keyword
        self.StyleSetSpec(stc.STC_LISP_KEYWORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # KeywordKW - The user defined keywords in keywordSet 1
        # we're going to use these to highlight the TPCL editor keywords such as
        # *EXPR*, *SYMBOL* and whatever else we need
        self.StyleSetSpec(stc.STC_LISP_KEYWORD_KW, "fore:#FF0000,bold,size:%(size)d" % faces)

        # Special...
        self.StyleSetSpec(stc.STC_LISP_SPECIAL, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # Identifier
        self.StyleSetSpec(stc.STC_LISP_IDENTIFIER, "fore:#007F7F,size:%(size)d" % faces)
        # Symbol
        self.StyleSetSpec(stc.STC_LISP_SYMBOL, "fore:#FF0000,bold,size:%(size)d" % faces)

        # Operators
        self.StyleSetSpec(stc.STC_LISP_OPERATOR, "bold,size:%(size)d" % faces)        
        # Identifiers
        self.StyleSetSpec(stc.STC_LISP_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comment-blocks
        self.StyleSetSpec(stc.STC_LISP_MULTI_COMMENT, "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        self.StyleSetSpec(stc.STC_LISP_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

        self.SetCaretForeground("BLUE")
        
        if text != None:
            self.SetText(text)


    def OnKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.GetKeyCode()

        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()

            # Tips
            if event.ShiftDown():
                #self.CallTipSetBackground("yellow")
                #self.CallTipShow(pos, 'lots of of text: blah, blah, blah\n\n'
                #                 'show some suff, maybe parameters..\n\n'
                #                 'fubar(param1, param2)')
                pass
            # Code completion
            else:
                kw = keyword.kwlist[:]

                kw.sort()  # Python sorts are case sensitive
                self.AutoCompSetIgnoreCase(False)  # so this needs to match

                # Images are specified with a appended "?type"
                for i in range(len(kw)):
                    if kw[i] in keyword.kwlist:
                        kw[i] = kw[i] + "?1"

                self.AutoCompShow(0, " ".join(kw))
        else:
            event.Skip()


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            #pt = self.PointFromPosition(braceOpposite)
            #self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            #print pt
            #self.Refresh(False)


    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1



    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1

        return line
