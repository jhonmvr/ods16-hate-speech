const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const axios = require("axios");
const fs = require("fs");
const path = require("path");
const FormData = require("form-data");

const client = new Client({ authStrategy: new LocalAuth() });

client.on("qr", (qr) => {
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("✅ Bot conectado a WhatsApp");
});

client.on("message", async (msg) => {
  console.log("📩 Mensaje recibido:", msg.body || "[Audio]");
  console.log("🔍 Tipo:", msg.type);

  try {
    const sender = msg.author || msg.from;
    const userNumber = sender.split("@")[0];
    const isGroup = msg.from.endsWith("@g.us");
    let groupName = null;

    if (isGroup) {
      const chat = await msg.getChat();
      groupName = chat.name;
    }

    // === TEXTO ===
    if (msg.type === "chat") {
      const text = msg.body;

      const response = await axios.post("http://localhost:5001/predict", {
        text,
        user: userNumber,
        group: groupName,
      });

      const resultado = response.data.resultado;
      const respuestaModerada = response.data.respuesta_moderada;

      if (resultado !== "Ninguno") {
        const advertencia =
          `⚠️ Este mensaje fue detectado como potencialmente ofensivo.\n` +
          `🔍 *Clasificación:* ${resultado}\n\n` +
          `💡 *Sugerencia alternativa:* ${respuestaModerada}`;
        await msg.reply(advertencia);
      }
    }

    // === AUDIO ===
    else if (msg.type === "audio" || msg.type === "ptt") {
      const media = await msg.downloadMedia();
      if (!media) return console.log("❌ No se pudo descargar el audio");

      const audioBuffer = Buffer.from(media.data, "base64");
      const filename = `audio-${Date.now()}.ogg`;
      const audioPath = path.join(__dirname, "audios", filename);

      fs.writeFileSync(audioPath, audioBuffer);
      console.log("🎙️ Audio guardado:", audioPath);

      const formData = new FormData();
      formData.append("audio", fs.createReadStream(audioPath));
      formData.append("user", userNumber);
      formData.append("group", groupName || "");

      const response = await axios.post(
        "http://localhost:5001/transcribe",
        formData,
        {
          headers: formData.getHeaders(),
        }
      );

      fs.unlinkSync(audioPath);

      const { resultado, respuesta_moderada } = response.data;

      if (resultado !== "Ninguno") {
        const advertencia =
          `⚠️ Este audio fue detectado como potencialmente ofensivo.\n` +
          `🔍 *Clasificación:* ${resultado}\n\n` +
          `💡 *Sugerencia alternativa:* ${respuesta_moderada}`;
        await msg.reply(advertencia);
      }
    }
  } catch (err) {
    console.error("❌ Error en procesamiento:", err.message);
    await msg.reply("⚠️ Ocurrió un error al procesar tu mensaje.");
  }
});

client.initialize();
