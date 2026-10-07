#!/bin/sh
# Serve this checkout's murmuration.html on 127.0.0.1 in the background and print its URL.
#   ./bootstrap.sh              start (or find) this checkout's server; the URL goes to stdout
#   ./bootstrap.sh --open       the same, then open the page in the default browser
#   ./bootstrap.sh --port N     use exactly port N (fails if anything else holds it)
#   ./bootstrap.sh --status     print the URL if this checkout's server is up (exit 0), else exit 1
#   ./bootstrap.sh --stop       stop this checkout's server
# Without --port it tries $MURMURATION_PORT or 8766, then the next free port above it, never one
# in AVOID (ports other local servers use: it neither probes nor takes them). Each checkout or
# worktree runs its own server; pid, port and log are in .serve/ (gitignored). Needs node and curl.
# The headless checks (murmuration-check.js, murmuration-falcon.js) need no server.
set -u

ROOT=$(cd "$(dirname "$0")" && pwd -P)
STATE=$ROOT/.serve/state
LOG=$ROOT/.serve/serve.log
AVOID=" 8765 8767 8776 8780 8781 8782 8783 "
PREFERRED=${MURMURATION_PORT:-8766}

say() { printf 'bootstrap: %s\n' "$*" >&2; }
die() { say "$*"; exit 1; }
url() { printf 'http://127.0.0.1:%s/murmuration.html\n' "$1"; }
is_port() { case $1 in ''|*[!0-9]*) return 1 ;; esac; [ "$1" -ge 1 ] && [ "$1" -le 65535 ]; }
get() { curl -q -s --noproxy '*' --max-time 2 "$@"; }

# probe PORT: sets KIND to free, ours (this checkout's server answers there; SPID is its pid) or taken
probe() {
  KIND=taken SPID=''
  body=$(get "http://127.0.0.1:$1/__serve" 2>/dev/null); rc=$?
  if [ "$rc" -eq 7 ]; then KIND=free
  elif [ "$rc" -eq 0 ] && [ "$(printf '%s\n' "$body" | sed -n 's/^root //p')" = "$ROOT" ]; then
    KIND=ours SPID=$(printf '%s\n' "$body" | sed -n 's/^pid //p')
  fi
}

# running: true, with PORT and PID set, if this checkout's server answers on the port in .serve/state
running() {
  [ -f "$STATE" ] && read -r PORT PID < "$STATE" && is_port "$PORT" || return 1
  probe "$PORT"; [ "$KIND" = ours ] && PID=$SPID
}

# drop a state file whose server no longer answers; kill its pid only if it is still our server
# script. True if it killed one.
clear_stale() {
  [ -f "$STATE" ] || return 1
  read -r _port _pid < "$STATE" 2>/dev/null
  rm -f "$STATE"
  [ -n "${_pid:-}" ] && ps -p "$_pid" -o command= 2>/dev/null | grep -qF "$ROOT/murmuration-serve.js" &&
    end_pid "$_pid" && say "stopped unresponsive server pid $_pid"
}

# end_pid PID: TERM (and CONT, so a stopped process acts on it), wait up to 5 s, then KILL
end_pid() {
  kill "$1" 2>/dev/null; kill -CONT "$1" 2>/dev/null
  i=0; while kill -0 "$1" 2>/dev/null && [ "$i" -lt 25 ]; do sleep 0.2; i=$((i + 1)); done
  if kill -0 "$1" 2>/dev/null; then kill -9 "$1" 2>/dev/null; fi
}

remember() { mkdir -p "$ROOT/.serve" && echo "$1 $2" > "$STATE"; }

start() {
  if running; then
    [ -z "$WANT" ] || [ "$WANT" = "$PORT" ] || say "already on port $PORT; run --stop first to move it to $WANT"
    say "already serving $ROOT (pid $PID)"; url "$PORT"; return 0
  fi
  clear_stale || :
  NODE=${NODE:-$(command -v node)}
  [ -n "$NODE" ] || die "node not found on PATH: install Node.js 16+ (e.g. 'brew install node') or set NODE=/path/to/node"
  "$NODE" -e 'process.exit(+process.versions.node.split(".")[0] >= 16 ? 0 : 1)' ||
    die "node $("$NODE" --version) is too old: need 16+"
  command -v curl > /dev/null || die "curl not found (used for health checks)"

  if [ -n "$WANT" ]; then
    case $AVOID in *" $WANT "*) die "port $WANT belongs to another local server; pick another" ;; esac
    probe "$WANT"
    case $KIND in
      ours) PORT=$WANT; remember "$PORT" "$SPID"; say "already serving $ROOT (pid $SPID)"; url "$PORT"; return 0 ;;
      free) PORT=$WANT ;;
      *) die "port $WANT is in use by another process; pick another or omit --port" ;;
    esac
  else
    PORT='' p=$PREFERRED last=$((PREFERRED + 40))
    while [ "$p" -le "$last" ] && [ "$p" -le 65535 ]; do
      case $AVOID in *" $p "*) p=$((p + 1)); continue ;; esac
      probe "$p"
      case $KIND in
        ours) PORT=$p; remember "$PORT" "$SPID"; say "already serving $ROOT (pid $SPID)"; url "$PORT"; return 0 ;;
        free) PORT=$p; break ;;
      esac
      p=$((p + 1))
    done
    [ -n "$PORT" ] || die "no free port in $PREFERRED-$last"
    [ "$PORT" = "$PREFERRED" ] || say "port $PREFERRED is taken by another process; using $PORT"
  fi

  mkdir -p "$ROOT/.serve"
  nohup "$NODE" "$ROOT/murmuration-serve.js" "$PORT" < /dev/null > "$LOG" 2>&1 &
  PID=$!
  remember "$PORT" "$PID"
  i=0
  while [ "$i" -lt 50 ]; do
    if ! kill -0 "$PID" 2>/dev/null; then
      rm -f "$STATE"; tail -n 5 "$LOG" >&2; die "server exited; log: $LOG"
    fi
    code=$(get -o /dev/null -w '%{http_code}' "$(url "$PORT")")
    if [ "$code" = 200 ] && running; then
      say "serving $ROOT (pid $PID, log .serve/serve.log)"; url "$PORT"; return 0
    fi
    sleep 0.2; i=$((i + 1))
  done
  end_pid "$PID"; rm -f "$STATE"; die "server did not answer within 10 s; log: $LOG"
}

stop() {
  if running; then
    end_pid "$PID"; rm -f "$STATE"; say "stopped pid $PID (port $PORT)"; return 0
  fi
  clear_stale || say "not running"
}

status() {
  if running; then say "serving $ROOT (pid $PID, port $PORT)"; url "$PORT"; return 0; fi
  say "not running"; return 1
}

ACTION=start WANT='' OPEN=''
while [ $# -gt 0 ]; do
  case $1 in
    --stop) ACTION=stop ;;
    --status) ACTION=status ;;
    --open) OPEN=1 ;;
    --port) [ $# -ge 2 ] || die "--port needs a number"; WANT=$2; shift ;;
    --port=*) WANT=${1#--port=} ;;
    -h|--help) awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 0 ;;
    *) die "unknown option $1 (see --help)" ;;
  esac
  shift
done
[ -z "$WANT" ] || is_port "$WANT" || die "--port needs a number from 1 to 65535"
is_port "$PREFERRED" || die "MURMURATION_PORT must be a number from 1 to 65535"

case $ACTION in
  stop) stop ;;
  status) status ;;
  start)
    start
    if [ -n "$OPEN" ]; then
      if command -v open > /dev/null; then open "$(url "$PORT")"; else xdg-open "$(url "$PORT")" > /dev/null 2>&1 & fi
    fi ;;
esac
