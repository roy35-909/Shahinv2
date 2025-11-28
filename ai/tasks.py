from quote.models import Quote

import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Subquery
from ai.ai_app import QuoteGenerator
import json
import re
User = get_user_model()


logger = logging.getLogger(__name__)

@shared_task
def generate_quote(topic):
    number = 200
    quote_generator = QuoteGenerator()

    for raw_item in quote_generator.generate_quote(topic, number):


        if not isinstance(raw_item, str):
            continue


        cleaned = re.sub(r"^```[\w]*\n?|\n?```$", "", raw_item).strip()


        try:
            item = json.loads(cleaned)
        except Exception:
            print("❌ JSON load failed:", cleaned)
            continue


        content = item.get(topic)
        author = item.get("author", "ai-generated")


        if not content:
            print("⚠️ Content missing:", item)
            continue


        Quote.objects.create(
            category=topic.lower(),
            content=content.strip(),
            author=author.strip()
        )

        print("✔️ Saved:", content[:30], "...")

