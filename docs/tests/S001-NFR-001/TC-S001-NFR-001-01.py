"""TC-S001-NFR-001-01 — docker build exits 0 on a clean checkout."""


def test_build_succeeds(docker_build):
    assert docker_build.returncode == 0, (
        f"docker build exited {docker_build.returncode}.\n"
        f"stderr:\n{docker_build.stderr[-1000:]}"
    )
