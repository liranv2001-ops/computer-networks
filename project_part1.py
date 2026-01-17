import csv
import socket
import time
import sys
from collections import Counter

# --- 1. Define Packet Object ---
class PacketObject:
    def __init__(self, app_protocol, src_ip, src_port, dst_ip, dst_port, message, timestamp):
        self.app_protocol = app_protocol
        self.src_ip = src_ip
        self.src_port = int(src_port)
        self.dst_ip = dst_ip
        self.dst_port = int(dst_port)
        self.message = message
        self.timestamp = timestamp

# --- 2. Load Data (Using built-in CSV module) ---
def load_packets(csv_file):
    print(f"Loading data from {csv_file}...")
    packets = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pkt = PacketObject(
                    row['app_protocol'], row['src_ip'], row['src_port'],
                    row['dst_ip'], row['dst_port'], row['message'], row['timestamp']
                )
                packets.append(pkt)
        print(f"Successfully loaded {len(packets)} packets.")
        return packets
    except FileNotFoundError:
        print("Error: CSV file not found!")
        return []

# --- 3. Simple Console Analysis ---
def analyze_data(packets):
    print("\n--- Data Analysis ---")
    protocols = [p.app_protocol for p in packets]
    counts = Counter(protocols)
    
    print("Protocol Distribution:")
    for proto, count in counts.items():
        print(f" - {proto}: {count} packets")
    
    print("(Note: Since we are running in 'Native Mode' without libraries,")
    print(" please use Excel to create the Pie Chart and Bar Graph for the report.)")

# --- 4. Traffic Generation ---
def generate_traffic(packets):
    print("\n--- Starting Traffic Generation ---")
    print("Make sure Wireshark is capturing on 'Adapter for loopback'!")
    time.sleep(2)

    for pkt in packets:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            target_ip = "127.0.0.1"
            target_port = pkt.src_port

            print(f"Sending {pkt.app_protocol} packet -> Port {target_port}")
            
            result = sock.connect_ex((target_ip, target_port))
            
            # Special handling for Port 12345 (The POST request)
            if pkt.src_port == 12345:
                 listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                 listener.bind(('127.0.0.1', 12345))
                 listener.listen(1)
                 
                 sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                 sender.connect(('127.0.0.1', 12345))
                 
                 conn, addr = listener.accept()
                 sender.send(pkt.message.encode('utf-8'))
                 
                 sender.close()
                 conn.close()
                 listener.close()
            else:
                sock.send(pkt.message.encode('utf-8'))

            sock.close()
            time.sleep(1)

        except Exception as e:
            pass # Ignore errors, we just want traffic on the wire

    print("\nDone! Traffic sent.")

if __name__ == "__main__":
    # Ensure this matches your CSV filename exactly
    csv_filename = 'group01_http_input.csv' 
    
    packets_list = load_packets(csv_filename)
    if packets_list:
        analyze_data(packets_list)
        generate_traffic(packets_list)