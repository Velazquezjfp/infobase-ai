"""TC-S001-NFR-001-07 — built image is under 800 MiB."""
import subprocess


def test_image_size_under_800_mib(built_image):
    result = subprocess.run(
        ["docker", "inspect", built_image, "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    size_bytes = int(result.stdout.strip())
    size_mib = size_bytes / (1024 ** 2)
    assert size_mib < 800, f"Image size {size_mib:.1f} MiB exceeds 800 MiB limit"
