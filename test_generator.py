from generator import generate_docker_config

try:
    print("Testing generate_docker_config...")
    result = generate_docker_config("I have a FastAPI app.")
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {e}")
