import TelegramBot from "node-telegram-bot-api";
import dotenv from "dotenv";
import axios from "axios";
import { db, initDB } from "./db.js";

dotenv.config();
await initDB();

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
const API_KEY = process.env.CURRENCY_API_KEY;
const BASE_URL = "https://api.apilayer.com/currency_data";

// --- Currencies by continent with RUB ---
const currenciesByContinent = {
  "Европа": ["EUR", "GBP", "CHF", "SEK", "NOK", "DKK", "RUB"],
  "Азия": ["JPY", "CNY", "INR", "KRW", "SGD", "THB"],
  "Америка": ["USD", "CAD", "BRL", "MXN", "ARS"],
  "Африка": ["ZAR", "EGP", "NGN", "KES"],
  "Океания": ["AUD", "NZD"]
};

// --- Helpers ---
const allCurrencies = Object.values(currenciesByContinent).flat().join(",");

async function getRates(symbols = allCurrencies) {
  try {
    const res = await axios.get(`${BASE_URL}/live`, {
      headers: { apikey: API_KEY },
      params: { base: "USD", symbols },
    });

    return Object.entries(res.data.quotes).map(([pair, rate]) => {
      const currency = pair.slice(3);
      return { currency, rate };
    });
  } catch (err) {
    console.error("Ошибка получения курсов:", err.response?.status, err.response?.data || err.message);
    return [];
  }
}

async function getRate(currency) {
  const rates = await getRates(currency);
  return rates[0]?.rate;
}

// --- Subscriptions ---
async function addSubscription(userId, currency) {
  await db.query(
    "INSERT INTO subscriptions (user_id, currency) VALUES ($1, $2) ON CONFLICT DO NOTHING",
    [userId, currency]
  );
}

async function removeSubscription(userId, currency) {
  await db.query(
    "DELETE FROM subscriptions WHERE user_id = $1 AND currency = $2",
    [userId, currency]
  );
}

async function getUserSubscriptions(userId) {
  const res = await db.query("SELECT currency FROM subscriptions WHERE user_id = $1", [userId]);
  return res.rows.map(r => r.currency);
}

// --- Bot commands ---
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const name = msg.from.first_name || "друг";

  const keyboard = {
    reply_markup: {
      keyboard: [["💰 Курсы валют"], ["📩 Мои подписки"]],
      resize_keyboard: true,
    },
  };

  await bot.sendMessage(
    chatId,
    `Привет, ${name}! 👋\nЯ бот для курсов валют.\n\nТы можешь:\n• Посмотреть текущие курсы\n• Подписаться на валюту, чтобы получать обновления`,
    keyboard
  );
});

// --- Main menu: select continent ---
bot.onText(/💰 Курсы валют/, async (msg) => {
  const chatId = msg.chat.id;

  const buttons = Object.keys(currenciesByContinent).map(continent => [
    { text: continent, callback_data: `continent:${continent}` }
  ]);

  await bot.sendMessage(chatId, "Выбери континент 🌍", {
    reply_markup: { inline_keyboard: buttons }
  });
});

// --- User subscriptions menu ---
bot.onText(/📩 Мои подписки/, async (msg) => {
  const chatId = msg.chat.id;
  const subs = await getUserSubscriptions(chatId);

  if (!subs.length) return bot.sendMessage(chatId, "У тебя пока нет подписок 📭");

  const buttons = subs.map(c => [{ text: `❌ Отписаться от ${c}`, callback_data: `unsub:${c}` }]);
  let text = "📩 <b>Твои подписки:</b>\n" + subs.map(s => `• ${s}`).join("\n");
  await bot.sendMessage(chatId, text, { parse_mode: "HTML", reply_markup: { inline_keyboard: buttons } });
});

// --- Callback handling ---
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const [action, value] = query.data.split(":");

  if (action === "continent") {
    // Show currencies for the selected continent with current rate
    const currencies = currenciesByContinent[value];
    const rates = await getRates(currencies.join(","));
    const rateMap = Object.fromEntries(rates.map(r => [r.currency, r.rate]));

    const buttons = currencies.map(c => [{
      text: `${c} (${rateMap[c]?.toFixed(2) || "–"})`,
      callback_data: `sub:${c}`
    }]);
    buttons.push([{ text: "⬅️ Назад", callback_data: "back:menu" }]);

    await bot.editMessageText(`Валюты в ${value}:`, {
      chat_id: chatId,
      message_id: query.message.message_id,
      reply_markup: { inline_keyboard: buttons }
    });
  }

  else if (action === "sub") {
    await addSubscription(chatId, value);
    await bot.answerCallbackQuery(query.id, { text: `✅ Подписка на ${value} добавлена!` });
  }

  else if (action === "unsub") {
    await removeSubscription(chatId, value);
    await bot.answerCallbackQuery(query.id, { text: `❌ Отписка от ${value} выполнена!` });
  }

  else if (action === "back" && value === "menu") {
    const buttons = Object.keys(currenciesByContinent).map(continent => [
      { text: continent, callback_data: `continent:${continent}` }
    ]);

    await bot.editMessageText("Выбери континент 🌍", {
      chat_id: chatId,
      message_id: query.message.message_id,
      reply_markup: { inline_keyboard: buttons }
    });
  }
});

// --- Notifications ---
async function notifySubscribers(currency, newRate) {
  const res = await db.query("SELECT user_id FROM subscriptions WHERE currency = $1", [currency]);
  for (const row of res.rows) {
    try {
      await bot.sendMessage(row.user_id, `💱 Новый курс ${currency}: <b>${newRate.toFixed(2)}</b>`, { parse_mode: "HTML" });
    } catch (err) {
      console.error("Ошибка уведомления:", err.message);
    }
  }
}

// --- Auto update ---
const UPDATE_INTERVAL = 10 * 60 * 1000;
let lastRates = {};

async function checkUpdates() {
  const rates = await getRates();

  for (const { currency, rate } of rates) {
    if (lastRates[currency] && lastRates[currency] !== rate) {
      await notifySubscribers(currency, rate);
    }
    lastRates[currency] = rate;
  }
}

setInterval(checkUpdates, UPDATE_INTERVAL);
checkUpdates();

console.log("✅ Бот запущен и слушает Telegram...");
