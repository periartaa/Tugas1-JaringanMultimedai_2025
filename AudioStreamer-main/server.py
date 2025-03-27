import logging
import time
import socket
import argparse
import signal
import pyaudio
import sys

# Setup Logging
logging.basicConfig(
    filename="audio_stream.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(event):
    logging.info(event)
    print(event)

# Analytics Variables
packets_received = 0
lost_packets = 0
start_time = time.time()

def update_analytics(expected_seq, received_seq):
    global packets_received, lost_packets
    packets_received += 1
    if expected_seq != received_seq:
        lost_packets += 1

def display_analytics():
    elapsed_time = time.time() - start_time
    loss_rate = (lost_packets / packets_received * 100) if packets_received else 0
    print(f"Packets Received: {packets_received}, Lost Packets: {lost_packets}, Loss Rate: {loss_rate:.2f}%, Uptime: {elapsed_time:.2f}s")
    logging.info(f"Packets Received: {packets_received}, Lost Packets: {lost_packets}, Loss Rate: {loss_rate:.2f}%, Uptime: {elapsed_time:.2f}s")

# Signal handler
def handler(signum, frame):
    global playStream, server_socket
    log_event("Exiting the program")
    try:
        playStream.stop_stream()
        playStream.close()
        server_socket.close()
    except Exception as e:
        log_event(f"Error during cleanup: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

parser = argparse.ArgumentParser(description="AudioStream server")
parser.add_argument("--protocol", required=False, default='udp', choices=['udp', 'tcp'])
parser.add_argument("--port", required=False, type=int, default=12345)
parser.add_argument("--size", required=False, type=int, default=10, choices=range(10, 151, 10))
args = parser.parse_args()

log_event(f"Server started with Protocol: {args.protocol.upper()}, Port: {args.port}, Size: {args.size} ms")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 441
NUMCHUNKS = int(args.size / 10)
silenceData = (0).to_bytes(2) * CHUNK * NUMCHUNKS

try:
    pyaudioObj = pyaudio.PyAudio()
    playStream = pyaudioObj.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK * NUMCHUNKS)
    log_event("PyAudio Device Initialized")
except pyaudio.PyAudioError as e:
    log_event(f"PyAudio Error: {e}")
    sys.exit(1)

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if args.protocol == 'udp' else socket.SOCK_STREAM)
    server_socket.bind(('', args.port))
    if args.protocol == 'tcp':
        server_socket.listen()
        connection, source = server_socket.accept()
        log_event(f"TCP Connection established with {source}")
except socket.error as e:
    log_event(f"Socket Error: {e}")
    sys.exit(1)

expectedSeqNum = 0

def recvData():
    global expectedSeqNum
    try:
        log_event(f"Expecting Sequence #{expectedSeqNum}")

        if args.protocol == 'udp':
            data, _ = server_socket.recvfrom(CHUNK * NUMCHUNKS * 2 + 2)
        else:
            data = connection.recv(CHUNK * NUMCHUNKS * 2 + 2)
            while len(data) < CHUNK * NUMCHUNKS * 2 + 2:
                chunk = connection.recv(CHUNK * NUMCHUNKS * 2 + 2 - len(data))
                if not chunk:
                    raise socket.error("Connection closed by client")
                data += chunk

        sequenceNumber = int.from_bytes(data[:2], byteorder="little", signed=False)
        audioData = data[2:]

        update_analytics(expectedSeqNum, sequenceNumber)

        if expectedSeqNum == sequenceNumber:
            log_event(f"Received Sequence #{sequenceNumber} ({len(data)} bytes)")
            playStream.write(audioData)
            expectedSeqNum = (expectedSeqNum + 1) % 65536
        else:
            log_event(f"Out of sequence! Expected {expectedSeqNum}, got {sequenceNumber}")
            playStream.write(silenceData)
            if sequenceNumber > expectedSeqNum:
                expectedSeqNum = sequenceNumber + 1
    except socket.error as e:
        log_event(f"Socket Error while receiving: {e}")
    except Exception as e:
        log_event(f"Unexpected Error: {e}")

while True:
    recvData()
    if time.time() - start_time > 10:
        display_analytics()