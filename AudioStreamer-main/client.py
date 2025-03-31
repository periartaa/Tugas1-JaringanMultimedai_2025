import logging
import time
import socket
import argparse
import signal
import pyaudio
import sys
import queue
import wave
import os
import threading

# Setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("audio_stream.log", mode="w"),  # mode "w" untuk overwrite jika ada
        logging.StreamHandler()  # Tampilkan juga di console
    ]
)

logging.info("Log test: File logging should work.")


class AudioClient:
    def __init__(self, protocol='udp', host="localhost", port=12345, size=10):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.size = size
        
        # Buat folder Recording jika belum ada
        self.recording_folder = "Recording"
        os.makedirs(self.recording_folder, exist_ok=True)
        
        # Audio Configuration
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 441  # 10 ms
        self.NUMCHUNKS = int(self.size / 10)
        
        # Rekaman
        self.recorded_frames = []
        self.is_recording = False
        self.stop_event = threading.Event()
        
        # Queue dan Network
        self.sendQueue = queue.Queue()
        self.sequenceNumber = 0
        
        # Setup
        self.setup_audio()
        self.setup_socket()

    def setup_audio(self):
        try:
            self.pyaudioObj = pyaudio.PyAudio()
            self.silenceData = (0).to_bytes(2) * self.CHUNK * self.NUMCHUNKS
            
            self.recordStream = self.pyaudioObj.open(
                format=self.FORMAT, 
                channels=self.CHANNELS, 
                rate=self.RATE, 
                input=True,
                frames_per_buffer=self.NUMCHUNKS * self.CHUNK, 
                stream_callback=self._record_callback
            )
            print("Audio device initialized.")
        except pyaudio.PyAudioError as e:
            print(f"PyAudio Error: {e}")
            sys.exit(1)

    def setup_socket(self):
        try:
            self.client_socket = socket.socket(
                socket.AF_INET, 
                socket.SOCK_DGRAM if self.protocol == 'udp' else socket.SOCK_STREAM
            )
            if self.protocol == 'tcp':
                self.client_socket.connect((self.host, self.port))
            print(f"Socket initialized with {self.protocol.upper()} protocol")
        except socket.error as e:
            print(f"Socket Error: {e}")
            sys.exit(1)

    def start_recording(self, duration=None):
        """Mulai menyimpan frame audio"""
        self.is_recording = True
        self.recorded_frames = []
        print("Recording started.")
        
        # Jika ada durasi, gunakan threading untuk stop otomatis
        if duration:
            threading.Thread(target=self._stop_after_duration, args=(duration,), daemon=True).start()

    def _stop_after_duration(self, duration):
        """Stop rekaman setelah durasi tertentu"""
        time.sleep(duration)
        if self.is_recording:
            self.stop_recording()

    def stop_recording(self, filename=None):
        """Hentikan rekaman dan simpan file"""
        if not self.is_recording:
            print("No active recording to stop.")
            return
        
        self.is_recording = False
        
        # Generate filename jika tidak disediakan
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.recording_folder, f"recording_{timestamp}.wav")
        else:
            # Pastikan filename memiliki path lengkap ke folder Recording
            filename = os.path.join(self.recording_folder, filename)
        
        # Simpan rekaman
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.pyaudioObj.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.recorded_frames))
            wf.close()
            
            print(f"Recording saved as {filename}")
            print(f"Duration: {len(self.recorded_frames) * self.CHUNK / self.RATE:.2f} seconds")
            print(f"File size: {os.path.getsize(filename) / 1024:.2f} KB")
        except Exception as e:
            print(f"Error saving recording: {e}")

    def _record_callback(self, data, frame_count, time_info, status):
        """Callback untuk merekam audio"""
        # Tambahkan ke queue untuk streaming
        self.sendQueue.put(data)
        
        # Simpan frame jika sedang merekam
        if self.is_recording:
            self.recorded_frames.append(data)
        
        return self.silenceData, pyaudio.paContinue

    def send_audio(self):
        """Kirim data audio"""
        try:
            audioData = self.sendQueue.get(timeout=1)
            seqBytes = self.sequenceNumber.to_bytes(2, byteorder="little", signed=False)
            sendData = seqBytes + audioData

            destination = (self.host, self.port)
            if self.protocol == 'udp':
                self.client_socket.sendto(sendData, destination)
            else:
                self.client_socket.sendall(sendData)

            self.sequenceNumber = (self.sequenceNumber + 1) % 65536
        except queue.Empty:
            pass
        except socket.error as e:
            print(f"Socket Error while sending: {e}")

    def run(self):
        """Jalankan streaming audio"""
        try:
            while not self.stop_event.is_set():
                self.send_audio()
        except Exception as e:
            print(f"Error in client run: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Bersihkan sumber daya"""
        print("Cleaning up resources...")
        try:
            self.recordStream.stop_stream()
            self.recordStream.close()
            self.pyaudioObj.terminate()
            self.client_socket.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    parser = argparse.ArgumentParser(description="Audio Streaming Client")
    parser.add_argument("--protocol", default='udp', choices=['udp', 'tcp'])
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=12345)
    parser.add_argument("--size", type=int, default=10, choices=range(10, 151, 10))
    args = parser.parse_args()

    client = AudioClient(
        protocol=args.protocol, 
        host=args.host, 
        port=args.port, 
        size=args.size
    )

    # Contoh cara menggunakan
    print("\nPilih aksi:")
    print("1. Rekam dengan durasi tertentu")
    print("2. Rekam dan stop manual")
    
    choice = input("Masukkan pilihan (1/2): ")
    
    # Thread untuk menjalankan streaming
    streaming_thread = threading.Thread(target=client.run, daemon=True)
    streaming_thread.start()

    if choice == '1':
        # Rekam dengan durasi
        duration = float(input("Masukkan durasi rekaman (detik): "))
        client.start_recording(duration)
        time.sleep(duration + 1)  # Tunggu sampai rekaman selesai
    else:
        # Rekam manual
        client.start_recording()
        input("Tekan Enter untuk berhenti merekam...")
        client.stop_recording()

    # Bersihkan
    client.stop_event.set()
    streaming_thread.join()
    client.cleanup()

if __name__ == "__main__":
    main()