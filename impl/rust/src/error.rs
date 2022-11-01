use core::fmt;
use std::{error::Error, result};

use serde::{Deserialize, Serialize};

use crate::token::Coord;

#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum OmegaError {
    InvalidCharacter {
        chr: char,
        coord: Coord,
        context: String,
    },
    UnexpectedLineEnd {
        coord: Coord,
        context: String,
    },
}

impl Error for OmegaError {}

impl fmt::Display for OmegaError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            OmegaError::InvalidCharacter { chr, coord, context } => write!(
                f,
                "Invalid character \'{}\'@{:?}\n\t{}",
                chr, coord, context
            ),
            OmegaError::UnexpectedLineEnd { coord, context } => write!(f,
                "Unexpected line end @{:?}\n\t{}", coord, context
            ),
        }
    }
}

pub(crate) type Result<T> = result::Result<T, OmegaError>;
