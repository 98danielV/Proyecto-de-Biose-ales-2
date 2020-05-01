#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 10:37:41 2020

@author: JUAN CRUZ
"""
#se define las librerias a usar y se exporta biosenal de modelo
from Modelo import Biosenal
from Interfaz import InterfazGrafico
import sys
from PyQt5.QtWidgets import QApplication

class Principal(object):
    def __init__(self):        #se definen las propiedades de la clase principal
        self.__app=QApplication(sys.argv)#para la ejecucion
        self.__mi_vista=InterfazGrafico()#para la interfaz
        self.__mi_biosenal=Biosenal()#para definir un objeto biosenal
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)#se define el controlador
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)#se define para la visualizacion
    def main(self):
        self.__mi_vista.show()#permite la ejecucion de la vista o intefaz
        sys.exit(self.__app.exec_())#para salir
    
class Coordinador(object):#se definen la clase y metodos de contador
    def __init__(self,vista,biosenal):#propiedades de coordinador
        self.__mi_vista=vista#para la interfaz
        self.__mi_biosenal=biosenal#se define la biosenal
    def recibirDatosSenal(self,data):#recibe los datos de la senal
        self.__mi_biosenal.asignarDatos(data)
    def paraguardar(self,can):#para guardar los datos de la senal filtrada
        self.__mi_biosenal.paraguardar(can)
    def retorng(self):#para retornar los datos guardados y poder guadar con la interfaz
        return self.__mi_biosenal.retorng()
    def devolverDatosSenal(self,x_min,x_max):#devuelve la parte requerida de una senal
        return self.__mi_biosenal.devolver_segmento(x_min,x_max)
    def escalarSenal(self,x_min,x_max,escala,canal):
        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala,canal)#funcion para escalar la senal un solo canal
    def devolver_canal(self, c, xmin, xmax):#devuelve el canal requerido en los tiempos requeridos
        return self.__mi_biosenal.devolver_canal(c, xmin, xmax)
    def descomponer(self, datos):#descompone la señal a filtrar
        return self.__mi_biosenal.descompose(datos)
    def filtrar(self, detalles, aprox, treshold, lam, p , signal):#filtra segun sean las condiciones para el filtrado wavelet
        return self.__mi_biosenal.filtrar(detalles, aprox, treshold, lam, p , signal)
    def welch(self,datos,fs,tipo_ventana,tamano_ventana,solapamiento):#funcion welch que enlaza la transferencia de datos de la interfaz y el modelo
        return self.__mi_biosenal.welch_analisis(datos,fs,tipo_ventana,tamano_ventana,solapamiento)
    def multitaper(self,datos,fs,w,t,n_t,fmin,fmax,first_parametro):#funcion multitaper que enlaza la transferencia de datos de la interfaz y el modelo
        return self.__mi_biosenal.multitaper_analisis(datos,fs,w,t,n_t,fmin,fmax,first_parametro)
    def wavelet(self,datos,fs,fmin,fmax,muestras):#funcion wavelet que enlaza la transferencia de datos de la interfaz y el modelo
        return self.__mi_biosenal.wavelet_continuo_analisis(datos,fs,fmin,fmax,muestras)   
p=Principal()
p.main()#se inicializa el programa como tal