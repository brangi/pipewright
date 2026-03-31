#!/bin/bash
# Demo presentation script — just prints commands, doesn't execute them

show() {
    clear
    echo ""
    echo -e "  \033[90m# $1\033[0m"
    echo -e "  \033[37m$ $2\033[0m"
    echo ""
    sleep 3
}

show "Quick setup — pick a provider, paste your key" "pipewright setup"
show "Generate tests for any source file" "pipewright run test-gen ./src/auth.py -p groq -y"
show "Solve a GitHub issue end-to-end" "pipewright run issue-solve 42"
show "Review code changes or a pull request" "pipewright run code-review HEAD~3..HEAD"
show "Debug an issue systematically" "pipewright run debug 'TypeError in auth.py line 42'"
show "Refactor code with AI guidance" "pipewright run refactor ./src/auth.py"
show "Generate documentation" "pipewright run docs-gen ./src/"

clear
echo ""
echo -e "  \033[90m# Works with 5 LLM providers — including free ones\033[0m"
echo -e "  \033[37m$ pip install pipewright\033[0m"
echo ""
sleep 4
