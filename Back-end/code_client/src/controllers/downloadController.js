const path = require("path");

function downloadRecording(req, res) {
  const { filename } = req.params;
  const filePath = path.join(__dirname, "../../recordings", filename);

  res.download(filePath, (err) => {
    if (err) {
      console.error("Error downloading file:", err);
      res.status(500).json({ error: "File not found or error in download" });
    }
  });
}

module.exports = { downloadRecording };
