import boto3

def lambda_handler(event, context):
    
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.c1a86732-9d3c-4d4e-84ed-fac474aea839"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])
def sent_to_q(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='DroneQueue')
    response = queue.send_message(MessageBody = message)

#start added
def read_q():
    s3 = boto3.resource("s3")
    s = s3.Object("cokecount", "count").get()["Body"].read()
    
    return s 
#end added

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "liftoff":
        return liftoff()
    elif intent_name == "target":
        return target()
    elif intent_name == "count":
        return count()
    elif intent_name == "land":
        return land(intent)
    elif intent_name == "error":
            return error()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Sentry - Thanks"
    speech_output = "Thank you for using Sentry.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Sentry"
    speech_output = "Welcome to Sentry. " \
                    "You can ask me to take off, land, or count. " 
    reprompt_text = "Please ask me to take off, land, or count. " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
#"There are people trying to benefit you and then there are people trying to put it in your butt"
#       -Raz 2017
def liftoff():
    session_attributes = {}
    card_title = "Lift off!"
    reprompt_text = ""
    sent_to_q("takeoff")
    should_end_session = False
   
    
    speech_output = "T minus 5 seconds to lift off "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def count():
    session_attributes = {}
    card_title = "Sentry Count"
    reprompt_text = ""
    sent_to_q("count")
    should_end_session = False

    speech_output = "There are " + read_q() + " objects "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def error():
    session_attributes = {}
    card_title = "Error"
    reprompt_text = ""
    sent_to_q("error")
    should_end_session = False

    speech_output = "Please try again"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def land(intent):
    session_attributes = {}
    card_title = "Sentry Landing"
    speech_output = "Fuck" \
                    "Please try again."
    reprompt_text = ""
    sent_to_q("land")
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def target(intent):
    session_attributes = {}
    card_title = "Searching for Target"
    speech_output = "Is the target in view? idk I'm just a robot who works for the cia"
    
    reprompt_text = ""
    sent_to_q("target")
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Standard",
            "title": title,
            "content": output,
            "image": {
                "smallImageUrl": "https://carfu.com/resources/card-images/race-car-small.png",
                "largeImageUrl": "https://carfu.com/resources/card-images/race-car-large.png"
          }
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
