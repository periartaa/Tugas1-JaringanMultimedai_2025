import logging
import time
import socket
import argparse
import signal
import pyaudio
import sys
import traceback

import logging
from logging.handlers import RotatingFileHandler

# Setup Logging dengan RotatingFileHandler
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Simpan log ke file dengan batasan ukuran 5MB, simpan 3 backup log lama
file_handler = RotatingFileHandler("audio_stream.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Logging dimulai...")


logging.info("Log test: File logging should work.")



class AdvancedAudioServer:
    def __init__(self, protocol='udp', port=12345, size=10):
        self.protocol = protocol
        self.port = port
        self.size = size
        
        # Audio Configuration
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 441  # 10 ms
        self.NUMCHUNKS = int(self.size / 10)
        
        # Variabel untuk tracking
        self.last_received_sequence = -1
        self.total_packets = 0
        self.lost_packets = 0
        
        self.setup_socket()
        self.setup_audio()

    def setup_socket(self):
        try:
            # Pilih tipe socket berdasarkan protokol
            socket_type = socket.SOCK_DGRAM if self.protocol == 'udp' else socket.SOCK_STREAM
            self.server_socket = socket.socket(socket.AF_INET, socket_type)
            
            # Izinkan reuse address untuk menghindari konflik port
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind ke semua interface
            self.server_socket.bind(('0.0.0.0', self.port))
            
            # Untuk TCP, listen
            if self.protocol == 'tcp':
                self.server_socket.listen(1)
                logging.info(f"Menunggu koneksi TCP di port {self.port}")
                self.connection, self.client_address = self.server_socket.accept()
                logging.info(f"Koneksi dari {self.client_address}")
            
            logging.info(f"Server siap dengan protokol {self.protocol}")
        
        except Exception as e:
            logging.error(f"Kesalahan setup socket: {e}")
            logging.error(traceback.format_exc())
            sys.exit(1)

    def setup_audio(self):
        try:
            self.pyaudio = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK * self.NUMCHUNKS
            )
        except Exception as e:
            logging.error(f"Kesalahan setup audio: {e}")
            sys.exit(1)

    def receive_data(self):
        try:
            # Ukuran paket: sequence number (2 byte) + audio data
            max_packet_size = self.CHUNK * self.NUMCHUNKS * 2 + 2
            
            if self.protocol == 'udp':
                data, client_address = self.server_socket.recvfrom(max_packet_size)
                logging.debug(f"Terima UDP dari {client_address}")
            else:
                data = self.connection.recv(max_packet_size)
                if not data:
                    logging.error("Koneksi terputus")
                    return False
            
            # Ekstrak sequence number
            sequence_number = int.from_bytes(data[:2], byteorder='little')
            audio_data = data[2:]
            
            # Debug sequence number
            logging.debug(f"Sequence Number: {sequence_number}")
            logging.debug(f"Panjang data: {len(data)} byte")
            
            # Update tracking
            self.total_packets += 1
            
            # Cek urutan
            if self.last_received_sequence == -1:
                self.last_received_sequence = sequence_number
            
            if sequence_number != self.last_received_sequence + 1:
                self.lost_packets += 1
                logging.warning(
                    f"Paket tidak berurutan! "
                    f"Terakhir: {self.last_received_sequence}, "
                    f"Sekarang: {sequence_number}"
                )
            
            # Update last sequence
            self.last_received_sequence = sequence_number
            
            # Putar audio (opsional)
            self.audio_stream.write(audio_data)
            
            # Tampilkan statistik periodik
            if self.total_packets % 100 == 0:
                loss_rate = (self.lost_packets / self.total_packets) * 100
                logging.info(
                    f"Statistik: Total={self.total_packets}, "
                    f"Hilang={self.lost_packets}, "
                    f"Loss Rate={loss_rate:.2f}%"
                )
            
            return True
        
        except Exception as e:
            logging.error(f"Kesalahan menerima data: {e}")
            logging.error(traceback.format_exc())
            return False

    def run(self):
        logging.info("Server mulai berjalan...")
        try:
            while True:
                if not self.receive_data():
                    break
        except KeyboardInterrupt:
            logging.info("Server dihentikan")
        finally:
            # Bersihkan sumber daya
            if self.protocol == 'tcp':
                self.connection.close()
            self.server_socket.close()
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.pyaudio.terminate()

def main():
    parser = argparse.ArgumentParser(description="Audio Streaming Server")
    parser.add_argument("--protocol", choices=['udp', 'tcp'], default='udp')
    parser.add_argument("--port", type=int, default=12345)
    parser.add_argument("--size", type=int, default=10, choices=range(10, 151, 10))
    args = parser.parse_args()

    server = AdvancedAudioServer(
        protocol=args.protocol, 
        port=args.port, 
        size=args.size
    )
    server.run()

if __name__ == "__main__":
    main()