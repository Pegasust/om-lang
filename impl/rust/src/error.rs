use core::fmt;
use std::{result, error::Error};

use serde::{Serialize, Deserialize};

use crate::token::Coord;

#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum OmegaError {
    InvalidCharacter(InvalidCharacter),
}
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct InvalidCharacter {
    pub(crate) chr: char,
    pub(crate) coord: Coord,
    pub(crate) context: String,
}

impl Error for OmegaError {}

impl fmt::Display for OmegaError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidCharacter(c) => write!(f, "Invalid character \'{}\'@{:?}\n\t{}",
                c.chr, c.coord, c.context
                )
        }
    }
}

pub(crate) type Result<T> = result::Result<T, OmegaError>;
