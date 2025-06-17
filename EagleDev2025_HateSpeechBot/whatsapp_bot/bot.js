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
  console.log("📩 Mensaje recibido:", msg.body || "[No es texto]");
  console.log("🔍 Tipo:", msg.type);

  try {
    const from = msg.from;
    const sender = msg.author || msg.from;
    const userNumber = sender.split("@")[0];
    const isGroup = msg.from.endsWith("@g.us");
    let groupName = null;

    if (isGroup) {
      const chat = await msg.getChat();
      groupName = chat.name;
      console.log("👥 Grupo detectado:", groupName);
    }

    // === Texto ===
    if (msg.type === "chat") {
      const text = msg.body;
      const res = await axios.post("http://localhost:5001/predict", {
        text,
        user: userNumber,
        group: groupName,
      });

      console.log("🤖 Respuesta del modelo:", res.data);

      if (res.data.resultado !== "Normal") {
        await msg.reply(
          "⚠️ Este mensaje puede contener lenguaje ofensivo según IA."
        );
      }
    }

    // === Audio ===
    else if (msg.type === "audio" || msg.type === "ptt") {
      const media = await msg.downloadMedia();
      if (!media) return console.log("❌ No se pudo descargar el audio");

      const audioBuffer = Buffer.from(media.data, "base64");
      const filename = `audio-${Date.now()}.ogg`;
      const audioPath = path.join(__dirname, "audios", filename);

      fs.writeFileSync(audioPath, audioBuffer);
      console.log("🎙️ Audio guardado en:", audioPath);

      const formData = new FormData();
      formData.append("audio", fs.createReadStream(audioPath));
      formData.append("user", userNumber);
      formData.append("group", groupName || "");

      const res = await axios.post(
        "http://localhost:5001/transcribe",
        formData,
        {
          headers: formData.getHeaders(),
        }
      );

      console.log("🧠 Transcripción recibida:", res.data);

      if (res.data.resultado !== "Normal") {
        await msg.reply("⚠️ El audio contiene lenguaje ofensivo según IA.");
      }

      fs.unlinkSync(audioPath); // Limpieza
    }
  } catch (err) {
    console.error("❌ Error en el procesamiento:", err.message);
  }
});

client.initialize();
