const express = require("express");
const { runUdp } = require("../services/udpService");

const router = express.Router();

router.get("/", runUdp);

module.exports = router;
