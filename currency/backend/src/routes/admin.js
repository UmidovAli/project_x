import express from "express";
import { pool } from "../db.js";
import { authMiddleware, checkRole } from "../middleware/authMiddleware.js";

const router = express.Router();

// GET /api/admin/users  (только admin)
router.get("/users", authMiddleware, checkRole("admin"), async (req, res) => {
  try {
    const { rows } = await pool.query(
      "SELECT id, email, role, pair, limit_value, created_at, updated_at FROM users ORDER BY id DESC"
    );
    res.json(rows);
  } catch (err) {
    res.status(500).json({ message: "Ошибка получения списка пользователей", error: err.message });
  }
});

export default router;
