import pg from "pg";
import dotenv from "dotenv";

dotenv.config();

export const db = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function initDB() {
  await db.query(`
    CREATE TABLE IF NOT EXISTS rates (
      currency TEXT PRIMARY KEY,
      rate NUMERIC,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  await db.query(`
    CREATE TABLE IF NOT EXISTS subscriptions (
      user_id BIGINT,
      currency TEXT,
      PRIMARY KEY (user_id, currency)
    );
  `);
}
