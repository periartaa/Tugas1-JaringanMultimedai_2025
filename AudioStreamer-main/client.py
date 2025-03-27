import logging
import time
import socket
import argparse
import signal
import pyaudio
import sys
import queue

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
packets_sent = 0
start_time = time.time()

def update_analytics():
    global packets_sent
    packets_sent += 1

def display_analytics():
    elapsed_time = time.time() - start_time
    print(f"Packets Sent: {packets_sent}, Uptime: {elapsed_time:.2f}s")
    logging.info(f"Packets Sent: {packets_sent}, Uptime: {elapsed_time:.2f}s")

# Signal handler
def handler(signum, frame):
    global recordStream, client_socket
    log_event("Exiting the program")
    try:
        recordStream.stop_stream()
        recordStream.close()
        client_socket.close()
    except Exception as e:
        log_event(f"Error during cleanup: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

# Command line arguments
parser = argparse.ArgumentParser(description="AudioStream client")
parser.add_argument("--protocol", required=False, default='udp', choices=['udp', 'tcp'])
parser.add_argument("--host", required=False, default="localhost")
parser.add_argument("--port", required=False, type=int, default=12345)
parser.add_argument("--size", required=False, type=int, default=10, choices=range(10, 151, 10))
args = parser.parse_args()

log_event(f"Client started with Protocol: {args.protocol.upper()}, Host: {args.host}, Port: {args.port}, Size: {args.size} ms")

# Audio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 441  # 10 ms
NUMCHUNKS = int(args.size / 10)

sendQueue = queue.Queue()
silenceData = (0).to_bytes(2) * CHUNK * NUMCHUNKS
sequenceNumber = 0

def record(data, frame_count, time_info, status):
    sendQueue.put(data)
    return silenceData, pyaudio.paContinue

try:
    pyaudioObj = pyaudio.PyAudio()
    recordStream = pyaudioObj.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                   frames_per_buffer=NUMCHUNKS * CHUNK, stream_callback=record)
    log_event("PyAudio Device Initialized")
except pyaudio.PyAudioError as e:
    log_event(f"PyAudio Error: {e}")
    sys.exit(1)

# Socket setup
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if args.protocol == 'udp' else socket.SOCK_STREAM)
    if args.protocol == 'tcp':
        client_socket.connect((args.host, args.port))
except socket.error as e:
    log_event(f"Socket Error: {e}")
    sys.exit(1)

destination = (args.host, args.port)

def sendAudio():
    global sequenceNumber
    try:
        audioData = sendQueue.get(timeout=1)
        seqBytes = sequenceNumber.to_bytes(2, byteorder="little", signed=False)
        sendData = seqBytes + audioData

        update_analytics()
        log_event(f"Sending Sequence #{sequenceNumber} ({len(sendData)} bytes)")

        if args.protocol == 'udp':
            client_socket.sendto(sendData, destination)
        else:
            client_socket.sendall(sendData)

        sequenceNumber = (sequenceNumber + 1) % 65536
    except queue.Empty:
        log_event("Warning: No audio data in queue!")
    except socket.error as e:
        log_event(f"Socket Error while sending: {e}")

while True:
    sendAudio()
    if time.time() - start_time > 10:
        display_analytics()