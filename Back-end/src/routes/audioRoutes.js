const express = require("express");
const multer = require("multer");
const router = express.Router();

// Konfigurasi upload file audio
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// API untuk mengunggah file audio
router.post("/upload", upload.single("audio"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "No audio file uploaded" });
  }
  console.log(`Received file: ${req.file.originalname}`);
  res.json({
    message: "File uploaded successfully",
    filename: req.file.originalname,
  });
});

// API untuk mendapatkan status server
router.get("/status", (req, res) => {
  res.json({ message: "Server is running..." });
});

module.exports = router;
