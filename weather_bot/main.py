def post_temperature(event, context):
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
    import requests

    KELVIN = -273
    LOWER_TEMPERATURE_LIMIT = os.environ.get('LOWER_TEMPERATURE_LIMIT', 5)
    try:
        API_KEY = os.environ['API_KEY']
    except KeyError:
        print("ERROR! Please define API_KEY environment")
        os._exit(1)
    # デフォルトでは東京駅の緯度経度とする
    LATITUDE = os.environ.get('BOT_LATITUDE', 35.6809591)
    LONGITUDE = os.environ.get('BOT_LONGITUDE', 139.7673068)

    def get_weather_data():
        """OpenWeatherMapの5day/3hour forecast data apiから結果を取得する

        Returns:
            json: API取得結果
        """
        url = "https://community-open-weather-map.p.rapidapi.com/forecast"
        querystring = {"lat": LATITUDE, "lon": LONGITUDE}
        headers = {
            'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
            'x-rapidapi-key': API_KEY}
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        return response.json()

    def get_unixtime(days):
        """日付差異を与えて、日付以下を切り捨てたunixtimeを返す

        Args:
            days (int): 日付差異

        Returns:
            int: unixtime
        """
        day = datetime.datetime.now() + datetime.timedelta(days=days)
        day = day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0).timestamp()
        return day

    def get_tomorrow_temperature_data():
        """明日の温度リストを返す

        Returns:
            array: 明日の温度リスト
        """
        all_data = get_weather_data()
        tomorrow_unixtime = get_unixtime(1)
        day_after_tomorrow_unixtime = get_unixtime(2)
        temperatures = []
        for l in all_data['list']:
            if tomorrow_unixtime <= l['dt'] < day_after_tomorrow_unixtime:
                temperatures.append(l['main']['temp'] + KELVIN)
        return temperatures

    # 明日の最低気温が設定気温を下回るかチェック
    temperatures = get_tomorrow_temperature_data()
    min_temperature = round(min(temperatures), 2)
    if min_temperature > LOWER_TEMPERATURE_LIMIT:
        return 0

    # slackメッセージ作成
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    slack_message = '明日{}は、最低気温が{}℃です :snowflake:'.format(
        tomorrow.strftime('%Y-%m-%d'), min_temperature)

    # slackへ投稿
    try:
        slack_token = os.environ['SLACK_TOKEN']
    except KeyError:
        print("ERROR! Please define SLACK_TOKEN environment")
        os._exit(1)
    channel = os.environ.get('CHANNEL', 'bot_environment')
    icon_emoji = os.environ.get('ICON_EMOJI', ':seedling:')
    slack = Slacker(slack_token)
    slack.chat.post_message(
        channel,
        slack_message,
        icon_emoji=icon_emoji)
