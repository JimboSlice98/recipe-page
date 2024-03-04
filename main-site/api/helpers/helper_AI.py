
import os, json 
from openai import OpenAI
import openai
from dotenv import load_dotenv

client = OpenAI()
# Load your OpenAI API key from an environment variable for security
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
except:
    openai.api_key = None


load_dotenv()

def get_recipe_from_prompt(user_input):
    # Only use this when we need it, as charging per request
    if "admin" in user_input:
        try:
            if len(user_input) > 100:
                return 
            prompt = f"{user_input} - give me a recipe for the before. i want you do give the answers in dictionary format with  title: x, ingredients: y, steps: x .x string and y and z should be a list of strings, so then i will use the dictionary values based on the keys)"
            print(prompt)

        # Use the client to create a chat completion
            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model="gpt-3.5-turbo",
            )

            # response = chat_completion.choices[0].message['content']
            response = chat_completion.choices[0].message.content

            # use this line if we are in production!
            # Convert JSON string to Python dictionary
            response_dict = json.loads(response)
        except:
            response_dict = {
        "title": "error to ai",
        "ingredients": ["error", "er"], 
        "steps": ["err", "err"]
            }
        
        return response_dict
    else:
        
        response = {
        "title": "Chocolate Cake",
        "ingredients": [
            "1 and 3/4 cups all-purpose flour",
            "2 cups granulated sugar",
            "3/4 cup unsweetened cocoa powder",
            "2 teaspoons baking soda",
            "1 teaspoon baking powder",
            "1 teaspoon salt",
            "2 large eggs",
            "1 cup buttermilk",
            "1/2 cup vegetable oil",
            "2 teaspoons vanilla extract",
            "1 cup hot water"
        ],
        "steps": [
            "Preheat oven to 350°F (175°C) and grease and flour two 9-inch round cake pans.",
            "In a large bowl, whisk together flour, sugar, cocoa powder, baking soda, baking powder, and salt.",
            "Add eggs, buttermilk, oil, and vanilla extract to the dry ingredients and mix until well combined.",
            "Stir in hot water until the batter is smooth and pour into prepared cake pans.",
            "Bake for 30-35 minutes or until a toothpick inserted into the center comes out clean.",
            "Let the cakes cool in the pans for 10 minutes, then transfer to a wire rack to cool completely.",
            "Frost and decorate as desired. Enjoy your delicious chocolate cake!"
        ]
        }
        # note this doesnt work when live!!!!
        return dict(response)
    