// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

use std::env;
use std::io::{self, Read};

fn main() {
    let args: Vec<String> = env::args().collect();
    let command = args.get(1).map(|s| s.as_str()).unwrap_or("help");

    let mut input = String::new();
    if command != "help" {
        io::stdin().read_to_string(&mut input).expect("Failed to read stdin");
    }

    match command {
        "wordfreq" => {
            let freq = pipewright_rust_demo::word_frequency(&input);
            let mut pairs: Vec<_> = freq.into_iter().collect();
            pairs.sort_by(|a, b| b.1.cmp(&a.1));
            for (word, count) in pairs {
                println!("{}: {}", word, count);
            }
        }
        "truncate" => {
            let max_len: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(80);
            for line in input.lines() {
                println!("{}", pipewright_rust_demo::truncate(line, max_len));
            }
        }
        "titlecase" => {
            for line in input.lines() {
                println!("{}", pipewright_rust_demo::title_case(line));
            }
        }
        _ => {
            eprintln!("Usage: textool <command> [args]");
            eprintln!("Commands: wordfreq, truncate [max_len], titlecase");
        }
    }
}
