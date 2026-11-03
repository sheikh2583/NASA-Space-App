#!/usr/bin/env bash
# Shared helpers. Source this file; do not run it.
ROOT="$(git rev-parse --show-toplevel)"
TEAM_CSV="$ROOT/scripts/team.csv"
ME_FILE="$ROOT/.git/team-me"
PY="$(command -v python3 || command -v python || true)"

lc() { echo "$1" | tr 'A-Z' 'a-z'; }
field() { # field <github-user> <column number>
  awk -F, -v u="$(lc "$1")" -v c="$2" 'NR>1 && tolower($1)==u {print $c}' "$TEAM_CSV"
}
me() {
  if [ -f "$ME_FILE" ]; then cat "$ME_FILE"; else echo "Run first: bash scripts/git/setup.sh <your-github-username>" >&2; exit 1; fi
}
my_prefix() { field "$(me)" 4; }
my_folder() { field "$(me)" 5; }
my_name()   { field "$(me)" 2; }
current_branch() { git rev-parse --abbrev-ref HEAD; }
not_on_main() {
  if [ "$(current_branch)" = "main" ]; then
    echo "You are on main. Start a branch first: bash scripts/git/start.sh <topic>" >&2; exit 1
  fi
}
pr_url() { # prints a GitHub compare URL for the current branch (best effort)
  local u b; u="$(git remote get-url origin)"; b="$(current_branch)"
  u="${u%.git}"; u="${u/git@github.com:/https://github.com/}"
  echo "$u/compare/main...$b?expand=1"
}
