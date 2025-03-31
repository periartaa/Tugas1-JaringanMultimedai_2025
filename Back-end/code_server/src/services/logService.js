const fs = require("fs");
const path = require("path");

const LOGS_DIR = path.join(__dirname, "../../logs");

const downloadLog = (req, res) => {
  const { filename } = req.params;
  const filePath = path.join(LOGS_DIR, filename);

  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).json({ success: false, message: "File tidak ditemukan" });
  }
};

module.exports = { downloadLog };
