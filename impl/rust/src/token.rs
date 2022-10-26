//! Repersents the tokens of Omega language

use std::{fmt, collections::HashSet, borrow::Borrow};

use serde::{Deserialize, Serialize};

/// Represents the coordinates of a given token
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Coord {
    pub(crate) col: u32,
    pub(crate) line: u32,
}

/// Represents the type of the token
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum TokenType {
    Punctuation,
    Keyword,
    Id,
    IntLiteral,
    StringLiteral,
}

/// Struct for a specific token
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Token {
    pub(crate) kind: TokenType,
    pub(crate) string_value: String,
    pub(crate) coord: Coord,
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Token(kind={:?}, lex=\"{}\", @={:?})",
            self.kind, self.string_value, self.coord
        )
    }
}

// #[derive(Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord, Debug)]
/// Bookkeeping structure for Punctuation.
pub struct PunctuationBookkeep;
// #[derive(Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord, Debug)]
pub struct KeywordBookkeep;

impl IntoIterator for PunctuationBookkeep {
    type Item = &'static str;
    type IntoIter = std::array::IntoIter<&'static str, 26>;
    fn into_iter(self) -> Self::IntoIter {
        let array = [
            // standard (23)
            // misc
            ":", ",", "&", "[", "]", "{", "}", "(", ")", // arithmetics
            "*", "/", "%", "+", "-", "=", // bitwise
            "|", "&", // comparisons
            "<=", "<", ">", ">=", "==", "!=", // extensions
            // bitwise
            "<<", ">>", "~",
        ];
        IntoIterator::into_iter(array)
    }
}

impl IntoIterator for KeywordBookkeep {
    type Item = &'static str;
    type IntoIter = std::array::IntoIter<&'static str, 17>;

    fn into_iter(self) -> Self::IntoIter {
        let array = [
            // standard (16)
            // boolean
            "and", "or", "not", // kw-literal
            "true", "false", // operations
            "length", "call", "print", "return", // symbolic
            "var", "func", // control
            "while", "if", "else", // primitive type
            "bool", "int", // extensions
            // primitive type
            "string",
        ];
        IntoIterator::into_iter(array)
    }
}

pub(crate) trait Bookkeep: IntoIterator<Item = &'static str> + Sized {
    fn contains<'a>(self, s: &str) -> bool {
        self.into_iter().any(|elem| elem.borrow() == s)
    }
    fn match_first_char<'a>(self, s: char) -> HashSet<Self::Item> {
        self.into_iter()
            .fold(HashSet::new(), |mut so_far, bookkeep_str| {
                if bookkeep_str.chars().nth(0).unwrap() == s {
                    so_far.insert(bookkeep_str);
                }
                so_far
            })
    }
}

impl Bookkeep for PunctuationBookkeep{}
impl Bookkeep for KeywordBookkeep{}
