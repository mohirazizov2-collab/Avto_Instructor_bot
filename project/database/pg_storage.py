from __future__ import annotations

import json
from typing import Any, Dict, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from sqlalchemy import text

from .database import engine


# ============================================================
# POSTGRESQL FSM STORAGE
# ============================================================

class PgStorage(BaseStorage):

    async def set_state(
        self,
        key: StorageKey,
        state: Any = None,
    ) -> None:

        if state is None:
            state_value = None
        elif isinstance(state, str):
            state_value = state
        else:
            state_value = getattr(
                state,
                "state",
                str(state),
            )

        key_str = self._key_to_str(key)

        async with engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO fsm_storage (
                        key,
                        state,
                        data
                    )
                    VALUES (
                        :key,
                        :state,
                        '{}'
                    )
                    ON CONFLICT (key)
                    DO UPDATE SET
                        state = EXCLUDED.state
                    """
                ),
                {
                    "key": key_str,
                    "state": state_value,
                },
            )

    async def get_state(
        self,
        key: StorageKey,
    ) -> Optional[str]:

        key_str = self._key_to_str(key)

        async with engine.connect() as conn:

            result = await conn.execute(
                text(
                    """
                    SELECT state
                    FROM fsm_storage
                    WHERE key = :key
                    """
                ),
                {
                    "key": key_str,
                },
            )

            row = result.fetchone()

            if row is None:
                return None

            return row[0]

    async def set_data(
        self,
        key: StorageKey,
        data: Dict[str, Any],
    ) -> None:

        key_str = self._key_to_str(key)

        data_json = json.dumps(
            data,
            default=str,
            ensure_ascii=False,
        )

        async with engine.begin() as conn:

            await conn.execute(
                text(
                    """
                    INSERT INTO fsm_storage (
                        key,
                        state,
                        data
                    )
                    VALUES (
                        :key,
                        NULL,
                        :data
                    )
                    ON CONFLICT (key)
                    DO UPDATE SET
                        data = EXCLUDED.data
                    """
                ),
                {
                    "key": key_str,
                    "data": data_json,
                },
            )

    async def get_data(
        self,
        key: StorageKey,
    ) -> Dict[str, Any]:

        key_str = self._key_to_str(key)

        async with engine.connect() as conn:

            result = await conn.execute(
                text(
                    """
                    SELECT data
                    FROM fsm_storage
                    WHERE key = :key
                    """
                ),
                {
                    "key": key_str,
                },
            )

            row = result.fetchone()

            if row is None or not row[0]:
                return {}

            try:
                return json.loads(row[0])
            except (
                json.JSONDecodeError,
                TypeError,
            ):
                return {}

    async def update_data(
        self,
        key: StorageKey,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        current = await self.get_data(key)

        current.update(data)

        await self.set_data(
            key,
            current,
        )

        return current

    async def close(self) -> None:
        pass

    @staticmethod
    def _key_to_str(
        key: StorageKey,
    ) -> str:

        return (
            f"{key.bot_id}:"
            f"{key.chat_id}:"
            f"{key.user_id}"
        )
