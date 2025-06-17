// Código del bot de WhatsApp
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({ authStrategy: new LocalAuth() });

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Bot conectado a WhatsApp');
});

client.on('message', async msg => {
    console.log("📩 Mensaje recibido:", msg.body); 

    try {
      const res = await axios.post("http://localhost:5001/predict", {
        text: msg.body,
        user: msg.from.split("@")[0], 
      });

      console.log("📤 Resultado del modelo:", res.data.resultado);

      if (res.data.resultado === "Ofensivo" || res.data.resultado === "Racista" || res.data.resultado === "Odio") {
        msg.reply("⚠️ Este mensaje puede contener lenguaje ofensivo según IA.");
      }
    } catch (err) {
      console.error("❌ Error con el backend:", err.message);
    }
});

client.initialize();
