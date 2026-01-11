import pandas as pd
import socket, struct, random, time, sys

print("--- Starting Project (Updated Version) ---")

# 1. Create CSV with app names (per requirements)
csv_filename = 'group01_http_input.csv'
data = {
    'msg_id': [1, 2, 3],
    'app_protocol': ['HTTP', 'HTTP', 'HTTP'],
    'src_app': ['client_browser', 'web_server', 'client_browser'],
    'dst_app': ['web_server', 'client_browser', 'web_server'],
    'message': ['GET /index.html', 'HTTP/1.1 200 OK', 'POST /login'],
    'timestamp': [0.015, 0.020, 0.045]
}

df = pd.DataFrame(data)
df.to_csv(csv_filename, index=False)
print(f"1. CSV file created: {csv_filename}")

# Map app names to ports
port_map = {
    'client_browser': 12345,
    'web_server': 80
}

# 2. Networking Functions
def checksum(data: bytes) -> int:
    if len(data) % 2: data += b'\0'
    res = sum(struct.unpack('!%dH' % (len(data)//2), data))
    while res >> 16: res = (res & 0xFFFF) + (res >> 16)
    return ~res & 0xFFFF

def build_ip_header(src_ip, dst_ip, payload_len, proto=socket.IPPROTO_TCP):
    ip_header = struct.pack('!BBHHHBBH4s4s', (4<<4)+5, 0, 20+payload_len, random.randint(0,65535), 0, 64, proto, 0, socket.inet_aton(src_ip), socket.inet_aton(dst_ip))
    return struct.pack('!BBHHHBBH4s4s', (4<<4)+5, 0, 20+payload_len, random.randint(0,65535), 0, 64, proto, checksum(ip_header), socket.inet_aton(src_ip), socket.inet_aton(dst_ip))

def build_tcp_header(src_ip, dst_ip, src_port, dst_port, payload=b'', flags=0x02):
    tcp_header = struct.pack('!HHLLBBHHH', src_port, dst_port, random.randint(0, 4294967295), 0, (5<<4), flags, 65535, 0, 0)
    pseudo_hdr = struct.pack('!4s4sBBH', socket.inet_aton(src_ip), socket.inet_aton(dst_ip), 0, socket.IPPROTO_TCP, len(tcp_header)+len(payload))
    return struct.pack('!HHLLBBH H H', src_port, dst_port, random.randint(0, 4294967295), 0, (5<<4), flags, 65535, checksum(pseudo_hdr + tcp_header + payload), 0)

# 3. Execution
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()
    
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    
    messages = pd.read_csv(csv_filename)
    
    print("3. Sending packets...")
    for i, row in messages.iterrows():
        msg_bytes = str(row['message']).encode('utf-8')
        
        # Translate app names to ports
        src_p = port_map[row['src_app']]
        dst_p = port_map[row['dst_app']]
        
        packet = build_ip_header(my_ip, my_ip, 20+len(msg_bytes)) + \
                 build_tcp_header(my_ip, my_ip, src_p, dst_p, msg_bytes, flags=0x18) + \
                 msg_bytes
                 
        raw_socket.sendto(packet, (my_ip, 0))
        print(f"   -> Sent: {row['message']} (From {row['src_app']} to {row['dst_app']})")
        time.sleep(1)

    print("\nSUCCESS! CSV updated and packets sent.")

except PermissionError:
    print("\n!!! ERROR: Run as Administrator !!!")
except Exception as e:
    print(f"\nError: {e}")

input("\nPress Enter to exit...")