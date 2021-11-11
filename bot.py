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
userClient = slack.WebClient(token=os.environ['SLACK_USER_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

welcome_messages = {}


class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to our server! \n\n'
                '*Get started by reading the following information!* \n\n'
                ':small_red_triangle:*If a disconnected student joins the classroom and has not sent you a message* - '
                'close the session in 5-7 minutes without a message from the student. \n\n'
                ':small_red_triangle:*If a student has not replied in a while* - After 10 minutes send them a follow '
                'up '
                'message. 5 minutes after that with no response send them a closing message and close the session. \n\n'
                ':small_red_triangle:*If a student is finished working for the day* - If the student does not end the '
                'session, please end when they disconnect with a closing message.'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    welcome = WelcomeMessage(channel, user)
    messagesend = welcome.get_message()
    response = client.chat_postMessage(**messagesend)
    welcome.timestamp = response['ts']

    if channel not in welcome_messages:
        welcome_messages[channel] = {}
    welcome_messages[channel][user] = welcome


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    message_id = event.get('ts')
    text = event.get('text')
    # print(event)

    if user_id is not None and BOT_ID != user_id:
        if text.lower() == 'start':
            send_welcome_message(f'@{user_id}', user_id)

    userClient.chat_delete(channel=channel_id, ts=message_id)


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
