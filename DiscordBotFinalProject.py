from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from random import choice, randint
import openai
import json
import requests
import re


def get_weather_forecast(api_key, latitude, longitude): #API call to get the weather information for Cvill
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={latitude},{longitude}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else: #Account for an error
        print("Error:", response.status_code)
        return None

api_key = "TwSv5I7l7KdUI42lClLFpiP4lLKI2iuK"
latitude = 38.0293
longitude = -78.4767

def print_weather(): #API call to take the weather data and make it into a readable string with only a few values
  forecast_data = get_weather_forecast(api_key, latitude, longitude)

  if forecast_data:
      # Extract the relevant information from the response
      timelines = forecast_data['timelines']
      if 'minutely' in timelines:  # Check if 'data' key exists
          data = timelines['minutely'][0]  # Extracting the first timeline
          # Extracting required information
          cloud_cover = data['values']['cloudCover']
          temperature = data['values']['temperature']
          humidity = data['values']['humidity']
          precipitation_probability = data['values']['precipitationProbability']
          pressure_surface_level = data['values']['pressureSurfaceLevel']
          wind_speed = data['values']['windSpeed']
          wind_direction = data['values']['windDirection']
          # Continue extracting other required information

          # Printing the extracted information (you can replace print with your desired logic)
          weather_info = (
              f"Cloud Cover: {cloud_cover}\n"
              f"Temperature: {temperature}\n"
              f"Humidity: {humidity}\n"
              f"Precipitation Probability: {precipitation_probability}\n"
              f"Pressure Surface Level: {pressure_surface_level}\n"
              f"Wind Speed: {wind_speed}\n"
              f"Wind Direction: {wind_direction}"
          )
          return weather_info
          # error handeling
      else:
          print("'data' key not found in timelines")
          return "failure of API, please try again"
  else:
      print("No forecast data available")
      return "failure of API, please try again"

def get_random_chuck_norris_joke(): #call the chucknorris API and return the joke as read from JSON

    url = "https://api.chucknorris.io/jokes/random"
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        return joke_data['value']
    else:
        return "Failed to fetch Chuck Norris joke"

def get_number_fact(number): #Use the numbersapi to get a number fact
    url = f"http://numbersapi.com/{number}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Failed to fetch number fact"

def get_random_joke(): #use random joke API to get a random joke
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        joke = f"{joke_data['setup']} {joke_data['punchline']}"
        return joke
    else:
        return "Failed to fetch joke"

def extract_and_verify_integer(input_string):
    # Define a regular expression pattern to match "number:' followed by digits
    if input_string.startswith("!number:"):
        # Remove "number:" from the beginning of the string
        number_str = input_string[len("!number:"):]

        # Verify if the remaining string is a valid integer
        if number_str.strip().isdigit():
            # If it's a valid integer, convert it to an integer and return
            return int(number_str.strip())
        else:
            # If it's not a valid integer, return None
            return None
    else:
        # If the input string doesn't start with "number:", return None
        return None

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Step 1: BOT SETUP Without intents your bot won't respond
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you are quiet'
    elif 'hello' in lowered:
        return 'Hello there! You need to code your AI Bot here'
    elif 'roll dice' in lowered:
        return f'You rolled a {randint(1, 6)}'
    elif 'help' in lowered:
        return ('you can say !weather or !temp for weather info, !chuck norris fo a chuck norris joke, !number: and '
                'then an integer for a number fact, or !joke for a random joke (that will be bad)')
    else:
        if '!weather' in lowered:
            return print_weather()
        if '!temp' in lowered:
            return print_weather()
        elif '!chuck norris' in lowered:
            return get_random_chuck_norris_joke()
        elif '!number:' in lowered:
            number = extract_and_verify_integer(lowered)
            if number is not None:
                return get_number_fact(number)
            else:
                return 'Please enter an integer after {!Number:}'
        elif '!joke' in lowered:
            return get_random_joke()
        else:
            return "Youuuuuuuu've stumped me, type {help} for usage"


#Step 2: Message Function
async def send_message(message: Message,user_message: str) -> None:
    if not user_message:
        print('(Message was empty becuase intents were not enabled...prob)')
        return
#check to see if you need to resopnd to private messages
    if is_private := user_message[0] =='?':
        user_message = user_message[1:]

    try:
        response: str= get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

#Step 3: Handle the startup of the bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

#Step 4:  Let's handle the messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user: #The bot wrote the message, or the bot talks to itself
        return

    username: str= str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

#Step 5 Main Starting point

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()