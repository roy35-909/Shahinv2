import json
import re
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from ai.ai_app import QuoteGenerator
from quote.models import Quote
from rest_framework.permissions import IsAdminUser
from rest_framework import status
class AIQuoteAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get topic from query params, default to "motivation"
        topic = request.query_params.get("topic", "motivation").strip().lower()
        number = int(request.query_params.get("number", 20))  # optional number param, default 20

        quote_generator = QuoteGenerator()

        saved_quotes = []

        for raw_item in quote_generator.generate_quote(topic, number):

            # Ensure it's a string
            if not isinstance(raw_item, str):
                continue

            # Remove code block formatting like ```json ... ```
            cleaned = re.sub(r"^```[\w]*\n?|\n?```$", "", raw_item).strip()

            # Convert to dict
            try:
                item = json.loads(cleaned)
            except Exception:
                print("❌ JSON load failed:", cleaned)
                continue

            # Extract content
            content = item.get(topic)
            author = item.get("author", "ai-generated")

            # Validate before saving
            if not content:
                print("⚠️ Content missing:", item)
                continue

            # Save to database
            quote_obj = Quote.objects.create(
                category=topic,
                content=content.strip(),
                author=author.strip()
            )
            saved_quotes.append({
                "content": content.strip(),
                "author": author.strip()
            })

            print("✔️ Saved:", content[:50], "...")

        return Response({
            "message": f"Quotes successfully generated for topic '{topic}'!",
            "saved_count": len(saved_quotes),
            "quotes": saved_quotes
        }, status=status.HTTP_200_OK)