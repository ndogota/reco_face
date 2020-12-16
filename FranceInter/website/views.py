from django.http import HttpResponse
from django.shortcuts import render
from matplotlib import patches
from PIL import Image
from .functions import *

import matplotlib.pyplot as plt
import numpy as np
import base64


def base(request, name_page):
    debug = False

    if request.method == 'POST':
        if request.POST['btn_start']:
            image = request.FILES['input_image']
            max_persons = request.POST.get('input_max_persons')
            message_fr = request.POST.get('input_message').replace("__max__", max_persons).replace("__actuel__", str(
                get_max_persons(get_objects_from_image(image, debug), debug))) if request.POST.get(
                'input_message') != '' else str(max_persons) + "personnes maximums dans le studio, merci de respecter " \
                                                               "les distances de sécurité. Vous êtes " + str(
                get_max_persons(get_objects_from_image(image, debug), debug)) + " personnes actuellement dans la " \
                                                                                "salle. "

            im = np.array(Image.open(image), dtype=np.uint8)
            fig, ax = plt.subplots(1)
            ax.imshow(im)
            json = get_objects_from_image(image, debug)
            detect_color = 'g' if int(get_max_persons(json, debug)) <= int(max_persons) else 'r'
            for obj in json['objects']:
                if obj['object'] == 'person' and obj['confidence'] >= 0.550:
                    rect = patches.Rectangle((obj['rectangle']['x'], obj['rectangle']['y']), obj['rectangle']['w'],
                                             obj['rectangle']['h'], linewidth=2, edgecolor=detect_color,
                                             facecolor='none')
                    ax.add_patch(rect)

            if detect_color == 'r':
                message_en = translate_text(message_fr, 'en', debug)
                text_to_speech(message_fr, 'fr', 'audio_fr', debug)
                text_to_speech(message_en, 'en', 'audio_en', debug)
                merge_audio('audio_fr', 'audio_en')
                audio_path = '/static/merged_audio.wav'
            else:
                audio_path = None

            plt.axis('off')
            image_modified_path = '/static/imgModified.' + image.name.split(".")[1].lower()
            if os.path.exists('website' + image_modified_path):
                os.remove('website' + image_modified_path)
            fig.savefig('website' + image_modified_path, bbox_inches='tight', pad_inches=0)
            return render(request, name_page, {'image': image_modified_path, 'audio_path': audio_path,
                                               'style': 'width: 100%; height: 100%'})

    return render(request, name_page)


def process_image(request, debug=False):
    max_persons = 5

    if request.method == 'POST':
        frame = request.POST['frame']
        imgdata = base64.b64decode(frame)
        im = np.array(Image.open(imgdata), dtype=np.uint8)
        fig, ax = plt.subplots(1)
        ax.imshow(im)
        json = get_objects_from_image(frame, debug)
        detect_color = 'g' if int(get_max_persons(json, debug)) <= int(max_persons) else 'r'
        for obj in json['objects']:
            if obj['object'] == 'person' and obj['confidence'] >= 0.550:
                rect = patches.Rectangle((obj['rectangle']['x'], obj['rectangle']['y']), obj['rectangle']['w'],
                                         obj['rectangle']['h'], linewidth=2, edgecolor=detect_color,
                                         facecolor='none')
                ax.add_patch(rect)

        plt.axis('off')
        frame_modified_path = '/static/frameModified.png'
        if os.path.exists('website' + frame_modified_path):
            os.remove('website' + frame_modified_path)
        fig.savefig('website' + frame_modified_path, bbox_inches='tight', pad_inches=0)


def image(request):
    return base(request, 'pages/image.html')


def video(request):
    return render(request, 'pages/video.html')


def processing(request):
    process_image(request)
    frame_binary = open('/static/frameModified.png', 'rb')
    frame_read = frame_binary.read()
    frame_64_encode = base64.encodebytes(frame_read)
    return HttpResponse(frame_64_encode)
