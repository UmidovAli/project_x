import jwt from "jsonwebtoken";

export const authMiddleware = (req, res, next) => {
  try {
    const header = req.headers.authorization;
    if (!header) return res.status(401).json({ message: "Нет токена" });

    const token = header.split(" ")[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    // decoded должен содержать { id, ... } при создании токена в auth/login
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ message: "Неверный токен", error: err.message });
  }
};

// проверка роли
export const checkRole = (role) => (req, res, next) => {
  if (!req.user) return res.status(401).json({ message: "Нет авторизации" });
  if (req.user.role !== role) return res.status(403).json({ message: "Доступ запрещён" });
  next();
};
