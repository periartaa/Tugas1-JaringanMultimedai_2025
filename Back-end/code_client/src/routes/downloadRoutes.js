const express = require("express");
const { downloadRecording } = require("../controllers/downloadController");

const router = express.Router();

// Endpoint untuk mengunduh rekaman
router.get("/download/:filename", downloadRecording);

module.exports = router;
