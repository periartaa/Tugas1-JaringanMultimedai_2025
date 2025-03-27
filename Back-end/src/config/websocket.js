const WebSocket = require("ws");

module.exports = (server) => {
  const wss = new WebSocket.Server({ server });
  let clients = [];

  wss.on("connection", (ws) => {
    console.log("Client connected");
    clients.push(ws);

    ws.on("message", (message) => {
      console.log(`Received ${message.length} bytes`);

      // Broadcast audio ke semua klien
      clients.forEach((client) => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(message);
        }
      });
    });

    ws.on("close", () => {
      console.log("Client disconnected");
      clients = clients.filter((client) => client !== ws);
    });
  });

  return wss;
};
