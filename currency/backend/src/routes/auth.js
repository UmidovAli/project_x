import express from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { pool } from "../db.js";  // твой файл подключения к PostgreSQL

const router = express.Router();

// ==========================
// Регистрация нового пользователя
// ==========================
router.post("/register", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email и пароль обязательны" });
    }

    // проверяем, есть ли уже пользователь
    const existing = await pool.query("SELECT * FROM users WHERE email=$1", [email]);
    if (existing.rows.length > 0) {
      return res.status(400).json({ message: "Пользователь с таким email уже существует" });
    }

    // хэшируем пароль
    const hashedPassword = await bcrypt.hash(password, 10);

    // создаем пользователя (по умолчанию роль = user)
    const result = await pool.query(
      "INSERT INTO users (email, password, role) VALUES ($1, $2, 'user') RETURNING id, email, role",
      [email, hashedPassword]
    );

    const user = result.rows[0];

    // создаем JWT (включаем роль)
    const token = jwt.sign(
      { id: user.id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "1d" }
    );

    res.json({ message: "Пользователь создан", token });

  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Ошибка регистрации", error: err.message });
  }
});

// ==========================
// Вход пользователя
// ==========================
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email и пароль обязательны" });
    }

    // ищем пользователя
    const { rows } = await pool.query("SELECT * FROM users WHERE email=$1", [email]);
    if (rows.length === 0) return res.status(400).json({ message: "Неверный email" });

    const user = rows[0];

    // сравниваем пароли
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ message: "Неверный пароль" });

    // создаем JWT с ролью
    const token = jwt.sign(
      { id: user.id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "1d" }
    );

    res.json({ message: "Успешный вход", token });

  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Ошибка входа", error: err.message });
  }
});

export default router;
