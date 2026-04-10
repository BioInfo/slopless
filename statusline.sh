#!/bin/bash
# Claude Code Status Line v5.1 - "Neon Dashboard"
# 2-line display with Unicode graphics, progress bar, segment separators
# Correct JSON paths per https://code.claude.com/docs/en/statusline
# Git caching (5s), single jq call, Warp-compatible ANSI

input=$(cat)
# Debug: uncomment next line to inspect raw JSON
# echo "$input" > /tmp/statusline-debug.json

# =============================================================================
# SINGLE jq CALL - extract everything at once for performance
# =============================================================================
eval "$(echo "$input" | jq -r '
  @sh "MODEL=\(.model.display_name // "Claude")",
  @sh "MODEL_ID=\(.model.id // "")",
  @sh "CWD=\(.workspace.current_dir // .cwd // "")",
  @sh "COST=\(.cost.total_cost_usd // 0)",
  @sh "DURATION_MS=\(.cost.total_duration_ms // 0)",
  @sh "API_MS=\(.cost.total_api_duration_ms // 0)",
  @sh "LINES_ADD=\(.cost.total_lines_added // 0)",
  @sh "LINES_DEL=\(.cost.total_lines_removed // 0)",
  @sh "USED_PCT=\(.context_window.used_percentage // 0)",
  @sh "CTX_SIZE=\(.context_window.context_window_size // 200000)",
  @sh "TOTAL_IN=\(.context_window.total_input_tokens // 0)",
  @sh "TOTAL_OUT=\(.context_window.total_output_tokens // 0)",
  @sh "AGENT=\(.agent.name // "")",
  @sh "VIM_MODE=\(.vim.mode // "")",
  @sh "STYLE=\(.output_style.name // "")",
  @sh "VERSION=\(.version // "")",
  @sh "EXCEEDS_200K=\(.exceeds_200k_tokens // false)"
' 2>/dev/null)" 2>/dev/null

# Fallbacks
[[ -z "$CWD" ]] && CWD="$HOME"
[[ -z "$MODEL" || "$MODEL" == "null" ]] && MODEL="Claude"
[[ "$COST" == "null" ]] && COST=0
[[ "$DURATION_MS" == "null" ]] && DURATION_MS=0
[[ "$USED_PCT" == "null" ]] && USED_PCT=0
[[ "$TOTAL_IN" == "null" ]] && TOTAL_IN=0
[[ "$TOTAL_OUT" == "null" ]] && TOTAL_OUT=0
[[ "$LINES_ADD" == "null" ]] && LINES_ADD=0
[[ "$LINES_DEL" == "null" ]] && LINES_DEL=0

# =============================================================================
# ANSI COLORS (standard codes - Warp compatible)
# =============================================================================
R=$'\033[0m'; DIM=$'\033[2m'; BOLD=$'\033[1m'
RED=$'\033[31m'; GRN=$'\033[32m'; YLW=$'\033[33m'; BLU=$'\033[34m'
MAG=$'\033[35m'; CYN=$'\033[36m'; WHT=$'\033[37m'; GRY=$'\033[90m'
BRED=$'\033[91m'; BGRN=$'\033[92m'; BYLW=$'\033[93m'; BBLU=$'\033[94m'
BMAG=$'\033[95m'; BCYN=$'\033[96m'; BWHT=$'\033[97m'

# Unicode glyphs (embedded directly - no escape interpretation needed)
SEP=" ${GRY}│${R} "

# =============================================================================
# FORMAT HELPERS
# =============================================================================
fmt_model() {
    case "$MODEL_ID" in
        *opus-4-6*|*opus-4.6*)     echo -n "${BMAG}◆ Opus4.6${R}" ;;
        *opus-4-5*|*opus-4.5*)     echo -n "${BMAG}◆ Opus4.5${R}" ;;
        *opus*)                     echo -n "${BMAG}◆ Opus${R}" ;;
        *sonnet-4-5*|*sonnet-4.5*) echo -n "${BBLU}◇ Son4.5${R}" ;;
        *sonnet*)                   echo -n "${BBLU}◇ Sonnet${R}" ;;
        *haiku-4-5*|*haiku-4.5*)   echo -n "${BGRN}○ Haiku4.5${R}" ;;
        *haiku*)                    echo -n "${BGRN}○ Haiku${R}" ;;
        *)                          echo -n "${CYN}● ${MODEL}${R}" ;;
    esac
}

fmt_tokens() {
    local t=$1
    if [[ $t -ge 1000000 ]]; then
        awk -v t="$t" 'BEGIN{printf "%.1fM", t/1000000}'
    elif [[ $t -ge 1000 ]]; then
        awk -v t="$t" 'BEGIN{printf "%.1fk", t/1000}'
    else
        printf "%d" "$t"
    fi
}

fmt_duration() {
    local ms=$1
    if [[ $ms -ge 3600000 ]]; then
        printf "%dh %dm" $((ms/3600000)) $(((ms%3600000)/60000))
    elif [[ $ms -ge 60000 ]]; then
        printf "%dm %ds" $((ms/60000)) $(((ms%60000)/1000))
    elif [[ $ms -ge 1000 ]]; then
        printf "%ds" $((ms/1000))
    else
        printf "%dms" "$ms"
    fi
}

# =============================================================================
# GIT INFO (cached 5s)
# =============================================================================
# Cache per-directory so switching projects doesn't show stale git info
GIT_CACHE="/tmp/statusline-git-$(echo "$CWD" | md5 -q 2>/dev/null || echo "$CWD" | md5sum 2>/dev/null | cut -d' ' -f1)"

git_seg=""
if command -v git &>/dev/null; then
    refresh=0
    if [[ ! -f "$GIT_CACHE" ]]; then
        refresh=1
    else
        age=$(( $(date +%s) - $(stat -f %m "$GIT_CACHE" 2>/dev/null || echo 0) ))
        [[ $age -gt 5 ]] && refresh=1
    fi
    if [[ $refresh -eq 1 ]]; then
        if git rev-parse --git-dir &>/dev/null 2>&1; then
            br=$(git branch --show-current 2>/dev/null)
            [[ -z "$br" ]] && br=$(git rev-parse --short HEAD 2>/dev/null)
            st=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
            md=$(git diff --numstat 2>/dev/null | wc -l | tr -d ' ')
            ut=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
            echo "${br}|${st}|${md}|${ut}" > "$GIT_CACHE"
        else
            echo "|||" > "$GIT_CACHE"
        fi
    fi
    IFS='|' read -r br st md ut < "$GIT_CACHE"
    if [[ -n "$br" ]]; then
        git_seg="${MAG}${br}${R}"
        [[ "$st" -gt 0 ]] 2>/dev/null && git_seg="${git_seg} ${BGRN}+${st}${R}"
        [[ "$md" -gt 0 ]] 2>/dev/null && git_seg="${git_seg} ${BYLW}!${md}${R}"
        [[ "$ut" -gt 0 ]] 2>/dev/null && git_seg="${git_seg} ${BRED}?${ut}${R}"
    fi
fi

# =============================================================================
# DIRECTORY
# =============================================================================
dir="$CWD"
[[ "$dir" == "$HOME"* ]] && dir="~${dir#$HOME}"
IFS='/' read -ra parts <<< "$dir"
[[ ${#parts[@]} -gt 4 ]] && dir="${parts[0]}/${parts[1]}/.../$(basename "$dir")"

# =============================================================================
# CONTEXT BAR (15 chars with Unicode block elements)
# =============================================================================
pct=${USED_PCT%.*}
[[ -z "$pct" || "$pct" == "null" ]] && pct=0

if [[ $pct -ge 80 ]]; then BAR_C="$BRED"
elif [[ $pct -ge 60 ]]; then BAR_C="$BYLW"
elif [[ $pct -ge 40 ]]; then BAR_C="$YLW"
else BAR_C="$BGRN"; fi

# Build bar: ▓ for filled, ░ for empty
BAR_W=15
filled=$((pct * BAR_W / 100))
[[ $filled -gt $BAR_W ]] && filled=$BAR_W
empty=$((BAR_W - filled))
bar=""
for ((i=0; i<filled; i++)); do bar="${bar}▓"; done
for ((i=0; i<empty; i++)); do bar="${bar}░"; done

# =============================================================================
# 5-HOUR BLOCK TIMER
# =============================================================================
hour=$(date -u +%H); min=$(date -u +%M)
block_hour=$((hour % 5))
remaining_min=$(( (4 - block_hour) * 60 + (60 - min) ))
[[ $remaining_min -ge 300 ]] && remaining_min=$((remaining_min - 300))
block_timer="$(( remaining_min / 60 ))h$(( remaining_min % 60 ))m"

# =============================================================================
# COMPUTED VALUES
# =============================================================================
session_tokens=$((TOTAL_IN + TOTAL_OUT))
tokens_str=$(fmt_tokens $session_tokens)

# =============================================================================
# LINE 1: Model + Agent + Vim │ Dir on Branch │ Lines
# =============================================================================
echo -n "$(fmt_model)"

# Agent
[[ -n "$AGENT" && "$AGENT" != "null" ]] && echo -n " ${BCYN}@${AGENT}${R}"

# Vim mode
if [[ -n "$VIM_MODE" && "$VIM_MODE" != "null" ]]; then
    case "$VIM_MODE" in
        INSERT) echo -n " ${BGRN}▶ INS${R}" ;;
        NORMAL) echo -n " ${BYLW}■ NOR${R}" ;;
    esac
fi

# Style (skip default)
[[ -n "$STYLE" && "$STYLE" != "null" && "$STYLE" != "default" ]] && echo -n " ${DIM}[${STYLE}]${R}"

echo -n "$SEP"
echo -n "${BCYN}${dir}${R}"

# Git
[[ -n "$git_seg" ]] && echo -n " on ${git_seg}"

# Lines changed
if [[ $LINES_ADD -gt 0 || $LINES_DEL -gt 0 ]]; then
    echo -n "$SEP"
    echo -n "${BGRN}▲ ${LINES_ADD}${R} ${BRED}▼ ${LINES_DEL}${R}"
fi

echo ""

# =============================================================================
# LINE 2: Context bar + % │ Cost │ Tokens │ Duration │ Block
# =============================================================================
echo -n "${BAR_C}${bar}${R} ${pct}%"

# Cost
if [[ "$COST" != "0" && -n "$COST" ]]; then
    echo -n "$SEP"
    printf "${BGRN}\$%.2f${R}" "$COST"
fi

# Tokens
if [[ $session_tokens -gt 0 ]]; then
    echo -n "$SEP"
    echo -n "${BAR_C}${tokens_str}${R}"
fi

# Duration
if [[ $DURATION_MS -gt 0 ]]; then
    echo -n "$SEP"
    echo -n "${BCYN}⏱ $(fmt_duration $DURATION_MS)${R}"
fi

# Block timer
echo -n "$SEP"
echo -n "${BBLU}⏳ ${block_timer}${R}"

# 200k warning
[[ "$EXCEEDS_200K" == "true" ]] && echo -n " ${BRED}⚠ >200k${R}"

echo ""
