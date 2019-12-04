import json
# Format an int with the correct number of leading zeros for standard reading
def format_int(n):
    f = str(n)
    while len(f) < 9:
        f = str(0) + f
    return f

# Sends a json dict over the passed socket
def send_json(j, sock):
    jstr = json.dumps(j)
    msg_len = format_int(len(jstr))
    sock.send(msg_len.encode('utf-8'))
    sock.send(jstr.encode('utf-8'))

# Receives a json from the passed socket and returns it as a dict
def recv_json(sock):
    msg_len= int(sock.recv(9).decode('utf-8'))
    msg = json.loads(sock.recv(msg_len).decode('utf-8'))
    return msg
