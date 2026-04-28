"""TC-S001-F-008-05 — no debug in prod: a production `npm run build` produces
a bundle in which the i18next debug flag is false.

Verification strategy (per the requirement's stated method):
  1. Confirm src/i18n/config.ts uses `import.meta.env.DEV` for the debug
     flag — Vite replaces this literal with `false` in production builds.
  2. Run `npm run build` and grep the produced bundle for the minified
     literal `debug:!0` (i.e., `debug: true`). It must be absent.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import PROJECT_ROOT  # noqa: E402

CONFIG_FILE = PROJECT_ROOT / "src" / "i18n" / "config.ts"
DIST_DIR = PROJECT_ROOT / "dist"


def test_config_uses_import_meta_env_dev():
    src = CONFIG_FILE.read_text(encoding="utf-8")
    assert "debug: import.meta.env.DEV" in src, (
        "src/i18n/config.ts must set debug from import.meta.env.DEV so that "
        "production builds inline it as false"
    )
    assert "debug: true" not in src, "config must not hardcode debug: true"


def test_production_bundle_has_no_debug_true():
    build = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert build.returncode == 0, (
        f"npm run build failed: stdout={build.stdout[-500:]!r} stderr={build.stderr[-500:]!r}"
    )

    js_files = list((DIST_DIR / "assets").glob("*.js"))
    assert js_files, f"expected built JS in {DIST_DIR / 'assets'}"

    for js in js_files:
        text = js.read_text(encoding="utf-8")
        assert "debug:!0" not in text, (
            f"{js.name} contains a minified `debug: true` literal — "
            "production build should compile import.meta.env.DEV to false"
        )
