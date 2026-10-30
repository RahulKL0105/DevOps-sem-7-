import docker

# Create a Docker client
client = docker.from_env()

# Run the container with the AppArmor option
container = client.containers.run(
    "flask-apparmor",
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")

# Test reading /etc/passwd
result = container.exec_run("cat /etc/passwd")
print(
    f"Attempt to read /etc/passwd: "
    f"Exit Code {result.exit_code}, "
    f"Output: {result.output.decode(errors='replace')}"
)

# Test executing /bin/bash
result = container.exec_run("/bin/bash")
print(
    f"Attempt to execute /bin/bash: "
    f"Exit Code {result.exit_code}, "
    f"Output: {result.output.decode(errors='replace')}"
)

# Stop and remove the container
container.stop()
container.remove()
print("Container stopped")
