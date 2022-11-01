#[cfg(test)]
mod scanner {
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
    pub fn correct() {
        let tests: Vec<String> = _correct_omega().unwrap();
        for (test_idx, test) in tests.iter().enumerate() {
            println!("-- Test {}: '{}'", test_idx, &test);
            let tokens = Scanner::new(test).iter().map(|v| {
                println!("Yielded: {:?}", &v);
                v
            }).collect_vec();
            assert!(tokens.len() >= if test.trim().len() == 0 {0} else {1}, "!!-- Test '{}':\nTokens: {:?}", &test, &tokens);
            let errors = tokens.iter().filter(|v| v.is_err()).collect_vec();
            assert!(errors.len() == 0, "!! --Test '{}':\nErrors: {:?}", &test, &errors);

        }
    }

    #[test]
    pub fn incorrect() {
        let tests: Vec<String> = _incorrect_omega().unwrap();
        for test in tests {
            let tokens = Scanner::new(&test).iter().collect_vec();
            assert!(tokens.iter().any(|res_token| res_token.is_err()),
                "Test '{}': no error; tokens: {:?}", &test, tokens
            )
        }
    }

    #[test]
    pub fn multiline() {
        let tests = vec![
            r#""#
        ].into_iter().map(|v| v.trim()).collect_vec();
        for test in tests {

        }
    }
}
