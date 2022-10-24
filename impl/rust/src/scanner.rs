//! Scanner for Omega language, given some string input. This is an abstraction for string iterator
//! and is intended to be used by the parser.

use crate::{error, token::Token};

pub struct Scanner {
    raw_string: String
}

impl Scanner {
    pub fn new<AnyStr: Into<String>>(s: AnyStr) -> Scanner {
        Scanner {
            raw_string: s.into()
        }
    }
}

impl IntoIterator for Scanner {
    type Item = Token;
    type IntoIter = impl Iterator<Item = Self::Item>;

    fn into_iter(self) -> Self::IntoIter {
        todo!()
    }
}

