## How to deploy
```
# トピック作成
$ gcloud pubsub topics create slack_garbage

# 関数のデプロイ
$ gcloud functions deploy post_garbage --runtime python37 --trigger-topic slack_garbage --set-env-vars TZ=Asia/Tokyo --set-env-vars CHANNEL=$YOUR_CHANNEL --set-env-vars SLACK_TOKEN=$YOUR_SLACK_TOKEN

# 関数のテスト
$ gcloud pubsub topics publish slack_garbage

# gcloud schedulerを作成
# GUI上で
```