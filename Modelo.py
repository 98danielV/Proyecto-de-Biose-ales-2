# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 12:56:57 2018

@author: SALASDRAI
"""
#se exporta numpy y las funciones para el filtrado y lo necesario
import numpy as np
import scipy.signal as senal;
from chronux.mtspectrumc import mtspectrumc
from funciones import descomponer,reconstruccion, umbral,lamda, denoise
import pywt
class Biosenal(object):#se define la clase biosenal como el objeto modelado que es una biosenal
    def __init__(self,data=None):
        if not data==None:#constructor para asignar los datos
            self.asignarDatos(data)#se asignan los datos para canal,puntos,etc
        else:#de caso contrario iguale los canales y puntos a cero, no guarda
            self.__data=np.asarray([])
            self.__canales=0
            self.__puntos=0
    def asignarDatos(self,data):#asigna los diferentes datos de la senal
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    def paraguardar(self,can):#guarda el canal filtrado
        self.__can = can
    def retorng(self):
        return self.__can#devuelve el canal filtrado
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min>=x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[:,x_min:x_max]
    def devolver_canal(self,canal, x_min, x_max):
        #prevengo errores logicos
        if (x_min >= x_max) and (canal > self.__canales):
            return None
        elif x_min==0 and x_max==0:
            return self.__data[canal,0:5000]
        #cojo los valores que necesito en la biosenal
        return self.__data[canal,x_min:x_max]

        
    def filtrar(self,detalles,aproximacion,treshold,lam,p,signal):#se define una funcion para el filtrado
        to = umbral(detalles,aproximacion,treshold,lam,p)#se hace uso de la funcion que entrega los detalles filtrados
        return self.reconstruir(aproximacion,to,signal)#se reconstruye  y entrega la senal filtrada    
    def descompose(self,signal):#descompone la senal
        return descomponer(signal)#uso de la funcion creada
    def reconstruir(self,aproximacion,detalles,signal):#se define una reconstruccion
        return reconstruccion(aproximacion,detalles,signal.shape[0])#se define para la reconstruccion
    def escalar_senal(self,x_min,x_max,escala,canal):
        copia_datos=self.__data[canal,x_min:x_max].copy()#genera una copia de tal manera que no se alteren los datos
        return copia_datos*escala #para escalar la senal
    def welch_analisis(self,datos,fs,tipo_ventana,tamano_ventana,solapamiento):#algoritmo que realiza los calculos para obtener el analisis por welch
        #quita el nivel DC restándole la media
        datosv = np.array(datos) - np.mean(np.array(datos))
        def ceros(tamano_ventana): #creacion de la funcion de ceros que permitira anadir una cantidad equivalente a la siguiente potencia de 2 proporcionada por el usuario
            return tamano_ventana*2-tamano_ventana
        solapamiento1=(tamano_ventana*solapamiento)/100 #el solapamiento es un porcentaje y no es mayo que el tamano de ventana
        tipoventana = ['boxcar','triang','blackman','hamming','hann','bartlett','flattop','parzen','bohman'] #permite la eleccion de algunos tipos de ventana
        f,Pxx = senal.welch(np.squeeze(datosv), fs,tipoventana[tipo_ventana-1], tamano_ventana, solapamiento1, tamano_ventana, scaling='density');
        return (f, Pxx) #devuelve la frecuencia y potencia
    
    def multitaper_analisis(self,datos,fs,w,t,n_t,fmin,fmax,first_parametro):#algoritmo que realiza los calculos para obtener el analisis por multitaper
        #quita el nivel DC restándole la media
        datosv = np.array(datos) - np.mean(np.array(datos))
        #evito errores lógicos
        if fmin>=fmax:
            return None
        p=(2*w*t)-n_t #obtencion del parámetro p de los tapers
        params = dict(fs = fs, fpass = [fmin, fmax], tapers = [w, t, p], trialave = 1)
        #para que de en cualquier cantidad de datos que se elijan de la senal
        segmentos=(len(datosv)/(fs*first_parametro))
        if type(segmentos)==float:
            segmentos1=round(segmentos) #si se obtien un decimal, aproxima al valor mas cercano
            x=first_parametro*fs*segmentos1
            datos_new=datosv[:x]#nuevo vector de datos
            data1 = np.reshape(datos_new,(first_parametro*fs,segmentos1),order='F') #reshape no recibe datos flotantes por lo que se aproxima al dato mas cercano y se define un nuevo vector de datos 
            Pxx1, f1 = mtspectrumc(data1, params)
            return (f1, Pxx1) #devuelvo la frecuencia y la potencia
        data = np.reshape(datosv,(first_parametro*fs,segmentos),order='F')#generacion de la nueva matriza partir de los parametros y los datos del canal seleccionado
        Pxx, f = mtspectrumc(data, params)
        return (f, Pxx)
    def wavelet_continuo_analisis(self,datos,fs,fmin,fmax,num_muestras): #algoritmo que realiza los calculos para obtener el analisis por wavelet
        sampling_period =  1/fs #periodo de muestreo
        Frequency_Band = [fmin, fmax] # Banda de frecuencia a analizar
        scales = np.arange(1, num_muestras)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
        N=datos.shape[0]
        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N
        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet
        [coef, freqs] = pywt.cwt(datos, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        return time, freqs, power


