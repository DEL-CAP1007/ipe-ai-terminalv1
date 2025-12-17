#!/bin/bash
# Usage: ./runcli.sh <command> [args...]

PYTHON_BIN="./venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
	PYTHON_BIN="python3"
fi

# convenience wrappers for search
if [ "$1" = "search.all" ] || [ "$1" = "search.all.summary" ]; then
	COMMAND="$1"
	shift
	pass_through=()
	saw_delim=0
	for arg in "$@"; do
		if [ "$arg" = "--" ]; then
			saw_delim=1
			continue
		fi
		if [ $saw_delim -eq 1 ]; then
			pass_through+=("$arg")
		fi
	done
	if [ $saw_delim -eq 0 ]; then
		pass_through=("$@")
	fi
	if [ "$COMMAND" = "search.all" ]; then
		has_no_summary=0
		for a in "${pass_through[@]}"; do
			if [ "$a" = "--no-summary" ]; then
				has_no_summary=1
			fi
		done
		if [ $has_no_summary -eq 0 ]; then
			pass_through+=("--no-summary")
		fi
		exec "$PYTHON_BIN" scripts/search_all_and_summarize.py "${pass_through[@]}"
	else
		exec "$PYTHON_BIN" scripts/search_all_and_summarize.py "${pass_through[@]}"
	fi
fi

if [ "$1" = "search.tasks" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.tasks.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py "$@"
	exit $?
fi

# convenience wrappers for events search
if [ "$1" = "search.events" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.event "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.events.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.event "$@"
	exit $?
fi

# convenience wrappers for clients search
if [ "$1" = "search.clients" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.client "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.clients.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.client "$@"
	exit $?
fi

# convenience wrappers for speakers search
if [ "$1" = "search.speakers" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.speaker "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.speakers.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.speaker "$@"
	exit $?
fi

# convenience wrappers for programs search
if [ "$1" = "search.programs" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.program "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.programs.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.program "$@"
	exit $?
fi

# convenience wrappers for cohorts search
if [ "$1" = "search.cohorts" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.cohort "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.cohorts.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.cohort "$@"
	exit $?
fi

# convenience wrappers for participants search
if [ "$1" = "search.participants" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.participant "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.participants.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.participant "$@"
	exit $?
fi

# convenience wrappers for communication log search
if [ "$1" = "search.comm" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.comm "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.comm.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.comm "$@"
	exit $?
fi

# saved query presets
if [ "$1" = "ops.deliverables" ]; then
	shift
	exec "$PYTHON_BIN" scripts/run_saved_query.py "ops.deliverables" "$@"
fi

if [ "$1" = "ops.followup" ]; then
	shift
	exec "$PYTHON_BIN" scripts/run_saved_query.py "ops.followup" "$@"
fi

if [ "$1" = "ops.blocked" ]; then
	shift
	exec "$PYTHON_BIN" scripts/run_saved_query.py "ops.blocked" "$@"
fi

if [ "$1" = "ops.progress" ]; then
	shift
	exec "$PYTHON_BIN" scripts/run_saved_query.py "ops.progress" "$@"
fi

if [ "$1" = "ops.suggest_tasks" ]; then
	shift
	exec "$PYTHON_BIN" scripts/suggest_tasks_from_brief.py "$@"
fi

if [ "$1" = "ops.review" ]; then
	shift
	exec "$PYTHON_BIN" scripts/review_suggestions.py "$@"
fi

if [ "$1" = "ops.approve" ]; then
	shift
	exec "$PYTHON_BIN" scripts/approve_suggestions.py "$@"
fi

if [ "$1" = "ops.reject" ]; then
	shift
	exec "$PYTHON_BIN" scripts/reject_suggestions.py "$@"
fi

if [ "$1" = "ops.queue" ]; then
	shift
	exec "$PYTHON_BIN" scripts/ops_queue.py "$@"
fi

if [ "$1" = "ops.brief" ]; then
	shift
	exec "$PYTHON_BIN" scripts/run_brief.py "$@"
fi

# convenience wrappers for participants search
if [ "$1" = "search.participants" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.participant "$@" --no-summary
	exit $?
fi

if [ "$1" = "search.participants.summary" ]; then
	shift
	if [ "$1" = "--" ]; then
		shift
	fi
	"$PYTHON_BIN" scripts/search_and_summarize.py --type notion.participant "$@"
	exit $?
fi

PYTHONPATH=. "$PYTHON_BIN" src/main.py "$@"
