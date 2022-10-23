import os, os.path
from google.cloud import storage
from google.cloud import speech
from nltk import PorterStemmer
from .textrank import *

# 스토리지 업로드
def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(contents)

    print(
        "{} with contents {} uploaded to {}.".format(
            destination_blob_name, contents, bucket_name
        )
    )


# STT_English
def transcribe_gcs_en(gcs_uri, content, sample_rate_hertz):
    print("영어 STT 시작")
    ## 가중치 파일로드
    words_list = list()
    with open("text/sciwords.txt") as f:
        text = f.read()
        for i in text.split():
            words_list.append(i)

    ## 가중치 부여
    boost = 10.0
    speech_contexts_element = {"phrases": words_list, "boost": boost}
    speech_contexts = [speech_contexts_element]

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        # wav 파일이므로 Linear16, Flac 파일은 FLAC
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        # hertz 16000, 44100(2개의 오디오 채널), Flac은 또 다르다.
        sample_rate_hertz=sample_rate_hertz, # 48000
        language_code="en-US",
        audio_channel_count=2,
        enable_separate_recognition_per_channel=True,
        enable_automatic_punctuation=True,
        speech_contexts = speech_contexts
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result()

    text_2 = ''
    text_1 = ''
    time_stamp = []


    for result in response.results:
        if result.channel_tag == 2:
            text_2 += result.alternatives[0].transcript + ' '
        else:
            text_1 += result.alternatives[0].transcript + ' '
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            time_stamp.append({'word': word,
                               'start_time': start_time.total_seconds(),
                               'end_time': end_time.total_seconds()})

    print("영어 STT 완료")

    return text_2, time_stamp


# STT_Korean
def transcribe_gcs_kor(gcs_uri, content, sample_rate_hertz):
    print("한국어 STT 시작")
    # ## 가중치 파일로드
    # words_list = list()
    # with open("text/sciwords.txt") as f:
    #     text = f.read()
    #     for i in text.split():
    #         words_list.append(i)

    # ## 가중치 부여
    # boost = 10.0
    # speech_contexts_element = {"phrases": words_list, "boost": boost}
    # speech_contexts = [speech_contexts_element]

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        # wav 파일이므로 Linear16, Flac 파일은 FLAC
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        # hertz 16000, 44100(2개의 오디오 채널), Flac은 또 다르다.
        sample_rate_hertz=sample_rate_hertz,  # 48000
        language_code="ko-KR",
        audio_channel_count=2,
        enable_separate_recognition_per_channel=True,
        enable_automatic_punctuation=True
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result()

    text_2 = ''
    text_1 = ''

    for result in response.results:
        if result.channel_tag == 2:
            text_2 += result.alternatives[0].transcript + ' '
        else:
            text_1 += result.alternatives[0].transcript + ' '

    print("한국어 STT 완료")

    return text_2


# STT Highlighting
def highlight_keywords(text):
    # text = transcribe_gcs_en() 첫번째 return 값 (STT script)
    stopwords = get_stopwords()
    keywords = get_keywords(text, word_num=10, stopwords_list=stopwords)
    pro_keywords = postprocess_keywords(keywords)
    keywords_only = [word for (word, _) in pro_keywords]

    stemmer = PorterStemmer()
    keywords_stem = [stemmer.stem(word) for word in keywords_only]

    words_list_text = text.split()
    for idx, word_in_text in enumerate(words_list_text):
        word_stem = stemmer.stem(word_in_text)
        if word_stem in keywords_stem:
            words_list_text[idx] = '<span style="color:#ff58b0; text-decoration:underline; font-weight:bold;" >' + word_in_text + '</span>'

    text_highlight = ' '.join(words_list_text)

    return text_highlight


# Keyword Timestamps in STT script
def get_kw_timestamps(text, timestamps):
    # kw_timestamps = transcribe_gcs_en() 두번째 return 값 (각 word의 timestamps dict)
    stopwords = get_stopwords()
    keywords = get_keywords(text, word_num=10, stopwords_list=stopwords)
    pro_keywords = postprocess_keywords(keywords)
    keywords_only = [word for (word, _) in pro_keywords]

    stemmer = PorterStemmer()
    keywords_stem = [stemmer.stem(word) for word in keywords_only]

    keyword_timestamps = {keyword: [] for keyword in keywords_only}
    for word_dict in timestamps:
        word_stem = stemmer.stem(word_dict['word'])
        if word_stem in keywords_stem:
            keyword_ori = keywords_only[keywords_stem.index(word_stem)]
            keyword_timestamps[keyword_ori].append(word_dict['start_time'])

    return keyword_timestamps