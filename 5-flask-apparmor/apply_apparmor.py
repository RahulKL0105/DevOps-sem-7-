import docker

client = docker.from_env()

print("Building Docker image...")
client.images.build(path=".", tag="flask-apparmor")

print("Starting container...")
container = client.containers.run(
    "flask-apparmor",
    ports={"5000/tcp": 5001},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")

container_info = client.api.inspect_container(container.id)

print("AppArmor profile:", container_info.get("AppArmorProfile"))
print(
    "Security options:",
    container_info["HostConfig"].get("SecurityOpt")
)

print("Container logs:")
print(container.logs().decode())

container.stop()
container.remove()
print("Container stopped and removed.")
