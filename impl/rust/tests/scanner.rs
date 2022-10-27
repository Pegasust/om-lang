#[cfg(test)]
mod tests {
    use std::error::Error;

    use itertools::Itertools;
    use project_root::get_project_root;
    use rust::scanner::Scanner;

    fn _correct_omega() -> Result<Vec<String>, Box<dyn Error>> {
        serde_json::from_str(&std::fs::read_to_string(get_project_root()?.join("tests/data/correct.json"))?).map_err(|e|
            e.into()
        )
    }
    fn _incorrect_omega() -> Result<Vec<String>, Box<dyn Error>> {
        serde_json::from_str(&std::fs::read_to_string(get_project_root()?.join("tests/data/incorrect.json"))?).map_err(|e|
            e.into()
        )
    }
    #[test]
    pub fn correct_omega() {
        let tests: Vec<String> = _correct_omega().unwrap();
        for (test_idx, test) in tests.iter().enumerate() {
            println!("Test {}: '{}'", test_idx, &test);
            let tokens = Scanner::new(test).iter().map(|v| {
                println!("Yielded: {:?}", v);
                v
            }).collect_vec();
            assert!(tokens.len() >= test.len(), "Test '{}': empty token", &test);
            assert!(tokens.iter().all(|res_token| res_token.is_ok()),
                "Test '{}': error", &test
            )
        }
    }

    #[test]
    pub fn incorrect_omega() {
        let tests: Vec<String> = _incorrect_omega().unwrap();
        for test in tests {
            let tokens = Scanner::new(&test).iter().collect_vec();
            assert!(tokens.iter().any(|res_token| res_token.is_err()),
                "Test '{}': no error; tokens: {:?}", &test, tokens
            )
        }
    }
}
