const http = require("http");
const app = require("./src/app");
const initWebSocket = require("./src/config/websocket");

const PORT = process.env.PORT || 3000;
const server = http.createServer(app);

// Inisialisasi WebSocket
initWebSocket(server);

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
