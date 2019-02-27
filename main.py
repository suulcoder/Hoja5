"""

Hoja 5
Saul Contreras
Michele Benvenuto

Simulador de procesos en una computadora
"""
import random
import simpy
import math

datos = []
class computador(object):#Clase computador

    def __init__(self, env, procesadores, memoria):
        # Ejecutar:Cantidad de procesos a realizar por intento en el cpu
        # CPU:Resource
        # Procesos: cantidad de instrucciones a realizar
        # Tiempo de creacion
        self.env = env
        self.cpu = simpy.Resource(env, capacity=procesadores)
        self.ram = simpy.Container(env, memoria,init=0)
        self.procesadores = procesadores

    def add(self, ram, intervalo):
        yield env.timeout((1/(self.ram.capacity+(intervalo*100)))*100)
        if(self.ram.capacity-self.ram.level<ram):
            self.ram.put(ram)

class Proceso(object):#Clase proceso

    def __init__(self, env, procesos, ejecutar, memoria, computador, nombre, inicial):
        self.env = env
        self.action = env.process(self.run(env, ejecutar, memoria, computador, nombre, inicial))
        self.procesos = procesos


    def run(self, env, ejecutar, memoria, computador, nombre, inicial):
        yield env.timeout(1.0/computador.procesadores)
        with computador.cpu.request() as process:  # Utiliza el CPU
            contador = 3
            while True:
                try:
                    contador = contador - 1
                    self.procesos = self.procesos - 1
                    yield self.env.timeout(3/ejecutar)
                    yield process
                except simpy.Interrupt:
                    if (self.procesos < 0):  # Si ya no existe mas instrucciones
                        env.process(terminar(env, memoria, computador, nombre, inicial))  # Termina
                    else:
                        print('%s a procesado 3 instrucciones a %s. Instrucciones restantes:%s' % (nombre, env.now, self.procesos))
                        continuar = random.randint(1, 2)
                        if continuar == 0:  # Si regresa a ready
                            yield env.process(ready(env, self.procesos, ejecutar, memoria, computador, nombre, inicial))
                        elif continuar == 1:  # Si debe esperar
                            yield env.process(wait(env, self.procesos, ejecutar, memoria, computador, nombre, inicial))


def new(env, instrucciones, intervalo, cantidad, computador, inicio):
    for i in range(inicio, cantidad):
        tiempo = random.expovariate(1.0 / intervalo)#Generamos el intervalo
        memoria_RAM = random.randint(1, 10)#Generamos la memoria ram que consume el proceso
        instructions = random.randint(1, 10)#Generamos las instrucciones que consume el proceso
        inicial = env.now
        yield env.process(computador.add(memoria_RAM,intervalo))
        print(computador.ram.level)
        yield env.process(ready(env, instructions, instrucciones, memoria_RAM, computador, 'Proceso %d' % i, inicial))


def ready(env, procesos, ejecutar, memoria, computador, nombre, inicial):
    print('%s preparando proceso a %s' % (nombre, env.now))
    proceso = Proceso(env, procesos, ejecutar,memoria, computador, nombre, inicial)
    yield env.process(correr(env, ejecutar, proceso))

def correr(env, ejecutar, proceso):
    yield env.timeout(ejecutar)
    proceso.action.interrupt()

def wait(env, procesos, ejecutar, memoria, computador, nombre, inicial):
    yield env.timeout(1)  # Wait por una unidad de tiempo
    print('%s en espera a %s' % (nombre, env.now))
    env.process(ready(env, procesos, ejecutar, memoria, computador, nombre, inicial))  # Ejecutar ready de nuevo hasta que se terminen los procesos

def terminar(env,memoria,computador,nombre, inicial):
    print('%s terminado a %s' % (nombre, env.now))
    datos.append(env.now-inicial)  # Almacenamos la informacion para realizar pruebas estadisticas
    yield computador.ram.get(memoria)

#-----------------------------------------------------------------------
#Definimos los valores predeterminados
procesadores = 2#Numero de  procesadores en la computadora
memoria = 200#Cantidad de memoria RAM de la computadora
instrucciones = 3#Cantidad de instrucciones por proceso
intervalo = 10#Intervalo de aparicion de procesos
cantidad = 200#Cantidad de procesos generados


env = simpy.Environment()
random.seed(9)
computador = computador(env, procesadores, memoria)
process_gen = env.process(new(env, instrucciones, intervalo, cantidad, computador,0))
env.run(until=process_gen)
total = 0
for i in datos:#Calculamos el promedio
    total = total + i
promedio =(total / len(datos))
sumatoria = 0
for i in datos:#Calculamos la desviacion estandar
    sumatoria = sumatoria + ((i-promedio)**2)
desviacion = sumatoria/len(datos)
desviacion = math.sqrt(desviacion)
print("El tiempo promedio es " + str(promedio))
print("La desviacion estandar es " + str(desviacion))
