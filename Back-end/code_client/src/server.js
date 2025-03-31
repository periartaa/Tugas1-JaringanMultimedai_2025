require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json()); // Middleware untuk membaca JSON

// Import routes
const udpRoutes = require("./routes/udpRoutes");
const utpRoutes = require("./routes/utpRoutes");
const downloadRoutes = require("./routes/downloadRoutes");

// Gunakan routes
app.use("/api/udp", udpRoutes);
app.use("/api/utp", utpRoutes);
app.use("/api/recording", downloadRoutes);

// Jalankan server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
