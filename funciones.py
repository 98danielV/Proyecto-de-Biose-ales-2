# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 17:21:30 2020

@author: JUAN CRUZ
"""

import numpy as np;
import scipy.io as sio;
# Se definen los vectores de wavelet y scale para la descomposicion
wavelet = [-1/np.sqrt(2) , 1/np.sqrt(2)];
scale = [1/np.sqrt(2) , 1/np.sqrt(2)];
# Se definen los inversos para la reconstruccion
wavelet_inv = [1/np.sqrt(2) , -1/np.sqrt(2)];
scale_inv = [1/np.sqrt(2) , 1/np.sqrt(2)];
#se crea la funcion descomponer, la cual hace parte del algoritmo de haar
def descomponer(signal):
    signal = np.squeeze(signal);#se eliminan corchetes inncesarios
    longitud_original = signal.shape[0];#se calcula la longiutd de la señal
    senalpdescomponer = signal#se redefine para efectos practicos
    jmax = np.floor(np.log2(longitud_original/len(wavelet))) #formula para obtener el numero maximo dde detalles
    detalles=[]#se almacenan los detalles en una lista
    for i in range(int(jmax)-1):  #se crea un cilo for para iterar hasta el numero de jmax obtenida
        if (senalpdescomponer.shape[0] % 2) != 0: #se añaden ceros si la señal no es de longitud par
            print("Anadiendo ceros");
            senalpdescomponer = np.append(senalpdescomponer, 0);
        Aprox = np.convolve(senalpdescomponer,scale,'full');# se hace la convolucion con el vector scale para el primer filtro
        #a partir del primero toma cada dos
        Aprox = Aprox[1::2];
        Detalles= np.convolve(senalpdescomponer,wavelet,'full');# se hace la convolucion con el vector wavelet para obtener los detalles
        #a partir del primero toma cada dos
        Detalles=list(Detalles)  # Se vuelve una lista para poder usar el método append
        detalles.append(Detalles[1::2]);# se allade el detalle a la lista
        senalpdescomponer = Aprox; # se redefine la señal a descomponer como la ultima aproximacion segun sea
    return Aprox,detalles #entrega solo la ultima aproximacion y la lista con todos los detalles (cantidad jmax)

def reconstruccion(aproxf,Detalles,lo):#reconstruye a partir de la aproximacion final y detalles
    X = aproxf # se redefine aproxf con el fin de evitar errores
    Detalles = list(Detalles) # se vuelve Detalles una lista para evitar errores con la funcion len
    for i in range(len(Detalles)):
        npoints_aprox=X.shape[0];#se encuentra el numero de puntos de la aproximacion
        Aprox_inv = np.zeros((2*npoints_aprox));# se genera un array de ceros del doble del numero de puntos
        Aprox_inv[0::2] = X;#se invierte la aproximacion
        Aprox_inv[1::2] = 0;
       
        A = np.convolve(Aprox_inv,scale_inv,'full')#se hace convolucion con la aporximacion inversa y el vector scale inverso
        npoints_aprox=len(Detalles[-(i+1)])#como arranca con el ultimo detalle se usa -(i+1), propiedad de las listas
        Detail_inv = np.zeros((2*npoints_aprox));#se encuentra el inverso del detall
        Detail_inv[0::2] = Detalles[-(i+1)];#se coloca desde el ultimo detalle
        Detail_inv[1::2] = 0;
        
        D = np.convolve(Detail_inv,wavelet_inv,'full')#convolucion del detalle inverso con el vector wavelet inverso
        X = A+D
        if i==(len(Detalles)-1):#para evitar errores de indexacion
            X=X[0:lo]#cuando este en la ultima interacion, se realiza el slicing hasta la longitud de la señal
            return X
            break# se rompe el ciclo
        elif X.shape[0]>len(Detalles[-(i+2)]) and i!=len(Detalles):#condicion para las otras iteraciones
            print('Quitando ceros');
            X = X[0:len(Detalles[-(i+2)])]#se realiza el recorte del vector hasta el detalle con la
            #anterior derivacion del anterior nivelpor lo que va -(i+2)
    
    return X

#Funciones filtrado
def umbral(detail,aprox,threshold,lam,p):#se define un funcion que reuna todas las opciones del filtrado wavelet

    if p==1:
        #one
        l = lamda(lam,detail,aprox)# se hace uso de la funcion para encontrar el lambda
        return np.squeeze(denoise(detail,threshold,l))#se ejecuta la funcion denoise que ya define el umbral suave o fuerte
    elif p==2:
        #single

        stdc=(np.median(np.absolute(detail[0]))/0.6745)
        # se define un sigma para todos los detalles
        l = lamda(lam,detail,aprox)# se calcula el lamda para definir el umbral, que es l*stdc
        return np.squeeze(denoise(detail,threshold,l*stdc))#se calcula de acuerdo al umbral suave o fuerte
        
    elif p==3:
        #multiple
        stdc = []#se define una lista que acumule la cantidad de sigmas para cada detalle
        l = lamda(lam,detail,aprox)#se calcula lamdda
        for i in range(len(detail)):# se recorre para cada detalle
            stdc.append(np.median(np.absolute(detail[i]))/0.6745)#se calcula para cada detalle
            detail[i] = denoise([detail[i]],threshold,l*stdc[i])#se redefine el detalle
        return np.squeeze(detail)# se entrega el vector de detalles sin excesos de corchetes inncesarios
    else:
        print('Opción incorrecta')
    
def lamda(lam,detail,aprox):# funcion para calcula lambda
    N = aprox.shape[0]
    for k in detail:
        N+=len(k)# N es la suma del tamaño de cada detalle con el tamaño de la ultima aproximacion
    #tipo de lambda
    if lam == 1:
        universal = np.sqrt(2*np.log2(N))#se define de acuerdo a formula
        return universal
    elif lam == 2:
        minimax = 0.3936+0.1829*(np.log(N)/np.log(2))#se define de acuerdo a formula
        return minimax
    elif lam == 3:
        x= reconstruccion(aprox,detail,N)#se necesita la señal recostruida para proceder con cada muestra de estas
        n = np.size(x)#se calcula el tamaño de esta señal
        sx2 =np.sort(abs(x))**2#de acuerdo a formula
        c = np.linspace(n-1,0,n)#vector n-1:-1:0
        s = np.cumsum(sx2)+c*sx2#se calcula esta operacion de acuerdo a la formula
        risks = (n -(2*np.arange(n))+s)/n#se define el vector de riesgo
        best = np.argmin(risks)# el mejor es el minimo valor
        sure = np.sqrt(sx2[best])# se calcula de acuerdo a la formula
        return sure
    
def denoise(detail,treshold,l):#funcion para el treshold o umbral
    if treshold==1:
        for i in range(len(detail)):#duro
            deta = np.array(detail[i])
            deta[np.absolute(deta)<l] = 0#si no es mayor al umbral este punto en el detalle se vuelve cero
            detail[i] = list(deta)#se añade tipo lista para evitar errores
        return detail#devuelve los detalles filtrados
    elif treshold==2:
        #suave
        dn = np.array(detail)#vuelve los detalles un array para mejor manipulacion
        for i in range(len(detail)):#para cada detalle
           
            dn[i] = np.sign(dn[i])*(np.absolute(dn[i])-l)# se calcula de acuerdo a teoría
            deta = dn[i]#se definie deta para evitar errores
            deta[deta<l] = 0#detalle menor al umbral suave es cero
            detail[i] = list(deta)# se vuelve a escribir en lista para evitar errores
        return detail #se retornan los detalles filtrados
    else:
        return 'No existe'
    