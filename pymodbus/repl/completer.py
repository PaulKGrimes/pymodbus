"""
Copyright (c) 2018 Riptide IO, Inc. All Rights Reserved.

"""
from __future__ import absolute_import, unicode_literals
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app
from pymodbus.repl.helper import get_commands
from pymodbus.compat import string_types


@Condition
def has_selected_completion():
    complete_state = get_app().current_buffer.complete_state
    return (complete_state is not None and
            complete_state.current_completion is not None)


style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})


class CmdCompleter(Completer):
    """Completer for haxor-news.
    :type text_utils: :class:`utils.TextUtils`
    :param text_utils: An instance of `utils.TextUtils`.
    :type fuzzy_match: bool
    :param fuzzy_match: Determines whether to use fuzzy matching.
    """

    def __init__(self, commands=None, ignore_case=True, **kwargs):
        self._commands = commands or get_commands()
        self._commands['help'] = ""
        self._command_names = self._commands.keys()
        self.ignore_case = ignore_case

    @property
    def commands(self):
        return self._commands

    @property
    def command_names(self):
        return self._commands.keys()

    def completing_command(self, words, word_before_cursor):
        """Determine if we are currently completing the hn command.
        :type words: list
        :param words: The input text broken into word tokens.
        :type word_before_cursor: str
        :param word_before_cursor: The current word before the cursor,
            which might be one or more blank spaces.
        :rtype: bool
        :return: Specifies whether we are currently completing the hn command.
        """
        if len(words) == 1 and word_before_cursor != '':
            return True
        else:
            return False

    def completing_arg(self, words, word_before_cursor):
        """Determine if we are currently completing an arg.
        :type words: list
        :param words: The input text broken into word tokens.
        :type word_before_cursor: str
        :param word_before_cursor: The current word before the cursor,
            which might be one or more blank spaces.
        :rtype: bool
        :return: Specifies whether we are currently completing an arg.
        """
        if len(words) > 1 and word_before_cursor != '':
            return True
        else:
            return False

    def arg_completions(self, words, word_before_cursor):
        """Generates arguments completions based on the input.
        :type words: list
        :param words: The input text broken into word tokens.
        :type word_before_cursor: str
        :param word_before_cursor: The current word before the cursor,
            which might be one or more blank spaces.
        :rtype: list
        :return: A list of completions.
        """
        cmd = words[0].strip()
        cmd = self._commands.get(cmd, None)
        if cmd:
            return cmd

    def _get_completions(self, word, word_before_cursor):
        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()
        return self.word_matches(word, word_before_cursor)

    def word_matches(self, word, word_before_cursor):
        """ True when the word before the cursor matches. """
        if self.ignore_case:
            word = word.lower()
        return word.startswith(word_before_cursor)

    def get_completions(self, document, complete_event):
        """Get completions for the current scope.
        :type document: :class:`prompt_toolkit.Document`
        :param document: An instance of `prompt_toolkit.Document`.
        :type _: :class:`prompt_toolkit.completion.Completion`
        :param _: (Unused).
        :rtype: generator
        :return: Yields an instance of `prompt_toolkit.completion.Completion`.
        """
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        text = document.text_before_cursor.lstrip()
        words = document.text.strip().split()
        meta = None
        commands = []
        if len(words) == 0:
            # yield commands
            pass
        if self.completing_command(words, word_before_cursor):
            commands = self._command_names
            c_meta = {k: v.help_text if not isinstance(v, string_types) else v for k, v in self._commands.items()}
            meta = lambda x: (x, c_meta.get(x, ''))
        else:
            if not list(filter(lambda cmd: any(x == cmd for x in words),
                               self._command_names)):
                # yield commands
                pass

            if ' ' in text:
                command = self.arg_completions(words, word_before_cursor)
                commands = list(command.get_completion())
                commands = list(filter(lambda cmd: not(any(cmd in x for x in words)), commands))
                meta = command.get_meta
        for a in commands:
            if self._get_completions(a, word_before_cursor):
                cmd, display_meta = meta(a) if meta else ('', '')
                yield Completion(a, -len(word_before_cursor),
                                 display_meta=display_meta)
