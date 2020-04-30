def post_garbage(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
        event. The `data` field contains the PubsubMessage message. The
        `attributes` field will contain custom attributes if there are any.
        context (google.cloud.functions.Context): The Cloud Functions event
        metadata. The `event_id` field contains the Pub/Sub message ID. The
        `timestamp` field contains the publish time.
    """
    from slacker import Slacker
    import datetime
    import os

    def get_week_number(dt):
        """
        calculate week number from datetime
        :param dt:
        :return week: week number
        """
        day = dt.day
        week = 0
        while day > 0:
            week += 1
            day -= 7
        return week

    try:
        slack_token = os.environ['SLACK_TOKEN']
    except KeyError:
        print("ERROR! Please define SLACK_TOKEN environment")
        os._exit(1)
    channel = os.environ.get('CHANNEL', 'random')
    icon_emoji = os.environ.get('ICON_EMOJI', ':owl:')

    number_of_week_settings = [
        {
            'weekday_numbers': [2, 5],
            'week_numbers': [1, 2, 3, 4, 5],
            'message': '明日は可燃ゴミの日'
        },
        {
            'weekday_numbers': [4],
            'week_numbers': [1, 2, 3, 4, 5],
            'message': '明日は古紙・ペットボトルの日'
        },
        {
            'weekday_numbers': [1],
            'week_numbers': [1, 2, 3, 4, 5],
            'message': '明日はビン・カン・プラの日'
        },
        {
            'weekday_numbers': [4],
            'week_numbers': [1, 3],
            'message': '明日は不燃ゴミの日'
        }
    ]

    slack = Slacker(slack_token)
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

    for number_of_week_setting in number_of_week_settings:
        # check weekday
        if tomorrow.weekday() not in number_of_week_setting['weekday_numbers']:
            continue
        # check week of number
        if get_week_number(tomorrow) not in number_of_week_setting['week_numbers']:
            continue
        slack.chat.post_message(channel, number_of_week_setting['message'], icon_emoji=icon_emoji)
