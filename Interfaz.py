#se definen las diferentes librerias
import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
from matplotlib.figure import Figure
import matplotlib.pyplot as plt;
from PyQt5.uic import loadUi#para cargar la interfaz desde designer
from chronux.mtspectrumc import mtspectrumc

from numpy import arange, sin, pi#funciones especificas
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#para la graficacion a traves de clases y en la interfaz
import scipy.io as sio
import numpy as np
from Modelo import Biosenal
#librerias elementales
# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(211)
        
        self.axes2 = self.fig.add_subplot(212)
        
       
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        
    #este metodo me grafica al senal senoidal que yo veo al principio, mas no senales
    def compute_initial_figure(self):
        #se inicializa con cualquier senal, para probar que este graficando con canvas
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
        self.axes.set_xlim(1.0,2.0)
        self.axes.set_title("Senal seno de prueba de campo ")
    def limpiar(self):
        self.axes.clear()
        self.axes2.clear()
        
    #hay que crear un metodo para graficar lo que quiera
    def graficar_gatos(self,datos,f,numcanal,xmin,xmax):
        
        if datos.ndim==1 and f==0:
            self.axes2.clear()#limpia toda grafica tipo canal una vez se quiera volver a graficar otro canal
            self.axes2.set_xlim(xmin,xmax)#se limita de acuerdo al requerimiento en la interfaz
            self.axes2.plot(datos)
            self.axes2.set_title("Canal "+str(numcanal))
            self.axes2.set_xlabel("Muestras")
            self.axes2.set_ylabel("Amplitud")
            self.axes2.figure.canvas.draw()#dibuja todo lo anterior
        elif datos.ndim ==1 and f==1:#f para definir en que subplor graficar
            self.axes.clear()#se limpia la ventana superior del subplor para graficar los canales filtrados
            self.axes.plot(datos,color = "red")
            self.axes.set_xlim(xmin,xmax)#se definen los limites de acuerdo al canal inferior
            self.axes.set_ylabel("Amplitud")
            self.axes.set_title("Canal "+str(numcanal)+" Filtrado")
            self.axes.figure.canvas.draw()#se dibuja

        else:#para la visualizacion inicial de cada canal separado
            self.axes.clear()# se limpia la ventana superior
            for c in range(datos.shape[0]):
                self.axes.plot(datos[c,:]+c*25)#se elige un voltaje dc de 25 para separa cada canal
            self.axes.set_title("Canales con sus muestras")
            self.axes.set_ylabel("Voltaje (uV)")
            self.axes.set_xlim(xmin,xmax)
        #ordenamos que dibuje
            self.axes.figure.canvas.draw()
            
    #se crean funciones para graficar los 3 tipos de analisis en frecuencias: welch, multitaper y wavelet continuo.
    def graficar_welch(self,x1, x2,numcanal, f_min, f_max):
        if f_min==0 and f_max==0:
            self.axes.clear()#se limpia la ventana superior del subplot para graficar los canales filtrados
            self.axes.plot(x1,x2,color = "blue") #grafica todos los valores de frecuencia y potencia espectral
            self.axes.set_xlabel("frecuencia Hz")
            self.axes.set_ylabel("Amplitud")
            self.axes.set_title("Analisis welch," "Canal "+str(numcanal))
            self.axes.figure.canvas.draw()#se di
        else:
            self.axes.clear()#limpia toda grafica tipo canal una vez se quiera volver a graficar otro canal
            self.axes.set_xlim(f_min,f_max)#se limita de acuerdo al requerimiento en la interfaz, se acorta al rango de frecuencias que el usuario elija
            self.axes.plot(x1,x2)
            self.axes.set_title("Canal "+str(numcanal))
            self.axes.set_xlabel("Frecuencia Hz")
            self.axes.set_ylabel("Amplitud")
            self.axes.set_title("Analisis welch," "Canal "+str(numcanal))
            self.axes.figure.canvas.draw()
            
    def graficar_multitaper(self,x1,x2,numcanal, f_min, f_max):
        if f_min==0 and f_max==0:
            self.axes.clear()#se limpia la ventana superior del subplor para graficar los canales filtrados
            self.axes.plot(x1,x2,color = "blue")
            self.axes.set_xlabel("frecuencia Hz")
            self.axes.set_ylabel("Potencia")
            self.axes.set_title("Analisis multitaper," "Canal "+str(numcanal))
            self.axes.figure.canvas.draw()
        else:
            
            self.axes.clear()#limpia toda grafica tipo canal una vez se quiera volver a graficar otro canal
            self.axes.set_xlim(f_min,f_max)#se limita de acuerdo al requerimiento en la interfaz
            self.axes.plot(x1,x2)
            self.axes.set_title("Canal "+str(numcanal))
            self.axes.set_xlabel("Muestras")
            self.axes.set_ylabel("Potencia")
            self.axes.set_title("Analisis welch," "Canal "+str(numcanal))
            self.axes.figure.canvas.draw()
            
    def graficar_wavelet(self, x1, x2, x3, numcanal, f_min, f_max):
        if f_min==0 and f_max==0:
            self.axes.clear()
            scalogram =self.axes.contourf(x1[:], x2[:],x3[:,:],100,extend='both')
            self.axes.set_ylabel("frecuencia [Hz]")
            self.axes.set_xlabel("tiempo [s]")
            self.axes.set_title("Analisis Wavelet Continuo, " "Canal "+str(numcanal))
            self.fig.colorbar(scalogram) #se crea la barra de color
            self.axes.figure.canvas.draw()
        else:
            self.axes.clear()
            scalogram =self.axes.contourf(x1[:], x2[:],x3[:,:],100,extend='both') #se grafica para las frecuencias que el usuario decida
            self.axes.set_ylabel("frecuencia [Hz]")
            self.axes.set_xlim(f_min,f_max)
            self.axes.set_xlabel("tiempo [s]")
            self.axes.set_ylim(f_min,f_max)#se limita de acuerdo al requerimiento en la interfaz
            self.axes.set_title("Analisis Wavelet Continuo, " "Canal "+str(numcanal))
            self.fig.colorbar(scalogram)
            self.axes.figure.canvas.draw() 
    
#%%
        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    #condtructor
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('anadir_grafico.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite añadir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        #se ade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se aade el campo de graficos
        layout.addWidget(self.__sc)
        #se definen los botones para que ejecuten cada funcion requerida 
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_mostrar.clicked.connect(self.graficar_canal)
        self.boton_rango.clicked.connect(self.set_timecanal)
        self.boton_filtrar.clicked.connect(self.filtracion)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_aumentar.clicked.connect(self.aumentar_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal)
        self.boton_guardar.clicked.connect(self.guardar_senal)
        self.mostrar_welch.clicked.connect(self.welch_analisis)
        self.mostrar_multitaper.clicked.connect(self.multitaper_analisis)
        self.mostrar_wavelet.clicked.connect(self.wavelet_continuo_analisis)
        #self.boton_rango_freq.clicked.connect(self.set_f_canal)
        #hay botones que no deberian estar habilitados si no he cargado la senal
        self.boton_mostrar.setEnabled(False)
        self.boton_rango.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.boton_filtrar.setEnabled(False)
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_guardar.setEnabled(False)
        #self.mostrar_welch.setEnabled(False)
        self.mostrar_multitaper.setEnabled(False)
        self.mostrar_wavelet.setEnabled(False)
        self.mostrar_welch.setEnabled(False)
        #cuando cargue la senal debo volver a habilitarlos    

    def welch_analisis(self): #funcion que grafica el método de welch segun el canal que se elija
        canal=self.num_canal.value() #se toma el canal
        fs=self.freq_muestreo_welch.value()#se toma la frecuencia de muestreo
        tipo_ventana=self.tipo_ventana_welch.currentIndex()+1# se da a elejir el tipo de ventana al usuario
        tamano_ventana=self.tamano_ventana_welch.value() #se toma el tamano de ventana
        solapamiento=self.solapamiento_welch.value() #se toma el solapamiento en porcentaje
        self.__f_min  = self.inicio_freq.value() #se permite guardar los valores de frecuencia en el que el usuario quiere ver senal con welch
        self.__f_max = self.final_freq.value()
        datos = self.__coordinador.devolver_canal(canal, self.start.value(), self.final_2.value() )
        grafica_welch=self.__coordinador.welch(datos,fs,tipo_ventana,tamano_ventana,solapamiento) #recibe los datos y los guarda en esa variable 
        self.__sc.graficar_welch(grafica_welch[0], grafica_welch[1], self.num_canal.value(), self.__f_min, self.__f_max ) #llama a el metodo de graficacion de welch
       
    def multitaper_analisis(self): #funcion que grafica el método de multitaper segun el canal que se elija
        canal=self.num_canal.value() #canal que se aplica el multitaper
        fs=self.freq_muestreo_multitaper.value()#frecuencia de muestreo dada por el usuario
        w=self.W_multitaper.value()
        #se ingresan los parametros del multitaper
        t=self.T_multitaper.value()
        n_t=self.numero_tapers_multitaper.value()
        fmin=self.f_min_multitaper.value()
        fmax=self.f_max_multitaper.value()
        first_parametro=self.first_parameter_multitaper.value()
        #si el usuario quiere ver el espectro de la señal en determinado intervalo de frecuencias
        self.__f_min  = self.inicio_freq.value() 
        self.__f_max = self.final_freq.value()
        #se manda los datos al controlador
        datos = self.__coordinador.devolver_canal(canal,self.__x_min,self.__x_max)
        #se obtienen los datos del controlador en una nueva variable
        senal_multitaper = self.__coordinador.multitaper(datos,fs,w,t,n_t,fmin,fmax,first_parametro)
        #se mandan los datos a la funcion graficar multitaper
        self.__sc.graficar_multitaper(senal_multitaper[0], senal_multitaper[1] ,self.num_canal.value(), self.__f_min, self.__f_max )
        
    def wavelet_continuo_analisis(self): #funcion que grafica el método de multitaper segun el canal que se elija
        #se debe ingresar el canal a analizar y también los diferentes parámetros para poder hacer el calculo de wavelet continuo
        canal=self.num_canal.value()
        fs=self.freq_muestreo_wavelet.value()
        fmin=self.f_min_wavelet.value()
        fmax=self.f_max_wavelet.value()
        muestras=self.muestras_wavelet.value()
        #si el usuario quiere ver el espectro de la señal en determinado intervalo de frecuencias
        self.__f_min  = self.inicio_freq.value() 
        self.__f_max = self.final_freq.value()
        #se mandan los datos colectados al controlador
        datos = self.__coordinador.devolver_canal(canal,self.__x_min,self.__x_max)
        #se reciben los datos del controlador y se guardan en una variable
        senal_wavelet=self.__coordinador.wavelet(datos,fs,fmin,fmax,muestras)
        #de la variable obtenida se mandan estos datos a la funcion graficar wavelt
        self.__sc.graficar_wavelet(senal_wavelet[0],senal_wavelet[1],senal_wavelet[2], self.num_canal.value(), self.__f_min, self.__f_max )

        
        
    def filtracion(self):
        P = self.pond.currentIndex()+1#debido a que la indexacion comienza desde cero se le suma 1
        U = self.umb.currentIndex()+1
        L = self.lamdita.currentIndex()+1
        canal=self.num_canal.value()
        ti=self.start.value()#se toma el valor de la muestra inicial y final
        tf=self.final_2.value()
        datos = self.__coordinador.devolver_canal(canal,0,tf)#se inicializa en cero puesto, que la funcion graficar gatos,
        #recorta a nuestro xmin que necesitamos
        [A,D] = self.__coordinador.descomponer(datos)#descomposcion
        Signalfil = self.__coordinador.filtrar(D,A,U,L,P,datos)#filtracion que viene ya con la recontruccion
        self.__coordinador.paraguardar(Signalfil)#para guardar los datos de la senal filtrada
            
        self.__sc.graficar_gatos(Signalfil,1,self.num_canal.value(),ti,tf)#grafica en los limites que queremosm en el subplot superior
        self.boton_guardar.setEnabled(True)#se habilira el boton para guardar
  

    def set_timecanal(self):#esta funcion redefine nuestros recortes de la senal en la interfaz
        canal=self.num_canal.value()
        ti = 0
        self.__x_min  = self.start.value()#se vuelven a establecer la muestra inicial y la muestra final de acuerdo a la interfaz
        self.__x_max=self.final_2.value()
        datos = self.__coordinador.devolver_canal(canal,ti,self.__x_max)#se retienen los datos del canal
        self.__sc.graficar_gatos(datos,0,self.num_canal.value(),self.start.value(),self.__x_max)#segrafica con nuesto xmin necesitado
        self.boton_filtrar.setEnabled(True)#se habilita el boton filtrar
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        
    def graficar_canal(self):
        #funcion que grafica el canal por primera vez
        canal=self.num_canal.value()#se encuentra el numero del canal deseado por el usuario
        datos = self.__coordinador.devolver_canal(canal, self.__x_min, self.__x_max)#se devuelve el canal de acuerdo al modelo
        self.__sc.graficar_gatos(datos,0,self.num_canal.value(),self.__x_min,self.__x_max)#se grafica la senal en los primeros limites establecidos en la primera carga
        self.boton_rango.setEnabled(True)#se habilitan todos losbotones del panel de operaciones basicas y el rango de tiempo
        self.boton_aumentar.setEnabled(True)
        self.boton_disminuir.setEnabled(True)
        self.boton_adelante.setEnabled(True)
        self.boton_atras.setEnabled(True)
        #se activan los botones que me permiten graficar los metodos de welch, multitaper y wavelet continuo
        self.mostrar_welch.setEnabled(True)
        self.mostrar_multitaper.setEnabled(True)
        self.mostrar_wavelet.setEnabled(True)
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador#para poder realizar la comunicacion con controlador, la clase coordinador
    def adelante_senal(self):#funcion para adelantar 2000 muestras
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000 
        self.__sc.graficar_gatos(self.__coordinador.devolver_canal(self.num_canal.value(), 0, self.__x_max),0,self.num_canal.value(),self.__x_min,self.__x_max)
    def atrasar_senal(self):#funcion para retrasar 2000 muestras
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.__sc.graficar_gatos(self.__coordinador.devolver_canal(self.num_canal.value(), 0, self.__x_max),0,self.num_canal.value(),self.__x_min,self.__x_max)
    
    def aumentar_senal(self):
        ##en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
       # #extraigo por fuera mi funcion de grafico puede leer los valores
        esc = self.__coordinador.escalarSenal(0,self.__x_max,2,self.num_canal.value())#se escala para 2 por arbitrariedad
        self.__sc.graficar_gatos(esc,0,self.num_canal.value(),self.__x_min,self.__x_max)
    def disminuir_senal(self):
        esc = self.__coordinador.escalarSenal(0,self.__x_max,0.5,self.num_canal.value())#se escala para 0.5 por arbitrariedad
        self.__sc.graficar_gatos(esc,0,self.num_canal.value(),self.__x_min,self.__x_max)
    
    def guardar_senal(self):
        s = self.__coordinador.retorng()#se recuperan los datos de la senal filtrada
        salida = {}# se crea un diccionario para poder crear el .mat
        
        options = QFileDialog.Options()#para las opciones
        
        arch, _ = QFileDialog.getSaveFileName(self,"Guardar senal","","Todos los archivos (*);;Archivos mat (*.mat)*", options=options)
        #le da nombre al archivo y donde guardar
        salida['data'] = s #se crea la llave data con los valores del vector filtrado
        
        file = arch #se nombra con lo definido anteriormente
        arch = sio.savemat(file,salida)#se guarda 
       
    def cargar_senal(self):
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat
        
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir senal","","Todos los archivos (*);;Archivos mat (*.mat)*")
        self.__sc.limpiar()
        if archivo_cargado != "":
    
            #la senal carga exitosamente entonces habilito los botones
            data = sio.loadmat(archivo_cargado)
            data = data["data"]
            if data.ndim == 2:
                signal = data
                #se definen los intervalos de los botones 
                self.num_canal.setRange(0,signal.shape[0]-1)
                self.start.setRange(0,signal.shape[1])
                self.final_2.setRange(0,signal.shape[1])
                self.freq_muestreo_welch.setRange(0,10000)
                self.tamano_ventana_welch.setRange(0,10000)
                self.solapamiento_welch.setRange(0,100)
                self.freq_muestreo_multitaper.setRange(0,10000)
                self.W_multitaper.setRange(0,10000)
                self.T_multitaper.setRange(0,10000)
                self.numero_tapers_multitaper.setRange(0,1000)
                self.f_min_multitaper.setRange(0,10000)
                self.f_max_multitaper.setRange(0,10000)
                self.first_parameter_multitaper.setRange(0,10000)
                self.__coordinador.recibirDatosSenal(signal)
                self.__x_min=0
                self.__x_max=3000
                self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max),0,0,self.__x_min,self.__x_max)
                self.boton_mostrar.setEnabled(True)
            elif data.ndim ==3:
                
                
                #volver continuos los datos
                sensores,puntos,ensayos=data.shape
                senal_continua=np.reshape(data,(sensores,puntos*ensayos),order="F")
                #se definen los intervalos de los botones
                self.num_canal.setRange(0,sensores-1)
                self.start.setRange(0,puntos*ensayos)
                self.final_2.setRange(0,puntos*ensayos)
                self.freq_muestreo_welch.setRange(0,10000)
                self.tamano_ventana_welch.setRange(0,10000)
                self.solapamiento_welch.setRange(0,100)
                self.freq_muestreo_multitaper.setRange(0,10000)
                self.W_multitaper.setRange(0,10000)
                self.T_multitaper.setRange(0,10000)
                self.numero_tapers_multitaper.setRange(0,1000)
                self.f_min_multitaper.setRange(0,10000)
                self.f_max_multitaper.setRange(0,10000)
                self.first_parameter_multitaper.setRange(0,10000)
                self.freq_muestreo_wavelet.setRange(0,10000)
                self.f_min_wavelet.setRange(0,10000)
                self.f_max_wavelet.setRange(0,10000)
                self.muestras_wavelet.setRange(0,10000)
                #el coordinador recibe y guarda la senal en su propio .py, por eso no 
                #necesito una variable que lo guarde en el .py interfaz
                self.__coordinador.recibirDatosSenal(senal_continua)
            
                self.__x_min=0
                self.__x_max=5000
                #graficar utilizando el controlador
                self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max),0,0,self.__x_min,self.__x_max)
                self.boton_mostrar.setEnabled(True)
                
            
            

