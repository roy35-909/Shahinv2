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
    quote_generator = QuoteGenerator()
    number = 200
    for quote in quote_generator.generate_quote(topic, number):
        quote = re.sub(r'^```[\w]*|```$', '', quote).strip()
        print(quote)
        print("DEBUG: quote =", repr(quote)) 
        try:
            dict_data = json.loads(quote)
        except:
            continue
        first_key = list(dict_data.keys())[0]
        first_value = dict_data[first_key]
        try:
            secnd_key = list(dict_data.keys())[1]
            secnd_value = dict_data[secnd_key]
        except:
            secnd_value = 'Unknown'
        Quote.objects.create(category=topic.lower(),content=first_value, author=secnd_value)

        print(first_key) 
        print(first_value)



