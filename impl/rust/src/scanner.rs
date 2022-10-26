//! Scanner for Omega language, given some string input. This is an abstraction for string iterator
//! and is intended to be used by the parser.

use std::collections::HashSet;

use crate::{
    error::{self, InvalidCharacter, OmegaError},
    token::{Bookkeep, Coord, PunctuationBookkeep, Token, TokenType},
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
    /// Creates an iterator through [Token]
    pub fn iter(&self) -> impl Iterator<Item = error::Result<Token>> + '_ {
        // I can't believe I just did it. Thanks for a lot of the references,
        // itertools.
        scanner(&self.raw_string)
    }
}

#[derive(Debug)]
enum ScanningType {
    Id,
    Int,
    String,
    Punctuation { remain: HashSet<&'static str> },
}


#[derive(Debug)]
struct ConcreteScannerState {
    scanning_type: ScanningType,
    str_so_far: String,
}

type ScannerState = Option<ConcreteScannerState>;

#[derive(Debug)]
enum CharMatchState {
    Forbidden { error_ctx: Option<String> },
    EndOfToken { next_scan_type: ScannerState },
    Match,
}

pub fn scanner<'a> (s: &'a str) -> impl Iterator<Item = error::Result<Token>> + 'a {
    //! TODO: Anyway to turn this into s: String?
    s.split('\n').enumerate().flat_map(|(line_idx, line)| {
        // Returns Result<Vec<Token>>. If there's something awry, the line is
        // at fault.
        println!("Line {}: {}", line_idx, line);
        // TODO: looks like scan() is not behaving as expected.
        // it exits at the first None return.
        line.chars().enumerate().scan(
            (line_idx, ScannerState::None),
            |(line_idx, state), (col_idx, chr)| -> Option<Result<Token, OmegaError>> {
                println!("{}:{} '{}': Pre-state is {:?}", line_idx, col_idx, chr, state);
                match state {
                    None => {
                        match chr {
                            '"' => {
                                *state = Some(ConcreteScannerState {
                                    scanning_type: ScanningType::String,
                                    str_so_far: String::new(),
                                });
                                println!("{}:{} '{}': State is {:?}", line_idx, col_idx, chr, state);
                            }
                            chr if chr.is_ascii_digit() => {
                                *state = Some(ConcreteScannerState {
                                    scanning_type: ScanningType::Int,
                                    str_so_far: chr.to_string(),
                                });
                                println!("{}:{} '{}': State is {:?}", line_idx, col_idx, chr, state);
                            }
                            chr if chr.is_ascii_alphabetic() || chr == '_' => {
                                *state = Some(ConcreteScannerState {
                                    scanning_type: ScanningType::Id,
                                    str_so_far: chr.to_string(),
                                });
                                println!("{}:{} '{}': State is {:?}", line_idx, col_idx, chr, state);
                            }
                            chr => {
                                let matches = PunctuationBookkeep.match_first_char(chr);
                                if !matches.is_empty() {
                                    *state = Some(ConcreteScannerState {
                                        scanning_type: ScanningType::Punctuation {
                                            remain: matches,
                                        },
                                        str_so_far: chr.to_string(),
                                    })
                                }
                                println!("{}:{} '{}': State is {:?}", line_idx, col_idx, chr, state);
                            }
                        };
                        None
                    }
                    Some(concrete_v) => match concrete_v.chr_type(chr) {
                        CharMatchState::Forbidden { error_ctx } => {
                            Some(Err(OmegaError::InvalidCharacter(InvalidCharacter {
                                chr,
                                coord: Coord {
                                    col: (col_idx + 1) as u32,
                                    line: (*line_idx + 1) as u32,
                                },
                                context: error_ctx.unwrap_or("Unknown context".to_owned()),
                            })))
                        }
                        CharMatchState::EndOfToken { next_scan_type } => {
                            let str_so_far = state.as_ref().unwrap().str_so_far.clone();
                            let tok = state
                                .as_ref()
                                .unwrap()
                                .construct_token(col_idx, *line_idx, str_so_far);
                            *state = next_scan_type;
                            Some(Ok(tok))
                        }
                        CharMatchState::Match => {
                            state.as_mut().unwrap().str_so_far += &chr.to_string();
                            None
                        }
                    },
                }
            },
        )
    })
}

trait ScanHelp {
    fn chr_type(&mut self, chr: char) -> CharMatchState;
    fn construct_token(&self, col_idx: usize, line_idx: usize, string_value: String) -> Token;
}

impl ScanHelp for ConcreteScannerState {
    fn chr_type(&mut self, chr: char) -> CharMatchState {
        match &mut self.scanning_type {
            ScanningType::String => match chr {
                '"' => CharMatchState::EndOfToken {
                    next_scan_type: None,
                },
                // TODO: for now, accept everything, don't need to worry about escape sequence
                _ => CharMatchState::Match,
            },
            ScanningType::Int => match chr {
                chr if chr.is_ascii_whitespace() => CharMatchState::EndOfToken {
                    next_scan_type: None,
                },
                chr if chr.is_ascii_digit() || chr == '_' => CharMatchState::Match,
                chr => {
                    let punc_match = PunctuationBookkeep.match_first_char(chr);
                    if punc_match.len() > 0 {
                        CharMatchState::EndOfToken {
                            next_scan_type: Some(ConcreteScannerState {
                                scanning_type: ScanningType::Punctuation { remain: punc_match },
                                str_so_far: chr.to_string(),
                            }),
                        }
                    } else {
                        CharMatchState::Forbidden {
                            error_ctx: Some(format!(
                                "Unexpected character '{}' while parsing integer literal",
                                chr
                            )),
                        }
                    }
                }
            },
            ScanningType::Id => match chr {
                chr if chr.is_ascii_whitespace() => CharMatchState::EndOfToken {
                    next_scan_type: None,
                },
                chr if chr.is_ascii_alphanumeric() => CharMatchState::Match,
                chr => {
                    let punc_match = PunctuationBookkeep.match_first_char(chr);
                    if punc_match.len() > 0 {
                        CharMatchState::EndOfToken {
                            next_scan_type: Some(ConcreteScannerState {
                                scanning_type: ScanningType::Punctuation { remain: punc_match },
                                str_so_far: chr.to_string(),
                            }),
                        }
                    } else {
                        CharMatchState::Forbidden {
                            error_ctx: Some(format!(
                                "Unexpected character '{}' while parsing id",
                                chr
                            )),
                        }
                    }
                }
            },
            ScanningType::Punctuation { remain } => {
                // update the remaining to this new character
                remain.retain(|v| {
                    v.chars()
                        .nth(self.str_so_far.len())
                        .map(|c| c == chr)
                        .unwrap_or(false)
                });
                self.str_so_far.push(chr);
                let ret = match remain.len() {
                    0 => CharMatchState::Forbidden {
                        error_ctx: Some(format!(
                            "No matching punctuation found for {}",
                            self.str_so_far
                        )),
                    },
                    1 => CharMatchState::EndOfToken {
                        next_scan_type: None,
                    },
                    _ => CharMatchState::Match,
                };
                ret
            }
        }
    }
    fn construct_token(&self, col_idx: usize, line_idx: usize, string_value: String) -> Token {
        Token {
            kind: match &self.scanning_type {
                ScanningType::String => TokenType::StringLiteral,
                ScanningType::Int => TokenType::IntLiteral,
                ScanningType::Id => {
                    // Special handler here, do we transform this to a keyword?
                    match self.str_so_far.as_str() {
                        s_ref if PunctuationBookkeep.contains(s_ref) => TokenType::Keyword,
                        &_ => TokenType::Id,
                    }
                }
                ScanningType::Punctuation { remain: _ } => TokenType::Punctuation,
            },
            string_value,
            coord: Coord {
                col: (col_idx + 1) as u32,
                line: (line_idx + 1) as u32,
            },
        }
    }
}
