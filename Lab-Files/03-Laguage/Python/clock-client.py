from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, date, timezone
from dateutil.parser import parse as is_date
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def main():
    try:
        # Load configuration settings
        load_dotenv()
        endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        api_key = os.getenv('LS_CONVERSATIONS_KEY')

        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(api_key))

        while True:
            user_text = input('\nEnter some text ("quit" to stop)\n')
            if user_text.lower() == 'quit':
                break

            result = analyze_conversation(client, user_text)
            top_intent, entities = extract_prediction_info(result)

            display_prediction_info(result, top_intent, entities)

            handle_intent(top_intent, entities)

    except Exception as ex:
        print(f"Error: {ex}")

def analyze_conversation(client, query):
    project_name = 'Clock'
    deployment_name = 'production'
    
    with client:
        return client.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "en",
                        "text": query
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": project_name,
                    "deploymentName": deployment_name,
                    "verbose": True
                }
            }
        )

def extract_prediction_info(result):
    top_intent = result["result"]["prediction"]["topIntent"]
    entities = result["result"]["prediction"]["entities"]
    return top_intent, entities

def display_prediction_info(result, top_intent, entities):
    print("View top intent:")
    print(f"\ttop intent: {top_intent}")
    print(f"\tcategory: {result['result']['prediction']['intents'][0]['category']}")
    print(f"\tconfidence score: {result['result']['prediction']['intents'][0]['confidenceScore']}\n")

    print("View entities:")
    for entity in entities:
        print(f"\tcategory: {entity['category']}")
        print(f"\ttext: {entity['text']}")
        print(f"\tconfidence score: {entity['confidenceScore']}")
    
    print(f"query: {result['result']['query']}")

def handle_intent(top_intent, entities):
    if top_intent == 'GetTime':
        location = get_entity_value(entities, 'Location', 'local')
        print(GetTime(location))
    elif top_intent == 'GetDay':
        date_string = get_entity_value(entities, 'Date', date.today().strftime("%m/%d/%Y"))
        print(GetDay(date_string))
    elif top_intent == 'GetDate':
        day = get_entity_value(entities, 'Weekday', 'today')
        print(GetDate(day))
    else:
        print('Try asking me for the time, the day, or the date.')

def get_entity_value(entities, category, default):
    for entity in entities:
        if entity["category"] == category:
            return entity["text"]
    return default

def GetTime(location):
    location_time_mapping = {
        'local': datetime.now(),
        'london': datetime.now(timezone.utc),
        'sydney': datetime.now(timezone.utc) + timedelta(hours=11),
        'new york': datetime.now(timezone.utc) - timedelta(hours=5),
        'nairobi': datetime.now(timezone.utc) + timedelta(hours=3),
        'tokyo': datetime.now(timezone.utc) + timedelta(hours=9),
        'delhi': datetime.now(timezone.utc) + timedelta(hours=5.5),
    }

    time_now = location_time_mapping.get(location.lower())
    
    if time_now:
        return f"{time_now.hour}:{time_now.minute:02d}"
    
    return f"I don't know what time it is in {location}."

def GetDate(day):
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    
    today = date.today()
    day = day.lower()

    if day == 'today':
        return today.strftime("%m/%d/%Y")
    
    if day in weekdays:
        today_num = today.weekday()
        week_day_num = weekdays[day]
        offset = week_day_num - today_num
        return (today + timedelta(days=offset)).strftime("%m/%d/%Y")

    return 'I can only determine dates for today or named days of the week.'

def GetDay(date_string):
    try:
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        return date_object.strftime("%A")
    except ValueError:
        return 'Enter a date in MM/DD/YYYY format.'

if __name__ == "__main__":
    main()
