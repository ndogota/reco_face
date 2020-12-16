import json
import uuid
import os
import requests
import azure.cognitiveservices.speech as speechsdk

from pydub import AudioSegment


# API Azure de reconnaissance d'objets / personnes
def get_objects_from_image(image_path, debug=False):
    face_api_url = 'https://franceinteretna.cognitiveservices.azure.com/vision/v2.0/detect'
    headers = {'Content-Type': 'application/octet-stream',
               'Ocp-Apim-Subscription-Key': os.environ['Key-Face-Api']}

    # api = requests.post(face_api_url, headers=headers, data=open(image_path, 'rb'))
    api = requests.post(face_api_url, headers=headers, data=image_path)
    if debug:
        print(json.dumps(api.json(), sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': ')))
    return api.json()


def get_max_persons(json, debug=False):
    nbr = 0
    for obj in json['objects']:
        nbr += 1 if obj['object'] == 'person' else 0
        if debug:
            print(obj)
    return nbr


# API Azure de traduction
def translate_text(text, to, debug=False):
    translate_api_url = 'https://franceinterservices.cognitiveservices.azure.com/translator/text/v3.0/translate?api-version=3.0&to=' + to
    headers = {'Content-type': 'application/json',
               'Ocp-Apim-Subscription-Key': os.environ['Key-Translate'],
               'X-ClientTraceId': str(uuid.uuid4())}
    body = [{'text': text}]

    request = requests.post(translate_api_url, headers=headers, json=body)
    response = request.json()
    if debug:
        print(json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': ')))
    return response[0]['translations'][0]['text']


# API Azure de text-to-speech
def text_to_speech(text, language, audio_filename, debug=False):
    speech_key, service_region = os.environ['Key-Speech'], "westeurope"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    if language == 'en':
        speech_config.speech_synthesis_voice_name = "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)"
    elif language == 'fr':
        speech_config.speech_synthesis_voice_name = "Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural)"

    audio_output = speechsdk.audio.AudioOutputConfig(filename=os.getcwd() + '/website/static/' + audio_filename + '.wav')

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    result = speech_synthesizer.speak_text_async(text).get()

    if debug:
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to [{}] for text [{}]".format(audio_filename, text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")


def merge_audio(filename_audio_1, filename_audio_2):
    audio_1 = AudioSegment.from_wav(os.getcwd() + '/website/static/' + filename_audio_1 + '.wav')
    audio_2 = AudioSegment.from_wav(os.getcwd() + '/website/static/' + filename_audio_2 + '.wav')

    merged_audio = audio_1 + audio_2
    merged_audio.export(os.getcwd() + '/website/static/merged_audio.wav', format="wav")
