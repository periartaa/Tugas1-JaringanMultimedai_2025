const express = require("express");
const { downloadLog } = require("../services/logService");

const router = express.Router();

router.get("/:filename", downloadLog);

module.exports = router;
