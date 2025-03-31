const express = require("express");
const { runUtpTest } = require("../controllers/utpController");

const router = express.Router();

// Jalankan UTP (User Test Plan)
router.get("/start", (req, res) => {
  const result = runUtpTest();
  res.json({ message: "UTP test started", result });
});

module.exports = router;
