const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

// Import rute
const audioRoutes = require("./routes/audioRoutes");

app.use("/api/audio", audioRoutes);

module.exports = app;
