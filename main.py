"""

Hoja 5
Saul Contreras
Michele Benvenuto

Simulador de procesos en una computadora
"""
import random
import simpy

datos = []

class computador(object):

    def __init__(self, env, procesadores, memoria):
        # Ejecutar:Cantidad de procesos a realizar por intento en el cpu
        # CPU:Resource
        # Procesos: cantidad de instrucciones a realizar
        # Tiempo de creacion
        self.env = env
        self.cpu = simpy.Resource(env, capacity=procesadores)
        self.ram = simpy.Container(env, init=memoria, capacity=memoria)


class Proceso(object):

    def __init__(self, env, procesos, ejecutar, memoria, computador, nombre):
        self.env = env
        self.action = env.process(self.run(env, ejecutar, memoria, computador, nombre))
        self.procesos = procesos

    def run(self, env, ejecutar, memoria, computador, nombre):
        with computador.cpu.request() as process:  # Utiliza el CPU
            contador = 3
            while True:
                try:
                    contador = contador - 1
                    self.procesos = self.procesos - 1
                    yield self.env.timeout(1)
                    if (self.procesos == 0):  # Si ya no existe mas instrucciones
                        env.process(terminar(env, memoria, computador, nombre))  # Termina
                except simpy.Interrupt:
                    if (self.procesos < 0):  # Si ya no existe mas instrucciones
                        env.process(terminar(env, memoria, computador, nombre))  # Termina
                    else:
                        print('%s a procesado 3 instrcciones a %s. Instrucciones restantes:%s' % (nombre, env.now, self.procesos))
                        continuar = random.randint(1, 2)
                        if continuar == 0:  # Si regresa a ready
                            yield env.process(ready(env, self.procesos, ejecutar, memoria, computador, nombre))
                        elif continuar == 1:  # Si debe esperar
                            yield env.process(wait(env, self.procesos, ejecutar, memoria, computador, nombre))


def new(env, instrucciones, intervalo, cantidad, computador):
    for i in range(cantidad):
        tiempo = random.expovariate(1.0 / intervalo)#Generamos el intervalo
        memoria_RAM = random.randint(1, 10)#Generamos la memoria ram que consume el proceso
        instructions = random.randint(1, 10)#Generamos las instrucciones que consume el proceso
        if (computador.ram.capacity != 0):
            env.timeout(tiempo)
            computador.ram.get(memoria_RAM)
            yield env.process(ready(env, instructions, instrucciones, memoria_RAM, computador, 'Proceso %d' % i))


def ready(env, procesos, ejecutar, memoria, computador, nombre):
    print('%s preparando proceso a %s' % (nombre, env.now))
    proceso = Proceso(env, procesos, ejecutar,memoria, computador, nombre)
    yield env.process(correr(env, ejecutar, proceso))

def correr(env, ejecutar, proceso):
    yield env.timeout(ejecutar)
    proceso.action.interrupt()

def wait(env, procesos, ejecutar, memoria, computador, nombre):
    yield env.timeout(1)  # Wait por una unidad de tiempo
    print('%s en espera a %s' % (nombre, env.now))
    env.process(ready(env, procesos, ejecutar, memoria, computador, nombre))  # Ejecutar ready de nuevo hasta que se terminen los procesos

def terminar(env,memoria,computador,nombre):
    print('%s terminado a %s' % (nombre, env.now))
    datos.append(env.now)  # Almacenamos la informacion para realizar pruebas estadisticas
    yield computador.ram.put(memoria)


#-----------------------------------------------------------------------
#Definimos los valores predeterminados
procesadores = 1#Numero de  procesadores en la computadora
memoria = 100#Cantidad de memoria RAM de la computadora
instrucciones = 3#Cantidad de instrucciones por proceso
intervalo = 10#Intervalo de aparacion de procesos
cantidad = 50#Cantidad de procesos generados

env = simpy.Environment()
random.seed(10)
computador = computador(env, procesadores, memoria)
process_gen = env.process(new(env, instrucciones, intervalo, cantidad, computador))
env.run(until=None)
total = 0
print(datos)
for i in datos:
    total = total + i
print("El tiempo promedio es " + str(total / len(datos)))
