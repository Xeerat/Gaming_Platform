# app/utils/cleanup.py
import os
import json
from pathlib import Path
from sqlalchemy import select
from app.database import async_session_maker
from app.migration.models import Novell

UPLOAD_DIR = Path("uploads/novels")

async def cleanup_orphan_files():
    async with async_session_maker() as session:
        # Получаем все проекты
        result = await session.execute(select(Novell))
        novels = result.scalars().all()
        used_urls = set()
        for novel in novels:
            data = novel.data or {}
            # Собираем все URL из data (спрайты, фон, музыка)
            if "sceneSpritesData" in data:
                for s in data["sceneSpritesData"]:
                    if s.get("src"):
                        used_urls.add(s["src"])
            if data.get("bgImage"):
                used_urls.add(data["bgImage"])
            if data.get("audioFile"):
                used_urls.add(data["audioFile"])
            if "dialogData" in data:
                for d in data["dialogData"]:
                    for s in d.get("sprites", []):
                        if s.get("src"):
                            used_urls.add(s["src"])
        # Удаляем файлы, которые не в used_urls
        for user_dir in UPLOAD_DIR.iterdir():
            if not user_dir.is_dir():
                continue
            for file_path in user_dir.iterdir():
                # Строим ожидаемый URL
                file_url = f"/uploads/novels/{user_dir.name}/{file_path.name}"
                if file_url not in used_urls:
                    file_path.unlink()  # удаляем файл