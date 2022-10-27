#!/usr/bin/env sh

# allows simple ways to edit packages in Cargo.toml with `cargo rm <package>`
cargo install cargo-edit
# reasonable feedback loop
cargo install cargo-watch
# Similar to npm run-script. The purpose is not so clear against makefiles
# but theoretically, this might help with Windows cargo development cycle
cargo install cargo-run-script

