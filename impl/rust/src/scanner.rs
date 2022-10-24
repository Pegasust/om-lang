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

pub fn scanner(s: String) -> impl Iterator<Item=error::Result<Token>> {
    s.split("\n").enumerate().peekable().map(|(line_idx, line)| {
        // Returns Result<Vec<Token>>. If there's something awry, the line is
        // at fault.
        // TODO: How to add a dummy variable to our filter_map?
        line.chars().enumerate().filter_map(|col_idx, chr| {
            
        })
        
    }).flatten()
}
// impl IntoIterator for Scanner {
//     type Item = Token;
//     type IntoIter = impl Iterator<Item = Self::Item>;
//
//     fn into_iter(self) -> Self::IntoIter {
//         scanner(self.raw_string)
//     }
// }

