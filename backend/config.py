import os
import sys
import socket
import threading
import select
from pathlib import Path
from dotenv import load_dotenv
import paramiko

# Load environment variables
BACKEND_DIR = Path(__file__).parent
env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

MODEL_MODE = os.getenv("MODEL_MODE", "local").lower().strip()

# Cloud settings
CLOUD_SSH_HOST = os.getenv("CLOUD_SSH_HOST", "")
CLOUD_SSH_USER = os.getenv("CLOUD_SSH_USER", "root")
CLOUD_SSH_KEY_PATH = os.getenv("CLOUD_SSH_KEY_PATH", "")
CLOUD_SSH_KEY = os.getenv("CLOUD_SSH_KEY", "")
CLOUD_SSH_PASSPHRASE = os.getenv("CLOUD_SSH_PASSPHRASE", "")
CLOUD_OLLAMA_PORT = int(os.getenv("CLOUD_OLLAMA_PORT", "11434"))

# Model Configurations
LOCAL_OLLAMA_URL = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434")
LOCAL_GRANITE_MODEL = os.getenv("LOCAL_GRANITE_MODEL", "granite4:latest")
CLOUD_GRANITE_MODEL = os.getenv("CLOUD_GRANITE_MODEL", "granite3-dense:2b")
CLOUD_QWEN_MODEL = os.getenv("CLOUD_QWEN_MODEL", "moondream:latest")

# Port for local end of SSH tunnel
TUNNEL_LOCAL_PORT = 11435
TUNNEL_REMOTE_PORT = 11434

# Global tunnel server and thread handle
tunnel_server = None
tunnel_thread = None
ssh_client = None
tunnel_active = False

def ssh_forwarder(chan, sock):
    """Bidirectionally copy data between SSH channel and local socket"""
    try:
        while True:
            r, w, x = select.select([chan, sock], [], [])
            if chan in r:
                data = chan.recv(4096)
                if not data:
                    break
                sock.sendall(data)
            if sock in r:
                data = sock.recv(4096)
                if not data:
                    break
                chan.sendall(data)
    except Exception:
        pass
    finally:
        try:
            chan.close()
        except:
            pass
        try:
            sock.close()
        except:
            pass

def tunnel_listen_loop(server_sock, transport):
    """Listen for local connections and forward them over SSH transport"""
    global tunnel_active
    while tunnel_active:
        try:
            # Set timeout so we can exit the loop if inactive
            server_sock.settimeout(1.0)
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            
            # Open direct-tcpip channel to remote Ollama port
            chan = transport.open_channel(
                "direct-tcpip",
                ("127.0.0.1", TUNNEL_REMOTE_PORT),
                addr
            )
            if chan is None:
                client_sock.close()
                continue
                
            # Spawn copy thread
            t = threading.Thread(target=ssh_forwarder, args=(chan, client_sock), daemon=True)
            t.start()
        except Exception as e:
            if tunnel_active:
                print(f"[SSH Tunnel Error] Loop exception: {e}")

def start_ssh_tunnel():
    """Establish the SSH connection and start local forwarding socket"""
    global tunnel_server, tunnel_thread, ssh_client, tunnel_active
    
    if MODEL_MODE != "cloud":
        return True
        
    print(f"\n[SSH Tunnel] Initializing connection to {CLOUD_SSH_HOST}...")
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load private key from environment variable CLOUD_SSH_KEY or CLOUD_SSH_KEY_PATH file
        pkey = None
        
        # 1. Try to load from env variable string CLOUD_SSH_KEY
        if CLOUD_SSH_KEY:
            import io
            raw_key = CLOUD_SSH_KEY.strip()
            if "\\n" in raw_key:
                raw_key = raw_key.replace("\\n", "\n")
            for key_class in [paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey]:
                try:
                    pkey = key_class.from_private_key(
                        io.StringIO(raw_key),
                        password=CLOUD_SSH_PASSPHRASE or None
                    )
                    if pkey:
                        print("[SSH Tunnel] Successfully loaded private key from CLOUD_SSH_KEY env var.")
                        break
                except Exception:
                    continue
        
        # 2. Fallback to reading CLOUD_SSH_KEY_PATH file
        if not pkey and CLOUD_SSH_KEY_PATH and os.path.exists(CLOUD_SSH_KEY_PATH):
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(
                    CLOUD_SSH_KEY_PATH, 
                    password=CLOUD_SSH_PASSPHRASE or None
                )
            except Exception:
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(
                        CLOUD_SSH_KEY_PATH, 
                        password=CLOUD_SSH_PASSPHRASE or None
                    )
                except Exception as e:
                    print(f"[SSH Tunnel Error] Failed loading private key from file: {e}")
                    
        if pkey:
            ssh_client.connect(
                CLOUD_SSH_HOST, 
                username=CLOUD_SSH_USER, 
                pkey=pkey, 
                timeout=15
            )
        else:
            ssh_client.connect(
                CLOUD_SSH_HOST, 
                username=CLOUD_SSH_USER, 
                password=CLOUD_SSH_PASSPHRASE, 
                timeout=15
            )
            
        print("[SSH Tunnel] SSH connection established successfully.")
        
        # Bind local forwarding port
        tunnel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tunnel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tunnel_server.bind(("127.0.0.1", TUNNEL_LOCAL_PORT))
        tunnel_server.listen(100)
        
        tunnel_active = True
        transport = ssh_client.get_transport()
        
        # Start tunnel thread
        tunnel_thread = threading.Thread(
            target=tunnel_listen_loop,
            args=(tunnel_server, transport),
            daemon=True
        )
        tunnel_thread.start()
        
        print(f"[SSH Tunnel] Active! Forwarding local port {TUNNEL_LOCAL_PORT} -> remote {TUNNEL_REMOTE_PORT}")
        return True
    except Exception as e:
        print(f"[SSH Tunnel Error] Failed to establish tunnel: {e}")
        return False

def stop_ssh_tunnel():
    """Tear down local forwarding socket and SSH connection"""
    global tunnel_server, tunnel_thread, ssh_client, tunnel_active
    
    print("\n[SSH Tunnel] Stopping tunnel...")
    tunnel_active = False
    
    if tunnel_server:
        try:
            tunnel_server.close()
        except:
            pass
        tunnel_server = None
        
    if ssh_client:
        try:
            ssh_client.close()
        except:
            pass
        ssh_client = None
        
    print("[SSH Tunnel] Stopped.")

# Made with Bob
