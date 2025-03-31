const dgram = require("dgram");
const fs = require("fs");
const path = require("path");

const LOGS_DIR = path.join(__dirname, "../../logs");
const UDP_PORT = 41234;
const serverUDP = dgram.createSocket("udp4");

if (!fs.existsSync(LOGS_DIR)) {
  fs.mkdirSync(LOGS_DIR);
}

const runUdp = (req, res) => {
  serverUDP.on("message", (msg, rinfo) => {
    console.log(`Pesan diterima: ${msg} dari ${rinfo.address}:${rinfo.port}`);
    const logFile = path.join(LOGS_DIR, "udp_log.txt");

    fs.appendFileSync(
      logFile,
      `[${new Date().toISOString()}] Pesan dari ${rinfo.address}:${
        rinfo.port
      }: ${msg}\n`
    );
  });

  serverUDP.bind(UDP_PORT, () => {
    console.log(`UDP server berjalan di port ${UDP_PORT}`);
  });

  res.json({
    success: true,
    message: `UDP server berjalan di port ${UDP_PORT}`,
  });
};

module.exports = { runUdp };
