use pyo3::exceptions::{PyException, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

// mod constants;
use crate::constants::{Board, Castle, Color, Move};

// mod engine;
use crate::engine;
use crate::engine::State;

pub fn player_string_to_enum(player: &str) -> Color {
    let mut _player: Color = Color::White;
    match player {
        "WHITE" => {
            _player = Color::White;
        }
        "BLACK" => {
            _player = Color::Black;
        }
        _ => {
            let gil = Python::acquire_gil();
            let py = gil.python();
            println!("Invalid Color. Must be 'WHITE' or 'BLACK'");
            PyException::new_err("Invalid Color. Must be 'WHITE' or 'BLACK'").restore(py);
        }
    }
    return _player;
}

macro_rules! pydict_get_item_or_raise_pyerror {
    ($pydict:expr, $key:expr) => {
        match $pydict.get_item($key) {
            Some(res) => match res.extract() {
                Ok(val) => val,
                Err(_e) => {
                    return Err(PyErr::new::<PyValueError, _>(format!(
                        "Dict key {} invalid type",
                        stringify!($key)
                    )))
                }
            },
            None => {
                return Err(PyErr::new::<PyTypeError, _>(format!(
                    "Dict key {} must be specified",
                    stringify!($key)
                )))
            }
        };
    };
}

pub fn convert_py_state<'a>(_py: Python<'a>, state_py: &'a PyDict) -> PyResult<State> {
    let board: Board = pydict_get_item_or_raise_pyerror!(state_py, "board");
    let current_player: Color = player_string_to_enum(pydict_get_item_or_raise_pyerror!(
        state_py,
        "current_player"
    ));
    // let _current_player: Color = (current_player);
    let white_king_castle_is_possible: bool =
        pydict_get_item_or_raise_pyerror!(state_py, "white_king_castle_is_possible");
    let white_queen_castle_is_possible: bool =
        pydict_get_item_or_raise_pyerror!(state_py, "white_queen_castle_is_possible");
    let black_king_castle_is_possible: bool =
        pydict_get_item_or_raise_pyerror!(state_py, "black_king_castle_is_possible");
    let black_queen_castle_is_possible: bool =
        pydict_get_item_or_raise_pyerror!(state_py, "black_queen_castle_is_possible");
    let total_full_moves: usize = pydict_get_item_or_raise_pyerror!(state_py, "total_full_moves");
    let half_moves_since_last_capture: usize =
        pydict_get_item_or_raise_pyerror!(state_py, "half_moves_since_last_capture");

    let state = State::new(
        board,
        current_player,
        white_king_castle_is_possible,
        white_queen_castle_is_possible,
        black_king_castle_is_possible,
        black_queen_castle_is_possible,
        total_full_moves,
        half_moves_since_last_capture,
    );
    return Ok(state);
}

// PYTHON MODULE
// ---------------------------------------------------------
// ---------------------------------------------------------
#[pymodule]
pub fn gym_chess(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<ChessEngine>()?;

    // #[pyfn(m, "state_to_python_dict")]
    // pub fn state_to_python_dict_py(_py: Python, state: State) -> PyResult<&PyDict> {
    //     let dict = PyDict::new(_py);
    //     let out = state_to_python_dict(dict, state);
    //     Ok(out)
    // }

    Ok(())
}

#[pyclass]
pub struct ChessEngine {}

#[pymethods]
impl ChessEngine {
    #[new]
    fn new() -> Self {
        ChessEngine {}
    }

    fn next_state<'a>(
        &mut self,
        _py: Python<'a>,
        state_py: &'a PyDict,
        _player: &str,
        _move: &str,
    ) -> PyResult<(&'a PyDict, isize)> {
        // parse state
        let state: State = convert_py_state(_py, state_py)?;

        // parse arguments
        let player: Color = player_string_to_enum(_player);

        // next state
        let move_union = engine::convert_move_to_type(_move);
        let (mut new_state, reward) = engine::next_state(&state, player, move_union);

        // update kings under attack
        engine::update_state(&mut new_state);
        // if both kings are checked, this position is impossible => raise exception
        if new_state.white_king_is_checked == true && new_state.black_king_is_checked == true {
            println!("Both Kings are in check: this position is impossible");
            PyException::new_err("Both Kings are in check: this position is impossible")
                .restore(_py);
        }

        // return new state
        let new_state_py = PyDict::new(_py);
        new_state.to_py_object(new_state_py);
        return Ok((new_state_py, reward));
    }

    #[args(attack = false)]
    fn get_possible_moves<'a>(
        &mut self,
        _py: Python<'a>,
        state_py: &'a PyDict,
        _player: &str,
        attack: bool,
    ) -> PyResult<Vec<String>> {
        // parse state
        let state: State = convert_py_state(_py, state_py)?;

        // parse arguments
        let player: Color = player_string_to_enum(_player);

        let (moves, castle_moves): (Vec<Move>, Vec<Castle>) =
            engine::get_all_possible_moves(&state, player, attack);
        // let moves: Vec<Move> = get_possible_moves(&state, player, attack);
        // let castle_moves: Vec<Castle> = get_possible_castle_moves(&state, player, attack);

        let mut moves_str: Vec<String> = moves
            .iter()
            .map(|&x| engine::convert_move_to_string(x))
            .collect();
        let castle_moves_str: Vec<String> = castle_moves
            .iter()
            .map(|&x| engine::convert_castle_move_to_string(x))
            .collect();
        moves_str.extend(castle_moves_str);
        return Ok(moves_str);
    }

    fn get_castle_moves<'a>(
        &mut self,
        _py: Python<'a>,
        state_py: &'a PyDict,
        _player: &str,
    ) -> PyResult<Vec<String>> {
        // parse state
        let state: State = convert_py_state(_py, state_py)?;

        // parse arguments
        let player: Color = player_string_to_enum(_player);

        let castle_moves: Vec<Castle> = engine::get_possible_castle_moves(&state, player, false);
        let castle_moves_str: Vec<String> = castle_moves
            .iter()
            .map(|&x| engine::convert_castle_move_to_string(x))
            .collect();
        return Ok(castle_moves_str);
    }

    fn update_state<'a>(&mut self, _py: Python<'a>, state_py: &'a PyDict) -> PyResult<&'a PyDict> {
        // parse state
        let mut state: State = convert_py_state(_py, state_py)?;
        // update kings under attack
        engine::update_state(&mut state);
        // Python state
        let state_py = PyDict::new(_py);
        state.to_py_object(state_py);
        return Ok(state_py);
    }
}
