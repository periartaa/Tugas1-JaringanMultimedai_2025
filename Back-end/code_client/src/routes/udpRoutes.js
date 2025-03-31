const express = require("express");
const { runUdpServer } = require("../controllers/udpController");

const router = express.Router();

// Jalankan server UDP
router.get("/start", (req, res) => {
  runUdpServer();
  res.json({ message: "UDP server started" });
});

module.exports = router;
