# Import packages
import argparse
import pickle
import os
import sys
import cv2
import imutils
import numpy as np
from tensorflow.keras.models import load_model

#________________________________TEMPERATURE - 7 segmentos___________________________________________


def cortar_imagens(imagens, cortes):
    '''
    Cortar imagens
    '''
    rotate = imutils.rotate(imagens, angle=180)
    pts1 = np.float32(
        [cortes["TL"], # top left
        cortes["TR"], # top right
        cortes["BL"], # bottom left
        cortes["BR"]] # bottom right
    )
    pts2 = np.float32(
            [[0,0], # top left
              [350,0], # top right
              [0,250], # bottom left
              [350,250]] # bottom right
        )

    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    result = cv2.warpPerspective(rotate, matrix, (350,250))
    return result


def cortar_digitos(result, cortes, digit_image=None):
    #for img in result:
    digit = []
    for i in range(len(LW)):
        digit_image = result[cortes["y1"]:cortes["y2"], cortes["LW"][i]:cortes["LW2"][i]]
        cv2_imshow(digit_image)
        if np.mean(digit_image) <= 50: 
            digit_ = None
            digit.append(digit_)
        else: 
            # transformar em esacala de cinza
            digit_image = cv2.cvtColor(digit_image, cv2.COLOR_BGR2GRAY)
            # remoção de ruído
            digit.append(
                cv2.medianBlur(
                    (cv2.GaussianBlur(
                        (cv2.bilateralFilter(
                            digit_image, 30, 17, 17
                            )
                        ), (5,5), 0)
                    ), 5
                    )
                )
      
    return digit
        

def threshold(digit):
    #Transformar digitos para preto e branco
    thresh_list = []
    for img in digit:
        _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        thresh_list.append(thresh)
    return thresh_list


cortes ["TL"]
cortes ["TR"]
cortes ["BL"] 
cortes ["BR"]
cortes ["LW"]
cortes ["LW2"]
cortes ["y1"]
cortes ["y2"]
def Prever_digitos(input_image, model_name, labelmap, cortes):
    
    with open(labelmap, "rb") as arquivo_tradutor:
        lb = pickle.load(arquivo_tradutor)
    modelo = load_model(model_name)
               
    list_digit_final = (
        threshold(
            cortar_digitos(
                cortar_imagens(
                    input_image, cortes
                    ), cortes
                )
            )
        )

    # Loop over every image and perform detection
    dic_saida = {}
    previsao = []
    acur = []
    for img in list_digit_final:
        if img is None:
            # previsão em formato de número
            previsao.append('0')
            acur.append('0')
            pass
        else: 
            imagem = cv2.resize(img, (100, 115))
            # adicionar uma dimensão no incício e uma no final para o Keras funcionar
            imagem_digito = np.expand_dims(imagem, axis=2)
            imagem_digito = np.expand_dims(imagem_digito, axis=0)
            # return digit
            digito_previsto = modelo.predict(imagem_digito)
            np.set_printoptions(suppress=True)
            score = 100 * np.max(digito_previsto)
            acur.append(score)
            # traduzir para digito
            digito_previsto = lb.inverse_transform(digito_previsto)[0]
            previsao.append(digito_previsto)
            # Juntar os valores:
    texto_previsao = float("".join(map(str, previsao)))/10
    dic_saida = {'value': texto_previsao, 'acur': acur}
    return dic_saida
