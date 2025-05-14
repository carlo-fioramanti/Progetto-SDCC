import subprocess
import time


def docker_compose_build():
    
    subprocess.run(["docker", "compose", "build", "--quiet"], check=True)

    
def docker_compose_up():
    
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

def wait_for_container(container_name, timeout=60):
    
    for _ in range(timeout):
        result = subprocess.run(
            ["docker", "ps", "-f", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )
        if "Up" in result.stdout:
            
            return True
        time.sleep(1)
    
    return False

def exec_python_in_container(container_name, script_name):
    
    try:
        subprocess.run([
            "docker", "exec", "-it", container_name,
            "bash", "-c", f"python {script_name}"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Interruzione ricevuta durante l'esecuzione nel container.")

def docker_compose_down():
    
    subprocess.run(["docker", "compose", "down"])

if __name__ == "__main__":
    try:
        docker_compose_build()
        docker_compose_up()
        if wait_for_container("frontend"):
            exec_python_in_container("frontend", "appFrontend.py")
        else:
            print("🚫 Errore: impossibile accedere al container.")
    except KeyboardInterrupt:
        print("\n🛑 Interruzione manuale ricevuta.")
    finally:
        docker_compose_down()
