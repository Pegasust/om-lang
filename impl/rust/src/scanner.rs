use std::collections::HashSet;

use crate::{token::{Token, Coord}, error};


enum ScannerState {
    NoContext,
    Punctuation {remain: HashSet<&'static str>},
    IdOrKeyword,
    IntLiteral,
    StringLiteral
}

pub struct Scanner {
    state: ScannerState,
    // shared states,
    raw_string: String,
}

impl Scanner {
    pub fn new(s: String) -> Self {
        Self {
            raw_string: s,
            state: ScannerState::NoContext,
        }
    }
}
impl Iterator for Scanner {
    type Item=error::Result<Token>;

    fn next(&mut self) -> Option<Self::Item> {
        s.
    }
}
