//! Scanner for Omega language, given some string input. This is an abstraction for string iterator
//! and is intended to be used by the parser.

use itertools::Itertools;

use crate::{
    error::{self, InvalidCharacter, OmegaError},
    token::{Bookkeep, Coord, KeywordBookkeep, PunctuationBookkeep, Token, TokenType},
};

pub struct Scanner {
    raw_string: String,
}

impl Scanner {
    pub fn new<AnyStr: Into<String>>(s: AnyStr) -> Scanner {
        Scanner {
            raw_string: s.into(),
        }
    }
}

enum ScanningType {
    Id ,
    Int ,
    String ,
    Punctuation ,
}

struct ConcreteScannerState {
    scanning_type: ScanningType,
    str_so_far: String,
}

type ScannerState = Option<ConcreteScannerState>;

enum CharMatchState {
    Forbidden { errorContext: Option<String> },
    EndOfToken,
    Match,
}

pub fn scanner(s: String) -> impl Iterator<Item = error::Result<Token>> {
    s.split("\n")
        .enumerate()
        .peekable()
        .map(|(line_idx, line)| {
            // Returns Result<Vec<Token>>. If there's something awry, the line is
            // at fault.
            // TODO: How to add a dummy variable to our filter_map? Is iter::scan sufficient?
            line.chars().enumerate().scan(
                ScannerState::NoContext,
                move |state: &mut ScannerState,
                      (col_idx, chr)|
                      -> Option<Result<Token, OmegaError>> {
                    match state {
                        ScannerState::NoContext => {
                            match chr {
                                '"' => {
                                    *state = ScannerState::String {
                                        str_so_far: String::new(),
                                    }
                                }
                                chr if chr.is_ascii_digit() => {
                                    *state = ScannerState::Int {
                                        str_so_far: chr.to_string(),
                                    }
                                }
                                chr if chr.is_ascii_alphabetic() || chr == '_' => {
                                    *state = ScannerState::Id {
                                        str_so_far: chr.to_string(),
                                    }
                                }
                            };
                            None
                        }
                        ScannerState::String { str_so_far }
                        | ScannerState::Int { str_so_far }
                        | ScannerState::Id { str_so_far } => {
                            match state.chr_type(chr) {
                                CharMatchState::Forbidden { errorContext } => {
                                    Some(error::Result::<Token>::Err(OmegaError::InvalidCharacter(
                                        InvalidCharacter {
                                            chr,
                                            coord: Coord {
                                                col: (col_idx + 1) as u32,
                                                line: (line_idx + 1) as u32,
                                            },
                                            context: errorContext
                                                .unwrap_or("Unknown context".to_owned()),
                                        },
                                    )))
                                }
                                CharMatchState::Match => {
                                    // *str_so_far += chr.to_string();
                                    None
                                }
                                CharMatchState::EndOfToken => Some(Ok(state.construct_token(
                                    col_idx,
                                    line_idx,
                                    str_so_far.to_string(),
                                ))),
                            };
                            // *str_so_far += &chr.to_string();
                            None
                        }
                    }
                },
            )
        })
        .flatten()
}

impl ScannerState {
    fn chr_type(&self, chr: char) -> CharMatchState {
        match *self {
            Self::String { str_so_far } => match chr {
                '"' => CharMatchState::EndOfToken,
                // TODO: for now, accept everything, don't need to worry about escape sequence
                _ => CharMatchState::Match,
            },
            Self::Int { str_so_far } => match chr {
                chr if chr.is_ascii_whitespace() => CharMatchState::EndOfToken,
                chr if PunctuationBookkeep.match_first_char(chr).is_some() => {
                    CharMatchState::EndOfToken
                }
                chr if chr.is_ascii_digit() || chr == '_' => CharMatchState::Match,
                chr => CharMatchState::Forbidden {
                    errorContext: Some(format!(
                        "Unexpected character '{}' while parsing integer literal",
                        chr
                    )),
                },
            },
            Self::Id { str_so_far } => match chr {
                chr if chr.is_ascii_whitespace() => CharMatchState::EndOfToken,
                chr if PunctuationBookkeep.match_first_char(chr).is_some() => {
                    CharMatchState::EndOfToken
                }
                chr if chr.is_ascii_alphanumeric() => CharMatchState::Match,
                chr => CharMatchState::Forbidden {
                    errorContext: Some(format!("Unexpected character '{}' while parsing id", chr)),
                },
            },
            Self::NoContext => panic!("Should not call chr_type with NoContext"),
        }
    }
    // fn is_ending_chr(&self, chr: char) -> bool {
    //     match *self {
    //         Self::String { str_so_far } => chr == '"',
    //         Self::Int { str_so_far } | Self::Id { str_so_far } => chr.is_ascii_whitespace(),
    //         Self::NoContext => false,
    //     }
    // }
    // fn chr_acceptable(&self, chr: char) -> bool {
    //     match *self {
    //         // TODO: for now, accept everything, don't need to worry about escape sequence
    //         Self::String { str_so_far } => true,
    //         Self::Int { str_so_far } => chr.is_ascii_digit() || chr == '_',
    //         Self::Id { str_so_far } => true,
    //         Self::NoContext => panic!("chr_acceptable should not be called with NoContext"),
    //     }
    // }
    fn construct_token(&self, col_idx: usize, line_idx: usize, string_value: String) -> Token {
        Token {
            kind: match *self {
                Self::String { str_so_far } => TokenType::StringLiteral,
                Self::Int { str_so_far } => TokenType::IntLiteral,
                Self::Id { str_so_far } => {
                    // Special handler here, do we transform this to a keyword?
                    match str_so_far.as_str() {
                        s_ref if PunctuationBookkeep.contains(s_ref) => TokenType::Keyword,
                        &_ => TokenType::Id,
                    }
                }
                Self::NoContext => {
                    panic!("NoContext should not be called to crate construct_token")
                }
            },
            coord: Coord {
                col: (col_idx + 1) as u32,
                line: (line_idx + 1) as u32,
            },
            string_value,
        }
    }
}
