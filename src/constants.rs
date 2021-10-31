use lazy_static::lazy_static;
use std::collections::HashMap;

//
// Types
//
pub type Board = [[isize; 8]; 8];
pub type Square = (isize, isize);
pub type Move = (Square, Square);

pub union MoveUnion {
    pub normal_move: Move,
    pub castle: Castle,
}

pub struct MoveStruct {
    pub is_castle: bool,
    pub data: MoveUnion,
}

//
// Constants
//
pub const EMPTY_SQUARE_ID: isize = 0;
pub const KING_ID: isize = 1;
pub const QUEEN_ID: isize = 2;
pub const ROOK_ID: isize = 3;
pub const BISHOP_ID: isize = 4;
pub const KNIGHT_ID: isize = 5;
pub const PAWN_ID: isize = 6;

pub const CONVERT_PAWN_TO_QUEEN_REWARD: isize = 10;
const PAWN_VALUE: isize = 1;
const KNIGHT_VALUE: isize = 3;
const BISHOP_VALUE: isize = 3;
const ROOK_VALUE: isize = 5;
const QUEEN_VALUE: isize = 10;
const KING_VALUE: isize = 0;
// const WIN_REWARD: isize = 100;
// const LOSS_REWARD: isize = -100;

const KING_DESC: &str = &"K";
const QUEEN_DESC: &str = &"Q";
const ROOK_DESC: &str = &"R";
const BISHOP_DESC: &str = &"B";
const KNIGHT_DESC: &str = &"N";
const PAWN_DESC: &str = &" ";

const CASTLE_KING_SIDE_WHITE: &str = "CASTLE_KING_SIDE_WHITE";
const CASTLE_QUEEN_SIDE_WHITE: &str = "CASTLE_QUEEN_SIDE_WHITE";
const CASTLE_KING_SIDE_BLACK: &str = "CASTLE_KING_SIDE_BLACK";
const CASTLE_QUEEN_SIDE_BLACK: &str = "CASTLE_QUEEN_SIDE_BLACK";

pub const DEFAULT_BOARD: Board = [
    [-3, -5, -4, -2, -1, -4, -5, -3],
    [-6, -6, -6, -6, -6, -6, -6, -6],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [3, 5, 4, 2, 1, 4, 5, 3],
];

//
// Structs
//
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum PieceType {
    King,
    Queen,
    Rook,
    Bishop,
    Knight,
    Pawn,
    Empty,
}

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum Color {
    White,
    Black,
}

impl Color {
    pub fn to_int(&self) -> isize {
        match self {
            Self::White => 1,
            Self::Black => -1,
        }
    }
}

#[derive(Debug)]
pub enum SquareColor {
    White,
    Black,
    None,
}

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum Castle {
    KingSideWhite,
    QueenSideWhite,
    KingSideBlack,
    QueenSideBlack,
}

impl Castle {
    pub fn to_str(&self) -> &str {
        match self {
            Castle::KingSideWhite => CASTLE_KING_SIDE_WHITE,
            Castle::QueenSideWhite => CASTLE_QUEEN_SIDE_WHITE,
            Castle::KingSideBlack => CASTLE_KING_SIDE_BLACK,
            Castle::QueenSideBlack => CASTLE_QUEEN_SIDE_BLACK,
        }
    }

    pub fn to_string(&self) -> String {
        self.to_str().to_string()
    }
}

#[derive(Debug)]
pub struct Piece<'a> {
    id: isize,
    _type: PieceType,
    color: Color,
    icon: char,
    desc: &'a str,
    value: isize,
}

pub const PIECES: [Piece; 13] = [
    Piece {
        icon: '♙',
        desc: PAWN_DESC,
        color: Color::Black,
        _type: PieceType::Pawn,
        id: -PAWN_ID,
        value: PAWN_VALUE,
    },
    Piece {
        icon: '♘',
        desc: KNIGHT_DESC,
        color: Color::Black,
        _type: PieceType::Knight,
        id: -KNIGHT_ID,
        value: KNIGHT_VALUE,
    },
    Piece {
        icon: '♗',
        desc: BISHOP_DESC,
        color: Color::Black,
        _type: PieceType::Bishop,
        id: -BISHOP_ID,
        value: BISHOP_VALUE,
    },
    Piece {
        icon: '♖',
        desc: ROOK_DESC,
        color: Color::Black,
        _type: PieceType::Rook,
        id: -ROOK_ID,
        value: ROOK_VALUE,
    },
    Piece {
        icon: '♕',
        desc: QUEEN_DESC,
        color: Color::Black,
        _type: PieceType::Queen,
        id: -QUEEN_ID,
        value: QUEEN_VALUE,
    },
    Piece {
        icon: '♔',
        desc: KING_DESC,
        color: Color::Black,
        _type: PieceType::King,
        id: -KING_ID,
        value: KING_VALUE,
    },
    Piece {
        icon: '.',
        desc: &" ",
        color: Color::White, // doesn't matter but must be set to avoid using Option<Color>
        _type: PieceType::Empty,
        id: EMPTY_SQUARE_ID,
        value: 0,
    },
    Piece {
        icon: '♚',
        desc: KING_DESC,
        color: Color::White,
        _type: PieceType::King,
        id: KING_ID,
        value: KING_VALUE,
    },
    Piece {
        icon: '♛',
        desc: QUEEN_DESC,
        color: Color::White,
        _type: PieceType::Queen,
        id: QUEEN_ID,
        value: QUEEN_VALUE,
    },
    Piece {
        icon: '♜',
        desc: ROOK_DESC,
        color: Color::White,
        _type: PieceType::Rook,
        id: ROOK_ID,
        value: ROOK_VALUE,
    },
    Piece {
        icon: '♝',
        desc: BISHOP_DESC,
        color: Color::White,
        _type: PieceType::Bishop,
        id: BISHOP_ID,
        value: BISHOP_VALUE,
    },
    Piece {
        icon: '♞',
        desc: KNIGHT_DESC,
        color: Color::White,
        _type: PieceType::Knight,
        id: KNIGHT_ID,
        value: KNIGHT_VALUE,
    },
    Piece {
        icon: '♟',
        desc: PAWN_DESC,
        color: Color::White,
        _type: PieceType::Pawn,
        id: PAWN_ID,
        value: PAWN_VALUE,
    },
];

lazy_static! {
    pub static ref ID_TO_COLOR: HashMap<isize, Color> = {
        PIECES
            .iter()
            .map(|piece| (piece.id, piece.color))
            .collect::<HashMap<_, _>>()
    };
    pub static ref ID_TO_ICON: HashMap<isize, char> = {
        PIECES
            .iter()
            .map(|piece| (piece.id, piece.icon))
            .collect::<HashMap<_, _>>()
    };
    pub static ref ID_TO_TYPE: HashMap<isize, PieceType> = {
        PIECES
            .iter()
            .map(|piece| (piece.id, piece._type))
            .collect::<HashMap<_, _>>()
    };
    pub static ref ID_TO_VALUE: HashMap<isize, isize> = {
        PIECES
            .iter()
            .map(|piece| (piece.id, piece.value))
            .collect::<HashMap<_, _>>()
    };
    pub static ref ID_TO_DESC: HashMap<isize, &'static str> = {
        PIECES
            .iter()
            .map(|piece| (piece.id, piece.desc))
            .collect::<HashMap<_, _>>()
    };
}
