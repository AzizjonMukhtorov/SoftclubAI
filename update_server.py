import paramiko
from scp import SCPClient
import time

HOST = "157.180.29.248"
USER = "soft"
PASS = "soft@2025"

def update():
    print(f"🚀 Updating {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)

    # 1. Upload modified files
    print("[1/3] Uploading new files...")
    with SCPClient(client.get_transport()) as scp:
        # Uploading to home first avoids permission issues
        scp.put("app/api/schemas.py", remote_path="schemas.py")
        scp.put("app/api/dashboard_routes.py", remote_path="dashboard_routes.py")
        scp.put("app/data/db_data.py", remote_path="db_data.py")
        scp.put("main.py", remote_path="main.py")

    # 2. Move to destination and restart
    print("[2/3] Applying changes and restarting service...")
    
    # Chained commands to ensure order
    cmds = [
        f"echo '{PASS}' | sudo -S mv ~/schemas.py /opt/srm-softclub/app/api/schemas.py",
        f"echo '{PASS}' | sudo -S mv ~/dashboard_routes.py /opt/srm-softclub/app/api/dashboard_routes.py",
        f"echo '{PASS}' | sudo -S mv ~/db_data.py /opt/srm-softclub/app/data/db_data.py",
        f"echo '{PASS}' | sudo -S mv ~/main.py /opt/srm-softclub/main.py",
        f"echo '{PASS}' | sudo -S systemctl restart srm-softclub"
    ]
    
    for cmd in cmds:
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
             print(f"Error executing {cmd}: {stderr.read().decode()}")

    print("[3/3] Verifying update...")
    time.sleep(3) # Wait for restart
    
    stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8001/api/dashboard | head -c 100")
    response = stdout.read().decode()
    
    if "riskDistribution" in response:
        print(f"✅ SUCCESS! Response: {response}...")
    else:
        print(f"❌ FAIL. Response: {response}")
        print(f"Logs: ")
        stdin, stdout, stderr = client.exec_command(f"echo '{PASS}' | sudo -S journalctl -u srm-softclub -n 20 --no-pager")
        print(stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    update()
