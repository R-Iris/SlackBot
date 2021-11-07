import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


@app.route('/PMtasks', methods=['POST'])
def PMtasks():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    tasks = "Wondering which PM to message? Here's a list! :grinning:" \
            "\n\n:clock1: *Asking for breaks*: @ Nain Haider" \
            "\n:page_facing_up: *ER related questions*: @ Jaclyn Combot" \
            "\n:ant: *Reporting bugs*: @ Fatima Mansoor Pal"

    client.chat_postMessage(channel=channel_id, text=tasks)

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
