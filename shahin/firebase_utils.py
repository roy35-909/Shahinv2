import firebase_admin
from firebase_admin import credentials, messaging

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    except:
        print("Not Finding The Files")


def send_notification_to_tokens(tokens, title, body, data=None):
    success_count = 0
    failure_count = 0
    for token in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token
            )
            messaging.send(message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {token}: {e}")
            failure_count += 1
    return {"success_count": success_count, "failure_count": failure_count}