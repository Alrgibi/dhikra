#!/usr/bin/env bash
# setup_env.sh -- rebuild the analysis environment. RUN THIS FIRST IN EVERY SESSION.
#
# WHY THIS EXISTS. The Cowork VM's $HOME is EPHEMERAL: it is a fresh machine each
# session. The project folder is a persistent mount; $HOME is not. So the pinned
# environment at $HOME/dhenv, built on 19 August, does not exist in any later
# session, and a script needing pandas or scikit-learn fails with a bare
# ModuleNotFoundError that reads like a broken repository rather than a missing
# environment. One session lost time to exactly that on 26 August.
#
# WHY NOT PUT THE ENVIRONMENT IN THE PROJECT FOLDER. Because it does not fit.
# The mount reports 100% used with about 685 MB free, and scikit-learn, pandas,
# scipy and matplotlib together are larger than that. Rebuilding into $HOME costs
# a few minutes of network and nothing of the user's disk.
#
# WHY IT IS SAFE TO RE-RUN. It is idempotent and RESUMABLE. device_bash allows
# 45 seconds per call and background jobs do not survive the call, so a full
# install WILL be cut off part way. That is fine: pip skips what is already
# satisfied, so running this three or four times in a row completes it. Run it
# until it prints READY.
#
# THE PIN IS LOAD-BEARING. models/dhikra_model.pkl is a scikit-learn 1.8.0
# pickle. scikit-learn does not guarantee that a model pickled by one version
# loads under another, and the model is FROZEN and cannot be rebuilt without a
# new external validation. The library is pinned to the model, not the reverse.
set -u
PYBASE="$HOME/python/bin/python3.12"
# BOOTSTRAP (added 26 Aug 2026): $HOME/python is as ephemeral as $HOME/dhenv,
# the device proxy 403s the standalone-CPython host, and scikit-learn 1.8.0
# needs python >= 3.11 while the VM ships 3.10. A CPython 3.12.13 tarball is
# therefore parked on the persistent mount; extract it if the interpreter is
# missing. (md5 50437aa442a57037ef35055d424aba80, python-build-standalone
# 20260807 install_only_stripped, shipped via the cloud container because of
# the proxy block.)
TARBALL="$(dirname "$0")/../docs/chapters/_tmp/py312.tar.gz"
if [ ! -x "$PYBASE" ] && [ -f "$TARBALL" ]; then
  echo "extracting pinned CPython 3.12 from docs/chapters/_tmp/py312.tar.gz"
  tar -C "$HOME" -xzf "$TARBALL"
fi
[ -x "$PYBASE" ] || PYBASE="$(command -v python3)"
VENV="$HOME/dhenv"

# The acceptance test is not "the packages imported". It is "the frozen model
# loads", because that is the only thing the environment exists to do and it is
# the thing a version mismatch breaks. An environment that imports sklearn and
# cannot unpickle the model is worse than none: it fails later and less clearly.
check_ready () {
  "$VENV/bin/python" - <<'PY' 2>/dev/null
import pickle, sys, os
sys.path.insert(0, "src")
root = os.environ.get("DHIKRA_ROOT", ".")
import sklearn, pandas, scipy, reportlab, pypdf, docx  # noqa -- page_count.py and check_docx.py need the last three
b = pickle.load(open(os.path.join(root, "models", "dhikra_model.pkl"), "rb"))
assert len(b["features"]) == 64 and abs(b["screening_threshold"] - 0.367) < 1e-9
print("READY  python %s  sklearn %s  model loads, 64 features, threshold %.3f"
      % (sys.version.split()[0], sklearn.__version__, b["screening_threshold"]))
PY
}

if [ -x "$VENV/bin/python" ] && check_ready; then
  exit 0
fi

[ -x "$VENV/bin/python" ] || { echo "creating $VENV from $PYBASE"; "$PYBASE" -m venv "$VENV" || exit 1; }

echo "installing (this WILL be cut off by the 45s limit; just run this script again)"
"$VENV/bin/pip" install --quiet --disable-pip-version-check \
    "scikit-learn==1.8.0" pandas scipy matplotlib reportlab pypdf python-docx 2>&1 | tail -3

if check_ready; then
  exit 0
fi
echo "NOT YET COMPLETE -- run this script again"
if [ "$PYBASE" = "$(command -v python3)" ]; then
  echo
  echo "  WARNING: built from the SYSTEM python ($("$PYBASE" -V 2>&1)), because"
  echo "  \$HOME/python/bin/python3.12 was absent. models/dhikra_model.pkl was"
  echo "  pickled under python 3.12 with scikit-learn 1.8.0. If the model refuses"
  echo "  to load under this interpreter, that is the reason, and no amount of"
  echo "  reinstalling scikit-learn will fix it. Say so rather than working around"
  echo "  it: the model is frozen and must not be rebuilt."
fi
exit 2
