const dgram = require("dgram");

function runUdpServer() {
  const server = dgram.createSocket("udp4");

  server.on("message", (msg, rinfo) => {
    console.log(`Received message: ${msg} from ${rinfo.address}:${rinfo.port}`);
  });

  server.bind(41234, () => {
    console.log("UDP server listening on port 41234");
  });
}

module.exports = { runUdpServer };
