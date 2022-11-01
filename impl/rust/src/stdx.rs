use std::iter::Peekable;

pub(crate) fn iter_empty<It, T>(iter: It) -> (Peekable<It>, bool) where It: Iterator<Item=T> {
    let mut peek = iter.peekable();
    let is_empty = peek.peek().is_none();
    (peek, is_empty)
}

pub(crate) fn opt_iter_least_1<It, T>(iter: It) -> Option<Peekable<It>> where It: Iterator<Item=T> {
    let (peek, empty) = iter_empty(iter);
    empty.then_some(peek)
}

pub(crate) trait StdxIter<T>: Iterator<Item=T> + Sized {
    fn non_empty(self) -> Option<Peekable<Self>> {
        opt_iter_least_1(self)
    }
}

impl <It, T> StdxIter<T> for It where It: Iterator<Item=T> {}

