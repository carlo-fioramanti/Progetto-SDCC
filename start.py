import subprocess
import time


def docker_compose_build():
    print("🔧 Eseguo: docker compose build")
    subprocess.run(["docker", "compose", "build"], check=True)

def docker_compose_up():
    print("🚀 Eseguo: docker compose up -d")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

def wait_for_container(container_name, timeout=60):
    print(f"⏳ Aspetto che il container '{container_name}' sia in esecuzione...")
    for _ in range(timeout):
        result = subprocess.run(
            ["docker", "ps", "-f", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )
        if "Up" in result.stdout:
            print(f"✅ Container '{container_name}' è attivo.")
            return True
        time.sleep(1)
    print(f"❌ Timeout: il container '{container_name}' non è attivo.")
    return False

def exec_python_in_container(container_name, script_name):
    print(f"🐍 Eseguo: python {script_name} dentro il container '{container_name}' (CTRL+C per uscire)")
    try:
        subprocess.run([
            "docker", "exec", "-it", container_name,
            "bash", "-c", f"python {script_name}"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Interruzione ricevuta durante l'esecuzione nel container.")

def docker_compose_down():
    print("🧹 Pulizia: docker compose down")
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
