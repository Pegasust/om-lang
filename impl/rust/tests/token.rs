#[cfg(test)]
mod tests {
    use rust::token::{PunctuationBookkeep, KeywordBookkeep};
    use itertools::Itertools;
    #[test]
    pub fn ensure_standard_punc_into_iter() {
        let puncs = PunctuationBookkeep {}
            .into_iter()
            .collect_vec();
        let standards = [
            ":", ",", "!=", "&", "*", "/", "%", "<=", "<", ">=", ">", "==", "|", "=", "+", "-",
            "[", "]", "{", "}", "(", ")",
        ];
        standards.iter().for_each(|s| {
            assert!(
                puncs.contains(s),
                "PunctuationBookkeep.into_iter does not contain standard \"{}\"",
                s
            )
        });
    }
    #[test]
    pub fn ensure_std_keyword_into_iter() {
        let standards = [
            "and", "bool", "call", "else", "false", "func", "if", "int", "length", "not", "or",
            "print", "return", "true", "var", "while",
        ];
        let kw = KeywordBookkeep{}.into_iter().collect_vec();
        standards.iter().for_each(|s| {
            assert!(kw.contains(s), 
                "KeywordBookkeep.into_iter does not contain standard \"{}\"", s
            )
        })
    }
}
