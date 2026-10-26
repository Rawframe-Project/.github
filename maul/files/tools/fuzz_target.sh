#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Sirac Ozmen
#
# Runs one libFuzzer target and reports a finding without its input.
#
#   tools/fuzz_target.sh TARGET [LIBFUZZER ARGUMENT...]
#
# The target runs with an explicit seed, never 0 (which libFuzzer takes
# as "pick one"), and writes its findings to out/fuzz-crashes/NAME/ and
# its log to out/fuzz-logs/NAME.log; OUT overrides out. Both stay on the
# machine that ran it. Every run's log is public in CI, and libFuzzer
# prints a finding's input there as bytes, text and Base64, so on a
# finding this prints only the target, its seed, the finding's file name
# (the SHA-1 of the input), the sanitizers' runtime error lines and the
# report from its "==PID== ERROR:" line to its "SUMMARY:" line, all
# taken from the log above libFuzzer's first input dump. It exits 0 when
# the target found nothing and 1 when it found something.
#
# A finding is reproduced by running the same target from the same
# corpus with the printed seed until it finds the same file name.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: tools/fuzz_target.sh TARGET [LIBFUZZER ARGUMENT...]" >&2
  exit 2
fi
target=$1
shift
name=$(basename "$target")
out=${OUT:-out}
crashes="$out/fuzz-crashes/$name"
log="$out/fuzz-logs/$name.log"
mkdir -p "$crashes" "$out/fuzz-logs"

seed=$(($(od -An -N4 -tu4 /dev/urandom) % 2147483647 + 1))
if "$target" -seed="$seed" -artifact_prefix="$crashes/" "$@" >"$log" 2>&1; then
  echo "$name: no finding (seed $seed)"
  exit 0
fi

# Everything from the first mutation line on is libFuzzer's dump of the
# input; no line of it is read.
head=$(sed '/^MS: [0-9]/,$d' "$log")
report=$(
  echo "$name: seed $seed"
  find "$crashes" -maxdepth 1 -type f -printf '%f\n' | sort
  grep -E -m 5 '^[^ ]+:[0-9]+:[0-9]+: runtime error: ' <<<"$head" || true
  sed -n '/^==[0-9]*== *ERROR: /,/^SUMMARY: /p' <<<"$head" | head -n 80
  echo "::error::$name found something"
)
# One write, so that targets run side by side do not interleave a short
# report.
printf '%s\n' "$report"
exit 1
