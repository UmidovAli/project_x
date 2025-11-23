// src/routes/currency.js
import express from "express";
import axios from "axios";
import { authMiddleware } from "../middleware/authMiddleware.js";
import { pool } from "../db.js";

const router = express.Router();

// 1. GET /api/currency/ (Оригинальный маршрут, защищен авторизацией)
// Сохраняет пачку курсов в БД
router.get("/", authMiddleware, async (req, res) => {
    const userId = req.user.id;
    const currencies = ["USD", "EUR", "GBP", "CAD", "TMT", "RUB"];

    try {
        const { data } = await axios.get(
            `https://v6.exchangerate-api.com/v6/${process.env.CURRENCY_API_KEY}/latest/USD`
        );

        // ... Ваш код сохранения в filteredRates и запись в requests ...
        const filteredRates = {};
        for (const code of currencies) {
            if (data.conversion_rates[code]) {
                filteredRates[code] = data.conversion_rates[code];
            }
        }
        await pool.query(
            "INSERT INTO requests (user_id, currency_codes, response_json) VALUES ($1, $2, $3)",
            [userId, currencies.join(","), filteredRates]
        );

        res.json(filteredRates);
    } catch (err) {
        console.error("Ошибка при получении валют:", err.message);
        res.status(500).json({ message: "Ошибка получения валют", error: err.message });
    }
});

// 2. НОВЫЙ МАРШРУТ: GET /api/currency/latest?pair=USD/RUB
// Запрашивается фронтендом для обновления текущего курса.
router.get("/latest", async (req, res) => {
    const { pair } = req.query;
    if (!pair) {
        return res.status(400).json({ message: "Пара валют (pair) обязательна" });
    }
    
    // Разделяем пару на базовую (BASE) и целевую (TARGET)
    const [base, target] = pair.toUpperCase().split("/");
    if (!base || !target) {
        return res.status(400).json({ message: "Неверный формат пары (ожидается BASE/TARGET)" });
    }

    try {
        // Запрос курса конкретной пары
        const { data } = await axios.get(
            `https://v6.exchangerate-api.com/v6/${process.env.CURRENCY_API_KEY}/pair/${base}/${target}`
        );
        
        // Внешний API возвращает { "conversion_rate": 90.12 }
        if (data && data.conversion_rate) {
            // Фронтенд ожидает "rate"
            return res.json({ pair: pair.toUpperCase(), rate: data.conversion_rate });
        } else {
            return res.status(500).json({ message: "Не удалось получить курс", detail: data });
        }

    } catch (err) {
        // Ошибка при обращении к внешнему API
        console.error("Ошибка при получении курса:", err.message);
        res.status(500).json({ message: "Ошибка получения курса", error: err.message });
    }
});

export default router;