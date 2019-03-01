#Autores:
#Diego Estrada 18540
#Isabel Ortiz 18176
#Fecha de entrega: 01/03/2019
#Descripción: Este programa realiza una simulación de un sistema operativo, con RAM y número de CPUs 
#determinados, es posible cambiar los parámetros con el fin de comparar el rendimiento.

import simpy
import random
import math

#Parámetros para variar el rendimiento
CapacidadRAM = 100 #Capacidad de RAM
NumeroProcesos = 200 # Cantidad de procesos a realizar
NumeroCPU = 1 #Numeros de CPU
Interval = 1 # Intervalo
InstruccionesCPU = 6  # Cuantas instrucciones realiza el CPU por unidad de tiempo
TiempoOperacionInOut = 1  # Tiempo de operacion I/O
TiemposDeProcesos = []  # Lista para almacenar tiempos
random.seed(300) 

#-----Clase que crea los componentes de un Sistema Operativo como lo son los CPU's y la RAM------#

class SistemaOperativo:

    def __init__(self, env):
        self.RAM = simpy.Container(env, init=CapacidadRAM, capacity=CapacidadRAM)
        self.CPU = simpy.Resource(env, capacity=NumeroCPU)

#-----Clase que nos ayudara a modelar como trabaja un proceso dentro de una computadora-----#
        
class Proceso:

    def __init__(self, id, no, env, sistema_operativo):
        # Atributos del proceso
        self.id = id
        self.no = no
        self.instrucciones = random.randint(1, 10)
        self.memoriaRequerida = random.randint(1, 10)
        self.env = env
        self.terminated = False
        self.sistema_operativo = sistema_operativo
        self.createdTime = 0
        self.finishedTime = 0
        self.totalTime = 0
        self.proceso = env.process(self.procesar(env, sistema_operativo))

    # Metodos de siguen el comportamiento de un proceso
    def procesar(self, env, sistema_operativo):
        inicio = env.now
        self.createdTime = inicio
        print('%s: Creado en %d' % (self.id, inicio))  # Se crea el proceso
        with sistema_operativo.RAM.get(self.memoriaRequerida) as getRam:  # Se pide la RAM
            yield getRam

            # Inicio uso de RAM
            print('%s: Obtiene RAM en %d (Estado: Wait)' % (self.id, env.now))
            siguiente = 0  # Nos indica el orden sobre que va despues de running
            while not self.terminated:
                with sistema_operativo.CPU.request() as req:  # Se asegura de pedir el CPU hasta que termine
                    print('%s: Espera al CPU en %d (Estado: Wait)' % (self.id, env.now))
                    yield req

                    # Inicio uso de CPU
                    print('%s: Obtiene CPU en %d (Estado: Running)' % (self.id, env.now))
                    for i in range(InstruccionesCPU):  # El numero de operaciones a realizar del proceso
                        if self.instrucciones > 0:
                            self.instrucciones -= 1  # Si siguen habiendo instrucciones realiza la operacion
                            siguiente = random.randint(1, 2)  # Indica si va a seguir operando las instrucciones o va a esperar
                    yield env.timeout(1)  # Cantidad de tiempo en que tarda el CPU en procesar un instruccion

                    # Inicio proceso I/O
                    if siguiente == 1:
                        print('%s: Espera operacion I/O en %d (Estado: I/O)' % (self.id, env.now))
                        yield env.timeout(TiempoOperacionInOut)

                    # Fin de uso de RAM 
                    if self.instrucciones == 0:
                        self.terminated = True  # En caso de que se terminen las instrucciones por completar

            print('%s: Terminado en %d (Estado: Terminated)' % (self.id, env.now))
            sistema_operativo.RAM.put(self.memoriaRequerida)  # Regresa la RAM que se utilizo
        fin = env.now
        self.finishedTime = fin  # Termina
        self.totalTime = int(self.finishedTime - self.createdTime)  # Se obtiene el tiempo en que cada proceso estuvo en la computadora
        TiemposDeProcesos.insert(self.no, self.totalTime)


# Generador de procesos
def proceso_generator(env, sistema_operativo):
    for i in range(NumeroProcesos):
        tiempo_creacion = math.exp(1.0/Interval)
        Proceso('Proceso %d' % i, i, env, sistema_operativo)
        yield env.timeout(tiempo_creacion)  # Tiempo que tardara en crearse cada proceso
        

#-------------------Se corre el programa--------------------------#

env = simpy.Environment()  # Se crea ambiente
sistema_operativo = SistemaOperativo(env)  # Se crea sistema operativo
env.process(proceso_generator(env, sistema_operativo))  # Se crean procesos
env.run()

#------Se calcula el Promedio de tiempo que esta cada proceso en la computadora y desviacion estandar------#

def promedio(s): 
    return (sum(s)*1.0)/len(s)
tiempo_promedio_total = promedio(TiemposDeProcesos)  # Se obtiene el tiempo promedio
varianza_tiempo_total = map(lambda x: (x - tiempo_promedio_total) ** 2, TiemposDeProcesos)
desvest_tiempo_total = math.sqrt(promedio(list(varianza_tiempo_total)))  # Se obtiene la desviacion estandar

print ("El promedio de tiempo es de: " + str(tiempo_promedio_total) + ", y su desviacion estandar es de: " + str(desvest_tiempo_total))

