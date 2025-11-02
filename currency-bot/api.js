import express from "express";
import { db } from "./db.js";

const app = express();
app.use(express.json());

// Получить все курсы
app.get("/api/rates", async (req, res) => {
  const result = await db.query("SELECT currency, rate FROM rates ORDER BY currency ASC");
  res.json(result.rows);
});

// Получить конкретную валюту
app.get("/api/rates/:currency", async (req, res) => {
  const currency = req.params.currency.toUpperCase();
  const result = await db.query("SELECT currency, rate FROM rates WHERE currency = $1", [currency]);
  if (result.rows.length === 0) return res.status(404).json({ error: "Валюта не найдена" });
  res.json(result.rows[0]);
});

// Обновить курс (для админа)
app.post("/api/rates/:currency", async (req, res) => {
  const currency = req.params.currency.toUpperCase();
  const { rate } = req.body;
  if (!rate) return res.status(400).json({ error: "rate обязателен" });

  await db.query(
    `INSERT INTO rates(currency, rate) VALUES ($1, $2)
     ON CONFLICT (currency) DO UPDATE SET rate = EXCLUDED.rate, updated_at = NOW()`,
    [currency, rate]
  );
  res.json({ currency, rate });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`REST API запущен на http://localhost:${PORT}`));
