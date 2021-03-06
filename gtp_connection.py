"""
gtp_connection.py
Module for playing games of Go using GoTextProtocol

Parts of this code were originally based on the gtp module
in the Deep-Go project by Isaac Henrion and Amos Storkey
at the University of Edinburgh.
"""
import traceback
from sys import stdin, stdout, stderr
from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    PASS,
    MAXSIZE,
    coord_to_point,
)
import numpy as np
import re


class GtpConnection:
    def __init__(self, go_engine, board, debug_mode=False):
        """
        Manage a GTP connection for a Go-playing engine

        Parameters
        ----------
        go_engine:
            a program that can reply to a set of GTP commandsbelow
        board:
            Represents the current board state.
        """
        self._debug_mode = debug_mode
        self.go_engine = go_engine
        self.board = board
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "genmove": self.genmove_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "gogui-rules_legal_moves": self.gogui_rules_legal_moves_cmd,
            "gogui-rules_final_result": self.gogui_rules_final_result_cmd,
            "gogui-rules_side_to_move": self.gogui_rules_side_to_move_cmd,
            "gogui-rules_game_id": self.gogui_rules_game_id_cmd,
            "gogui-rules_board": self.gogui_rules_board_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd,
            "gogui-rules_board_size": self.gogui_rules_board_size_cmd
        }

        # used for argument checking
        # values: (required number of arguments,
        #          error message on argnum failure)
        self.argmap = {
            "boardsize": (1, "Usage: boardsize INT"),
            "komi": (1, "Usage: komi FLOAT"),
            "known_command": (1, "Usage: known_command CMD_NAME"),
            "genmove": (1, "Usage: genmove {w,b}"),
            "play": (2, "Usage: play {b,w} MOVE"),
            "legal_moves": (1, "Usage: legal_moves {w,b}"),
        }

    def write(self, data):
        stdout.write(data)

    def flush(self):
        stdout.flush()

    def start_connection(self):
        """
        Start a GTP connection.
        This function continuously monitors standard input for commands.
        """
        line = stdin.readline()
        while line:
            self.get_cmd(line)
            line = stdin.readline()

    def get_cmd(self, command):
        """
        Parse command string and execute it
        """
        if len(command.strip(" \r\t")) == 0:
            return
        if command[0] == "#":
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]
        args = elements[1:]
        if self.has_arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".format(
                    traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error("Unknown command")
            stdout.flush()

    def has_arg_error(self, cmd, argnum):
        """
        Verify the number of arguments of cmd.
        argnum is the number of parsed arguments
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg):
        """ Write msg to the debug stream """
        if self._debug_mode:
            stderr.write(msg)
            stderr.flush()

    def error(self, error_msg):
        """ Send error msg to stdout """
        stdout.write("? {}\n\n".format(error_msg))
        stdout.flush()

    def respond(self, response=""):
        """ Send response to stdout """
        stdout.write("= {}\n\n".format(response))
        stdout.flush()

    def reset(self, size):
        """
        Reset the board to empty board of given size
        """
        self.board.reset(size)

    def board2d(self):
        return str(GoBoardUtil.get_twoD_board(self.board))

    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond("2")

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the Go engine """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the  Go engine """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game with new boardsize args[0]
        """
        self.reset(int(args[0]))
        self.respond()

    def showboard_cmd(self, args):
        self.respond("\n" + self.board2d())

    def komi_cmd(self, args):
        """
        Set the engine's komi to args[0]
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if command args[0] is known to the GTP interface
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(" ".join(list(self.commands.keys())))

    """
    ==========================================================================
    Assignment 1 - game-specific commands start here
    ==========================================================================
    """
    """
    ==========================================================================
    Assignment 1 - commands we already implemented for you
    ==========================================================================
    """

    def gogui_analyze_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond("pstring/Legal Moves For ToPlay/gogui-rules_legal_moves\n"
                     "pstring/Side to Play/gogui-rules_side_to_move\n"
                     "pstring/Final Result/gogui-rules_final_result\n"
                     "pstring/Board Size/gogui-rules_board_size\n"
                     "pstring/Rules GameID/gogui-rules_game_id\n"
                     "pstring/Show Board/gogui-rules_board\n"
                     )

    def gogui_rules_game_id_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond("NoGo")

    def gogui_rules_board_size_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond(str(self.board.size))

    def gogui_rules_side_to_move_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        color = "black" if self.board.current_player == BLACK else "white"
        self.respond(color)

    def gogui_rules_board_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        size = self.board.size
        str = ''
        for row in range(size-1, -1, -1):
            start = self.board.row_start(row + 1)
            for i in range(size):
                # str += '.'
                point = self.board.board[start + i]
                if point == BLACK:
                    str += 'X'
                elif point == WHITE:
                    str += 'O'
                elif point == EMPTY:
                    str += '.'
                else:
                    assert False
            str += '\n'
        self.respond(str)

    """
    ==========================================================================
    Assignment 1 - game-specific commands you have to implement or modify
    ==========================================================================
    """

    def gogui_rules_final_result_cmd(self, args):
        """ Implement this function for Assignment 1 """
        if len(self.legal_move_helper()) == 0:
            if (self.board.current_player == 1):
                self.respond("white")
            else:
                self.respond("black")
            # self.respond(self.board.current_player)
        # self.respond(self.legal_move_helper())
        else:
            self.respond("unknown")
        return

    def capture_detection(self, point, color):
        '''
        return True if there is capture happens
        else False
        '''
        monitor_board = self.board.copy()
        empty_points_original = self.board.get_empty_points()
        monitor_board.play_move(point, color)
        monitor_points_after = monitor_board.get_empty_points()

        tmp_list_original = list(empty_points_original)
        tmp_list_monitor = list(monitor_points_after)
        tmp_list_original.remove(point)
        # tmp_list_original.sort()
        # tmp_list_monitor.sort()
        if(tmp_list_original == tmp_list_monitor):
            return False
        # if(len(empty_points_original)-1 == len(monitor_points_after)):
        #     return False
        return True

    def gogui_rules_legal_moves_cmd(self, args):
        """ Implement this function for Assignment 1 """
        all_emptys = self.board.get_empty_points()
        color = self.board.current_player
        return_list = []
        for point in all_emptys:
            legal_status = self.board.is_legal(
                point, color)

            if legal_status == True:
                if not self.capture_detection(point, color):
                    return_list.append(point)

        # format the list
        for i in range(len(return_list)):
            return_list[i] = format_point(
                point_to_coord(return_list[i], self.board.size))

        return_list.sort(key=lambda x: x[0])
        self.respond(' '.join(return_list))
        return return_list

    def legal_move_helper(self):
        all_emptys = self.board.get_empty_points()
        color = self.board.current_player
        #color = GoBoardUtil.opponent(color)
        return_list = []
        for point in all_emptys:
            legal_status = self.board.is_legal(
                point, color)

            if legal_status == True:
                if not self.capture_detection(point, color):
                    return_list.append(point)
        return return_list

    def color_checker(self, input_color):
        if(input_color != self.board.current_player):
            return False
        return True

    def coordinate_checker(self, color, point):
        row = point[0]
        column = point[1]
        if not column.isdigit():
            return False
        return True

    def occupied_checker(self, point):
        if self.board.get_color(point) != 0:
            return False
        return True

    def play_cmd(self, args):
        """
        play a move args[1] for given color args[0] in {'b','w'}
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            color = color_to_int(board_color)

            color_validity = self.color_checker(color)
            if not color_validity:
                self.respond(
                    'illegal move: "{} {}" wrong color'.format(args[0], args[1]))
                return
            # pass is not allowed
            coordinate_validity = self.coordinate_checker(args[0], args[1])
            if not coordinate_validity:
                self.respond(
                    'illegal move: "{} {}" wrong coordinate'.format(args[0], args[1]))
                return

            coord = move_to_coord(args[1], self.board.size)
            if coord:
                move = coord_to_point(coord[0], coord[1], self.board.size)
            else:
                self.respond(
                    'illegal move: "{} {}" wrong coordinate'.format(args[0], args[1]))
                return

            occupied_validity = self.occupied_checker(move)
            if not occupied_validity:
                self.respond(
                    'illegal move: "{} {}" occupied'.format(args[0], args[1]))
                return

            if self.board.check_suicide(move, color):
                self.respond(
                    'illegal move: "{} {}" suicide'.format(args[0], args[1]))
                return

            if self.capture_detection(move, self.board.current_player):
                self.respond(
                    'illegal move: "{} {}" capture'.format(args[0], args[1]))
                return

            # if not self.board.play_move(move, color):
            #     self.respond("Illegal Move: {}".format(board_move))
            #     return
            if not self.board.play_move(move, color):
                self.debug_msg(
                    "Move: {}\nBoard:\n{}\n".format(board_move, self.board2d())
                )
            self.respond()
        except Exception as e:
            self.respond("Error: {}".format(str(e)))

    def genmove_cmd(self, args):
        """ generate a move for color args[0] in {'b','w'} """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        move = self.go_engine.get_move(self.board, color)
        move_coord = point_to_coord(move, self.board.size)
        move_as_string = format_point(move_coord)
        if (color_to_int(args[0]) != self.board.current_player):
            self.respond('illegal move: "{}" wrong color'.format(args[0]))
            return
        if self.board.is_legal(move, color):
            if not self.capture_detection(move, color):
                self.board.play_move(move, color)
                self.respond(move_as_string)
            else:
                self.respond("resign")
        else:
            self.respond("Illegal move: {}".format(move_as_string))

    """
    ==========================================================================
    Assignment 1 - game-specific commands end here
    ==========================================================================
    """


def point_to_coord(point, boardsize):
    """
    Transform point given as board array index
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)


def format_point(move):
    """
    Return move coordinates as a string such as 'A1', or 'PASS'.
    """
    assert MAXSIZE <= 25
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if move == PASS:
        return "PASS"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1] + str(row)


def move_to_coord(point_str, board_size):
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return PASS
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            # raise ValueError
            return False
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            # raise ValueError
            return False
    except (IndexError, ValueError):
        # raise ValueError("invalid point: '{}'".format(s))
        return False
    if not (col <= board_size and row <= board_size):
        # raise ValueError("point off board: '{}'".format(s))
        return False
    return row, col


def color_to_int(c):
    """convert character to the appropriate integer code"""
    color_to_int = {"b": BLACK, "w": WHITE, "e": EMPTY, "BORDER": BORDER}
    return color_to_int[c]
