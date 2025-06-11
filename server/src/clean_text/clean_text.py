"""
This file is still being worked on and is not currently being used in the functionality for server.py
"""

from typing import Tuple

Token = str


StringToken = str
StringPtr = int
Char = str


def get_ascii_chars(str_chunk: str) -> list[Char]:
    assert isinstance(str_chunk, str)

    return [char.lower() for char in str_chunk if char.isascii()]


def tokenize_list(char_list: list[Char]) -> list[StringToken]:

    string_token_list: list[StringToken] = list()
    char_list_pos: int = 0

    while char_list_pos < len(char_list):
        if char_list[char_list_pos].isnumeric():
            (to_append, new_pos) = handle_numeric(char_list, char_list_pos)
        elif char_list[char_list_pos].isalpha():
            (to_append, new_pos) = handle_word(char_list, char_list_pos)
        elif char_list[char_list_pos].isspace():
            (to_append, new_pos) = handle_whitespace(char_list, char_list_pos)
        else:
            (to_append, new_pos) = handle_others(char_list, char_list_pos)

        char_list_pos = new_pos
        if to_append != '':
            string_token_list.append(to_append)

    return string_token_list


def handle_numeric(char_list: list[Char], start_pos: StringPtr) -> Tuple[StringToken, StringPtr]:

    seen_period: bool = False

    for curr_pos in range(start_pos, len(char_list)):
        if char_list[curr_pos].isnumeric():
            continue
        elif char_list[curr_pos] == '.' and not seen_period and len(char_list) > curr_pos + 1 and char_list[curr_pos + 1].isnumeric():
            seen_period = True
        else:
            break

    if len(char_list) - 1 == curr_pos and char_list[curr_pos].isnumeric():

        return ''.join(char_list[start_pos:curr_pos + 1]), curr_pos + 1

    return ''.join(char_list[start_pos:curr_pos]), curr_pos


def handle_word(char_list: list[Char], start_pos: StringPtr) -> Tuple[StringToken, StringPtr]:
    for str_pos in range(start_pos, len(char_list)):
        if not char_list[str_pos].isalpha():
            break

    if len(char_list) - 1 == str_pos and char_list[str_pos].isalpha():
        return ''.join(char_list[start_pos:str_pos + 1]), str_pos + 1

    return ''.join(char_list[start_pos:str_pos]), str_pos


def handle_whitespace(char_list: list[Char], start_pos: StringPtr) -> Tuple[StringToken, StringPtr]:
    # white space priority when consecutive \n > \t >  '\v'
    # for later join, I want to remove spaces so that joining all the characters together is a lot easier via space
    # this can be easily changed by removing the if logic below that will return '' in the case of a space dominator
    # and then changing the clean_full_chunk to join by '' instead of ' '
    def get_dominator(left_whitespace: Char, right_whitespace: Char) -> Char:
        assert left_whitespace.isspace() and right_whitespace.isspace(
        ), f'{left_whitespace} or {right_whitespace} is not a space'

        match left_whitespace:
            case '\n':
                return left_whitespace
            case '\t':
                return left_whitespace if right_whitespace != '\n' else right_whitespace
            case ' ':
                return right_whitespace if right_whitespace != '\n' else left_whitespace
            case '\v':
                return right_whitespace
            case _:
                return right_whitespace

    curr_space = char_list[start_pos]
    for str_pos in range(start_pos, len(char_list)):
        if not char_list[str_pos].isspace():
            break
        else:
            curr_space = get_dominator(curr_space, char_list[str_pos])

    if curr_space == ' ':
        curr_space = ''

    if len(char_list) - 1 == str_pos and char_list[str_pos].isspace():
        str_pos += 1

    return curr_space, str_pos


def handle_others(char_list: list[Char], start_pos: StringPtr) -> Tuple[StringToken, StringPtr]:
    match char_list[start_pos]:
        case '-':
            if len(char_list) > start_pos + 1 and char_list[start_pos + 1] == '-':
                return '--', start_pos + 2
            else:
                return '-', start_pos + 1

        case _:
            return char_list[start_pos], start_pos + 1


def clean_full_chunk(str_chunk: str) -> str:
    cleaned_chunk: list[Char] = get_ascii_chars(str_chunk)
    tokenized_chunk: list[Char] = tokenize_list(cleaned_chunk)
    return ' '.join(tokenized_chunk)