from openai import OpenAI
from quote.models import Quote
import re
import json
from django.conf import settings
class prompts:
    def fitness_prompt(self) -> str:
        return (
            """
            Speak like a savage who bleeds for strength. Write quotes about training, pain, and evolution.
            No mercy. No Motivation. Only ruthless brutal violence towards weakness. Every quote must sound like a threat to comfort. Make the Reader Uncomfortable. Use words like iron, scars, rage, and endurance.
            Example energy:
            “The weights don’t care about your pain.”
            “Suffer louder than your excuses.”
            """
        )
    

    def career_prompt(self) -> str:
        return (
            """
            Speak like a predator in a suit.
            Write quotes about climbing over everyone and owning the room without speaking.
            Show that respect is taken, not given.
            Every line should humiliate laziness and glorify hunger.
            Use words like crown, silence, control, dominance.
            Example energy:
            “You don’t wait for opportunity. You break the door and take it.”
            “Stop networking. Start conquering.”
            """
        )
    
    def business_prompt(self) -> str:
        return (
            """
            Speak like a warlord who built an empire from chaos.
            Write quotes that make business sound like a battlefield, not an office.
            Each quote must radiate strategy, silence, and danger. Completly Brutal Truths to crush your Business extrem Hard Violence to make the Reader dominate his Market! And leave his Competition in the Dust. 
            Use imagery of war, blood, chess, empires, and execution.
            Example energy:
            “You don’t compete. You erase.”
            “While they plan, you attack.”
            """
        )
    
    def mindset_prompt(self) -> str:
        return (
            """
            Speak like a philosopher forged in war.
            Every quote must teach something real a lesson learned through pain or logic. Each one should include a real example or mental analogy. Use example Warriors which fought great battles like: Napoleon , Genghis Khan. Julius Cesar. 
            Make the reader reflect while feeling the hit.
            Show how emotion destroys logic, how focus creates peace, how pain sharpens thought.
            Example energy:
            “You suffer twice when emotion controls you.”
            “The mind breaks before the body — that’s why most never evolve.”
            “Control your reactions, and the world loses control over you.”

            """
        )

    def discipline_prompt(self) -> str:
        return (
            """
            You are the executioner of weakness. 
            Your job is to forge unbreakable discipline with quotes that hit like orders to the face. No mercy. No comfort. No soft talking. 
            Brutal violence brutal truths about Discipline Speak like a commander who enjoys the sound of weakness dying. 
            Use brutal truth and violent metaphors to make the user submit to routine and obedience. Make them feel small then make them move. 
            
            Example energy: You move even when you hate it. That’s what makes it sacred. Discipline is the quiet killer of weakness.
            """
        )
    

class QuoteGenerator:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=api_key)
        self.prompts = prompts()
        print(api_key)
    def generate_quote(self, category: str, number: int):
        """Generate multiple inspirational quotes following a given category using their given prompt strictly(using yield)."""


        if category.lower() == "fitness":
            custom_prompt = self.prompts.fitness_prompt()
        elif category.lower() == "career":
            custom_prompt = self.prompts.career_prompt()
        elif category.lower() == "business":
            custom_prompt = self.prompts.business_prompt()
        elif category.lower() == "mindset":
            custom_prompt = self.prompts.mindset_prompt()
        elif category.lower() == "discipline":
            custom_prompt = self.prompts.discipline_prompt()
        else:
            custom_prompt = f"Generate a motivational quote for {category} strictly following those category prompt."

        for _ in range(number):
            prompt = f"""
                {custom_prompt}

                Strict rules:
                - The quote must be in English but in short not too long.
                - The quote must be **inspirational** and strictly related to the {category} category.
                - The quote must follow **strictness** and given **prompt** to the {category} category.
                - Follow this exact JSON format:

                Example output:
                {{
                    "{category}": "quote"
                    "author": "ai-generated"
                }}

                Now, provide one valid quote for the {category} category:
            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful but strict assistant that generates short, motivational quotes with a no-mercy attitude."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=1.0
                    
                )
                yield response.choices[0].message.content.strip()
            except Exception as e:
                yield {"error": str(e)}



if __name__ == "__main__":
    quote_generator = QuoteGenerator()
    category = "career"
    number = 100

    for quote in quote_generator.generate_quote(category, number):
        print("RAW OUTPUT:", repr(quote))
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
        Quote.objects.create(category=category.lower(),content=first_value, author=secnd_value)
        print(quote)
