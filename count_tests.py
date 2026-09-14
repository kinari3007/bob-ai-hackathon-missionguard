"""Run pytest with verbose output to get exact test names and count."""
import json, subprocess, sys

root = r"C:\IBM Hackathone\bob-ai-hackathone-missionguard"
py = sys.executable

proc = subprocess.run(
    [py, "-m", "pytest", "-v", "--tb=short", "--no-header"],
    capture_output=True, text=True,
    cwd=r"C:\IBM Hackathone\bob-ai-hackathon-missionguard"
)

lines = (proc.stdout or "").splitlines()
# grab last 80 lines — summary + test names
tail = "\n".join(lines[-80:])

with open(r"C:\IBM Hackathone\bob-ai-hackathon-missionguard\count_tests_out.txt", "w") as f:
    f.write(tail)
    if proc.stderr:
        f.write("\n--- STDERR ---\n")
        f.write(proc.stderr[-500:])
