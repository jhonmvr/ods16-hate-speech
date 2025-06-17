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
    try {
        const text = msg.body;
        const from = msg.from;
        const sender = msg.author || msg.from; 

        // Extraer número del usuario
        const userNumber = (msg.author || msg.from).split('@')[0];

        // Detectar si es grupo
        const isGroup = msg.from.endsWith('@g.us');
        let groupName = null;

        if (isGroup) {
            const chat = await msg.getChat();
            groupName = chat.name;
        }

        // Enviar al backend
        const res = await axios.post('http://localhost:5001/predict', {
            text,
            user: userNumber,
            group: groupName
        });

        if (res.data.resultado !== "Normal") {
            msg.reply("⚠️ Este mensaje puede contener lenguaje ofensivo según IA.");
        }

    } catch (err) {
        console.error('❌ Error con el backend:', err.message);
    }
});


client.initialize();
