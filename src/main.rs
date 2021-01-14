use gym_chess_rust::{example, Color, Move, MoveUnion, State, DEFAULT_BOARD, ID_TO_ICON};

fn show_moves(state: &State, moves: &[Move]) {
    for (i, _move) in moves.iter().enumerate() {
        let x = _move.0 .0 as usize;
        let y = _move.0 .1 as usize;
        let piece_id = state.board[x][y];
        let piece_icon = &ID_TO_ICON.get(&piece_id).unwrap();
        println!("{}. {} {:?} -> {:?}", i + 1, piece_icon, _move.0, _move.1);
    }
}

fn main() {
    println!("====> {:?}", gym_chess_rust::ID_TO_COLOR.get(&1));

    let king = gym_chess_rust::ID_TO_TYPE.get(&100);
    let mut is_king = false;
    match king {
        Some(gym_chess_rust::PieceType::King) => is_king = true,
        _ => (),
    }
    // if let gym_chess_rust::ID_TO_TYPE.get(&1) = king {
    //     println!("", );
    //     isKing = true;
    // }

    // let isKing = gym_chess_rust::PieceType::King == gym_chess_rust::ID_TO_TYPE.get(&1);
    println!("is_king ====> {:?}", is_king);

    println!("{:?}", DEFAULT_BOARD);

    let mut state = State::new(DEFAULT_BOARD, "WHITE", true, true, true, true);
    gym_chess_rust::render_state(&state);

    for _ in 0..2 {
        // white
        {
            let player = Color::White;
            let moves = gym_chess_rust::get_possible_moves(&state, player, false);
            show_moves(&state, &moves);
            let move_union = MoveUnion {
                normal_move: moves[16],
            };
            let new = gym_chess_rust::next_state(&state, player, move_union);
            state = new.0;
            gym_chess_rust::render_state(&state);
        }

        // black
        {
            let player = Color::Black;
            let moves = gym_chess_rust::get_possible_moves(&state, player, false);
            show_moves(&state, &moves);
            let move_union = MoveUnion {
                normal_move: moves[16],
            };
            let new = gym_chess_rust::next_state(&state, player, move_union);
            state = new.0;
            gym_chess_rust::render_state(&state);
        }
    }

    // gym_chess_rust::render_state(state);
    // let player = Color::Black;
    // let moves = gym_chess_rust::get_possible_moves(&state, player, false);

    // for (i, _move) in moves.iter().enumerate() {
    //     let x = _move.0.0 as usize;
    //     let y = _move.0.1 as usize;
    //     let piece_id = state.board[x][y];
    //     let piece_icon = &ID_TO_ICON.get(&piece_id).unwrap();
    //     println!("{}. {} {:?} -> {:?}", i+1, piece_icon, _move.0, _move.1);
    // }
}
