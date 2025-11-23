import express from "express";
import bcrypt from "bcryptjs";
import { pool } from "../db.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// GET /api/user/profile
router.get("/profile", authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    const { rows } = await pool.query(
      "SELECT id, email, role, pair, limit_value, created_at, updated_at FROM users WHERE id=$1",
      [userId]
    );
    if (rows.length === 0) return res.status(404).json({ message: "Пользователь не найден" });
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ message: "Ошибка получения профиля", error: err.message });
  }
});

// PUT /api/user/update  (обновить email, pair, limit)
router.put("/update", authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    const { email, pair, limit } = req.body;

    // простая валидация
    if (email && typeof email !== "string") return res.status(400).json({ message: "Неверный email" });

    const { rows } = await pool.query(
      `UPDATE users
       SET email = COALESCE($1, email),
           pair = COALESCE($2, pair),
           limit_value = COALESCE($3, limit_value),
           updated_at = CURRENT_TIMESTAMP
       WHERE id=$4
       RETURNING id, email, role, pair, limit_value, created_at, updated_at`,
      [email, pair, limit, userId]
    );

    res.json({ message: "Профиль обновлён", user: rows[0] });
  } catch (err) {
    // если уникальность email нарушена
    if (err.code === "23505") return res.status(400).json({ message: "Email уже используется" });
    res.status(500).json({ message: "Ошибка обновления профиля", error: err.message });
  }
});

// POST /api/user/change-password
router.post("/change-password", authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    const { oldPassword, newPassword } = req.body;
    if (!oldPassword || !newPassword) return res.status(400).json({ message: "Нужно старый и новый пароль" });

    const { rows } = await pool.query("SELECT password FROM users WHERE id=$1", [userId]);
    if (rows.length === 0) return res.status(404).json({ message: "Пользователь не найден" });

    const hash = rows[0].password;
    const ok = await bcrypt.compare(oldPassword, hash);
    if (!ok) return res.status(400).json({ message: "Старый пароль неверен" });

    const newHash = await bcrypt.hash(newPassword, 10);
    await pool.query("UPDATE users SET password=$1, updated_at=CURRENT_TIMESTAMP WHERE id=$2", [newHash, userId]);
    res.json({ message: "Пароль успешно изменён" });
  } catch (err) {
    res.status(500).json({ message: "Ошибка смены пароля", error: err.message });
  }
});

export default router;
