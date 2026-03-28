
import socket
import hashlib
import os
import sys
import time
import threading
import logging


def load_config(config_path):
    nodes = []
    with open(config_path, 'r') as f:
        lines = []
        for line in f:
            line = line.split('#')[0].strip()
            if line:
                lines.append(line)

    n_broadcasts = int(lines[0])

    for line in lines[1:]:
        parts = line.split()
        ip = parts[0]
        port = int(parts[1])
        nodes.append((ip, port))

    return n_broadcasts, nodes


def build_message(node_index):
    msg = bytearray(1024)

    msg[0] = node_index

    random_bytes = os.urandom(1003)
    msg[1:1004] = random_bytes

    sha1_hash = hashlib.sha1(msg[0:1004]).digest()
    msg[1004:1024] = sha1_hash

    return bytes(msg)

def verify_message(data):
    sha1_trimis = data[1004:1024]
    sha1_calculat = hashlib.sha1(data[0:1004]).digest()
    ok = (sha1_trimis == sha1_calculat)
    return sha1_trimis, sha1_calculat, ok

def send_message(sock, data, addr, error_logger):
    sock.settimeout(5)
    try:
        sock.sendto(data, addr)
        return True
    except socket.timeout:
        error_logger.error(f"TIMEOUT la trimitere catre {addr}")
        return False
    except Exception as e:
        error_logger.error(f"Eroare la trimitere catre {addr}: {e}")
        return False

def receive_message(sock, error_logger):

    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        if len(data) != 1024:
            error_logger.error(f"Mesaj cu lungime gresita: {len(data)} bytes (asteptat 1024)")
            return None, None
        return data, addr
    except socket.timeout:

        return None, None
    except OSError as e:
        if hasattr(e, 'winerror') and e.winerror == 10054:
            return None, None
        error_logger.error(f"Eroare la receptie: {e}")
        return None, None


def setup_loggers(node_index):
    msg_logger = logging.getLogger(f"messages_{node_index}")
    msg_logger.setLevel(logging.INFO)
    msg_handler = logging.FileHandler(f"node_{node_index}.log", mode='w')
    msg_handler.setFormatter(logging.Formatter('%(message)s'))
    msg_logger.addHandler(msg_handler)

    error_logger = logging.getLogger(f"errors_{node_index}")
    error_logger.setLevel(logging.ERROR)
    err_handler = logging.FileHandler(f"node_{node_index}_errors.log", mode='w')
    err_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    error_logger.addHandler(err_handler)

    return msg_logger, error_logger


def receiver_thread(sock, msg_logger, error_logger, expected_count, received_counter, stop_event):

    while not stop_event.is_set() and received_counter[0] < expected_count:
        data, addr = receive_message(sock, error_logger)

        if data is None:
            continue

        sha1_trimis, sha1_calculat, ok = verify_message(data)

        status = "OK" if ok else "FAIL"
        src_index = data[0]  

        sha1_trimis_hex = sha1_trimis.hex()
        sha1_calculat_hex = sha1_calculat.hex()

        log_line = f"{status} {src_index} {sha1_trimis_hex} {sha1_calculat_hex}"
        msg_logger.info(log_line)

        print(f"[Nod {src_index}→primit] {log_line}")

        received_counter[0] += 1

    print(f"[Receiver] Am primit toate {received_counter[0]} mesaje așteptate. Receiver oprit.")

def run_node(config_path, node_index):

    N, nodes = load_config(config_path)
    M = len(nodes)          
    expected_received = N * M  

    my_ip, my_port = nodes[node_index]

    print(f"[Nod {node_index}] Pornit pe {my_ip}:{my_port}")
    print(f"[Nod {node_index}] N={N} broadcasts, M={M} noduri, aștept {expected_received} mesaje total")

    msg_logger, error_logger = setup_loggers(node_index)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_ip, my_port))
    print(f"[Nod {node_index}] Socket legat pe {my_ip}:{my_port}")


    print(f"[Nod {node_index}] Aștept 30 secunde pentru sincronizare...")
    time.sleep(30)
    print(f"[Nod {node_index}] Start broadcasting!")

    received_counter = [0]  
    stop_event = threading.Event()

    recv_thread = threading.Thread(
        target=receiver_thread,
        args=(sock, msg_logger, error_logger, expected_received, received_counter, stop_event),
        daemon=True  
    )
    recv_thread.start()

    for i in range(N):
        msg = build_message(node_index)

        for idx, (ip, port) in enumerate(nodes):
            success = send_message(sock, msg, (ip, port), error_logger)
            if not success:
                error_logger.error(f"Broadcast {i+1}/{N} catre nod {idx} ({ip}:{port}) ESUAT")

        time.sleep(0.05)


        if (i + 1) % max(1, N // 10) == 0:
            print(f"[Nod {node_index}] Trimis {i+1}/{N} broadcasts")

    print(f"[Nod {node_index}] Am trimis toate {N} broadcasts. Aștept să primesc {expected_received} mesaje...")


    recv_thread.join(timeout=300)  

    stop_event.set()
    sock.close()

    print(f"[Nod {node_index}] FINALIZAT. Primit: {received_counter[0]}/{expected_received}")
    print(f"[Nod {node_index}] Log-ul mesajelor: node_{node_index}.log")
    print(f"[Nod {node_index}] Log-ul erorilor:  node_{node_index}_errors.log")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilizare: python bcastnode.py <config_file> <node_index>")
        print("Exemplu:   python bcastnode.py config.txt 3")
        sys.exit(1)

    config_path = sys.argv[1]
    node_index = int(sys.argv[2])

    run_node(config_path, node_index)