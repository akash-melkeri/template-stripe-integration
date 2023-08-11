from flask import Flask
from flask import request, jsonify
import stripe
app = Flask(__name__)

app.config.from_pyfile('config.py')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.post("/stripe-webhook")
def webhook_received():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(ok=False, message="Invalid Request")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify(ok=False, message="Invalid Request")

    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))
      return jsonify(ok=False, message="Unknown Error")
    return jsonify(ok=True)


if __name__ == '__main__':
    app.run(port=6105)