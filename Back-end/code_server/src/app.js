const express = require("express");
const cors = require("cors");

const utpRoutes = require("./routes/utpRoutes");
const udpRoutes = require("./routes/udpRoutes");
const logRoutes = require("./routes/logRoutes");

const app = express();
app.use(express.json());
app.use(cors());

// Tambahkan route ke aplikasi
app.use("/utp", utpRoutes);
app.use("/udp", udpRoutes);
app.use("/logs", logRoutes);

module.exports = app;
