# AudioStreamer

## Langkah - Langkah Persiapan
1. Pastikan anda memiliki compiler python untuk menjalankan program
2. Donlowad pada device anda
   ``` Bash
   git clone https://github.com/periartaa/Tugas1-JaringanMultimedai_2025.git
   ```
4. Instal Dependensi yang Diperlukan
   ``` Bash
   pip install pyaudio
   ```
5. Jalankan program "server.py" & "client.py"


## Langkah Run Program
1. Jalankan skrip
2. Anda bisa menggunakan perintah:
   ``` Bash
   python nama_file.py --protocol udp --port 12345 --size 10
   ```

   Keterangan :
   - nama_file.py --> Ubah sesaui nama file yag akan djalankan
   - --protocol udp --> Menentukan apakah server menggunakan UDP atau TCP. Default: udp
   - --port 12345: Port yang digunakan untuk menerima data audio.
   - --size 10: Ukuran buffer dalam milidetik (harus kelipatan 10 antara 10 hingga 150 ms).
   - Contoh :
      - Run server
     ``` Bash
     python server.py --protocol udp --port 12345 --size 10
     ```
      - Run client
     ``` Bash
     python client.py --protocol udp --port 12345 --size 10
     ```
3. Pastikan menjalankan server terlebih dahulu lalu jalankan client
4. Pada saat menjalankan client, akan terdapat 2 pilihan
   ``` Bash
   Pilih aksi:
   1. Rekam dengan durasi tertentu
   2. Rekam dan stop manual
   ```
5. Setelah memilih aksi tersebut, server akan otomatis berhenti jika client berhenti.
