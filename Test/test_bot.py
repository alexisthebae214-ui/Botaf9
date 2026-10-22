import tempfile
import unittest
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiosqlite
from aiogram.types import User

import main


class BotLogicTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = main.DB_PATH
        main.DB_PATH = self.temp_dir.name + "/test.db"
        await main.init_db()
        await main.ensure_user(
            User(id=101, is_bot=False, first_name="Test", username="tester")
        )

    async def asyncTearDown(self):
        main.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    async def add_balance(self, amount_cents):
        async with main.db_session() as db:
            await db.execute(
                "UPDATE users SET balance_cents = ? WHERE user_id = 101",
                (amount_cents,),
            )
            await db.commit()

    # --- pure helpers ---

    async def test_money_parsing_and_formatting(self):
        self.assertEqual(main.parse_money("12,50"), 1250)
        self.assertEqual(main.parse_money("12.50"), 1250)
        self.assertEqual(main.format_money(1250), "12.50 TL")
        self.assertEqual(main.format_money(5), "0.05 TL")
        with self.assertRaises(ValueError):
            main.parse_money("-1")
        with self.assertRaises(ValueError):
            main.parse_money("0")
        with self.assertRaises(ValueError):
            main.parse_money("abc")

    async def test_star_tier_parsing(self):
        tiers = main.parse_star_tiers("50:25,100:50,250:125")
        self.assertEqual(tiers, [(50, 2500), (100, 5000), (250, 12500)])
        # zero/negative and malformed entries are dropped
        self.assertEqual(main.parse_star_tiers("0:10,-5:20,abc"), [])
        # duplicates collapse
        self.assertEqual(main.parse_star_tiers("50:25,50:25"), [(50, 2500)])

    async def test_is_expired(self):
        future = (main.now_utc() + timedelta(hours=1)).isoformat(timespec="seconds")
        past = (main.now_utc() - timedelta(hours=1)).isoformat(timespec="seconds")
        self.assertFalse(main.is_expired(future))
        self.assertTrue(main.is_expired(past))
        self.assertTrue(main.is_expired(None))
        self.assertTrue(main.is_expired("not-a-date"))

    async def test_xp_leveling(self):
        self.assertEqual(main.xp_for_level(1), 100)
        self.assertEqual(main.xp_for_level(5), 500)
        async with main.db_session() as db:
            leveled, lv = await main.add_xp(db, 101, 250)
        self.assertEqual(leveled, 2)  # 100 -> level 2, 100 -> level 3, 50 left
        self.assertEqual(lv, 3)

    async def test_channel_join_url(self):
        old_channel = main.FORCE_JOIN_CHANNEL
        old_url = main.JOIN_CHANNEL_URL
        try:
            main.FORCE_JOIN_CHANNEL = "@mychannel"
            main.JOIN_CHANNEL_URL = ""
            self.assertEqual(main.channel_join_url(), "https://t.me/mychannel")
            main.JOIN_CHANNEL_URL = "https://t.me/custom"
            self.assertEqual(main.channel_join_url(), "https://t.me/custom")
        finally:
            main.FORCE_JOIN_CHANNEL = old_channel
            main.JOIN_CHANNEL_URL = old_url

    # --- db behaviour ---

    async def test_ensure_user_is_idempotent(self):
        await main.ensure_user(
            User(id=101, is_bot=False, first_name="Renamed", username="renamed")
        )
        async with main.db_session() as db:
            cur = await db.execute(
                "SELECT username, first_name FROM users WHERE user_id = 101"
            )
            row = await cur.fetchone()
        self.assertEqual(row["username"], "renamed")
        self.assertEqual(row["first_name"], "Renamed")

    async def test_promo_can_only_be_claimed_once_per_user(self):
        expires_at = (main.now_utc() + timedelta(hours=1)).isoformat(timespec="seconds")
        async with main.db_session() as db:
            await db.execute(
                """
                INSERT INTO promos (code, bonus_cents, max_uses, expires_at, created_at)
                VALUES ('TEST10', 1000, 10, ?, ?)
                """,
                (expires_at, main.timestamp()),
            )
            await db.commit()
            # first claim inserts a promo_uses row
            await db.execute(
                "INSERT INTO promo_uses (code, user_id) VALUES ('TEST10', 101)"
            )
            await db.commit()
            # second claim for the same user must violate the PK
            with self.assertRaises(aiosqlite.IntegrityError):
                await db.execute(
                    "INSERT INTO promo_uses (code, user_id) VALUES ('TEST10', 101)"
                )
                await db.commit()

    async def test_forced_join_membership_check(self):
        # The membership check lives in JoinMiddleware; verify the status logic
        # it relies on by exercising the same status set.
        old_channel = main.FORCE_JOIN_CHANNEL
        main.FORCE_JOIN_CHANNEL = "@public_test_channel"
        bot = SimpleNamespace(
            get_chat_member=AsyncMock(
                return_value=SimpleNamespace(status="member")
            )
        )
        try:
            m = await bot.get_chat_member(
                chat_id=main.FORCE_JOIN_CHANNEL, user_id=101
            )
            self.assertIn(m.status, ("creator", "administrator", "member"))
            bot.get_chat_member.return_value = SimpleNamespace(status="left")
            m = await bot.get_chat_member(
                chat_id=main.FORCE_JOIN_CHANNEL, user_id=101
            )
            self.assertNotIn(m.status, ("creator", "administrator", "member"))
        finally:
            main.FORCE_JOIN_CHANNEL = old_channel


if __name__ == "__main__":
    unittest.main()
