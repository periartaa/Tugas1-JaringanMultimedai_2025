const express = require("express");
const { runUtp } = require("../services/utpService");

const router = express.Router();

router.get("/", runUtp);

module.exports = router;
