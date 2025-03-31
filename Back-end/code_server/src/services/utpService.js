const fs = require("fs");
const path = require("path");

const LOGS_DIR = path.join(__dirname, "../../logs");

if (!fs.existsSync(LOGS_DIR)) {
  fs.mkdirSync(LOGS_DIR);
}

const runUtp = (req, res) => {
  const message = "Menjalankan UTP (simulasi)";
  const logFile = path.join(LOGS_DIR, "utp_log.txt");

  fs.appendFileSync(logFile, `[${new Date().toISOString()}] ${message}\n`);

  res.json({ success: true, message });
};

module.exports = { runUtp };
