#!/usr/bin/env python3

import socket
import threading
import logging 	
import sys
import pickle
import random
import time
import speech_recognition as sr
import pyaudio
import wave

logging.basicConfig(level=logging.DEBUG,
                     format='(%(threadName)-10s) %(message)s',)

Lpersonajes=["Mike","Parker","Ariel","Batman","Wolverine","Dora","Tigger","Shaggy"]
Lpistas=[["Solo tiene un ojo","Es verde","Tiene 2 pies","Amigo de Solivan","Es un montruo"],
		["Un gran poder conlleva una gran responsabilidad","Traje rojo con azul","Sobrino de May","Novio de Mary Jane","Enemigo de octopus"],
		["Sirena","Cabello rojo","Novia del pricipe erick","Hija de Poseidon","Pierde su voz"],
		["Enemigo del pinguino","Usa capa","Amigo de Robin","El mejor detective","su traje es negro"],
		["Tiene garras","Huesos de adamantium","Es Xmen","Es un mutante","Tiene una hija que no es su hija"],
		["su amigo es botas","su enemigo es un zorro","Tiene un mapa","su primo es diego","es exploradora"],
		["Rebota sobre su propia cola","Es de color anaranjado","Es rayado","Amigo de Winnie Pooh","Es un tigre"],
		["Es un hippie","Usa camisa verde","Habla con su perro","Suele perderse","Resuelve misterios"]]


Npistas=2
personajeA=random.randint(0,6)
mapa=Lpistas[personajeA][0:Npistas]
Ltiros=[]

r = sr.Recognizer()
response = {
        "success": True,
        "error": None,
        "transcription": None
}

def validacion(personaje):
	if(personaje==personajeA):
		print("personaje incorrecto!!!")
		return 1
	else:
		print("Ganaste encontraste al personaje")
		return 0

data_string = pickle.dumps(mapa)
start_time = 0

class Servidor():
	"""docstring for Servidor"""
	def __init__(self, host="localhost", port=9000):
	#def __init__(self, host="10.100.73.232", port=4000):
		global mapa,Lpersonajes,personajeA,Ltiros,start_time

		self.clientes = []
		self.data_string = pickle.dumps(mapa)
		self.ganar=0
		self.cont=0
		self.Ndato=0
		self.ban=0
		self.tablero=0
		self.estatus=0
		self.Njugadores=0
		self.inicio=0

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((str(host), int(port)))
		self.sock.listen(10)
		self.sock.setblocking(False)

		event = threading.Event()
		aceptar = threading.Thread(target=self.aceptarCon, args=(event,))
		procesar = threading.Thread(target=self.procesarCon, args=(event,))
		
		aceptar.daemon = True
		aceptar.start()

		procesar.daemon = True
		procesar.start()

		while True:
			msg = input('->')
			if(self.estatus==1):
				self.ganar=0
				self.cont=0
				self.Ndato=0
				self.ban=0
				self.estatus=0
				self.Njugadores=0
				self.inicio=0
				event.clear()
				personajeA=random.randint(0,6)
				Npistas=2
				mapa=Lpistas[personajeA][0:Npistas]
				data_string = pickle.dumps(mapa)
				del Ltiros[:]
				del self.clientes[:]
			if msg == 'salir':
				self.sock.close()
				sys.exit()
			else:
				pass

	def msg_to_all(self, msg):
		for c in self.clientes:
			try:
				c.sendall(msg)
			except:
				self.clientes.remove(c)

	def msg_to_except(self, msg, cliente):
		for c in self.clientes:
			try:
				if(c!=cliente):
					c.sendall(msg)
			except:
				self.clientes.remove(c)

	###############################################aqui esta la funcion que decide a quien le manda 1 es su turno, 0 no lo es.
	def msg_to_shot(self,ide):
		for c in self.clientes:
			try:
				if(ide==int(c.fileno())):
					time.sleep(0.01)
					bytesToSend=str.encode("1")
					c.sendall(bytesToSend)
				else:	
					time.sleep(0.01)
					bytesToSend=str.encode("0")
					c.sendall(bytesToSend)
			except:
				self.clientes.remove(c)
	###################################################################################
	def msg_to_c(self,msg,msg1,cliente):
		for c in self.clientes:
			try:
				if(c==cliente):
					c.sendall(msg)
					if(repr(msg)=="b'Felicidades Adivinaste al personaje!!!'"):
						time.sleep(0.01)
						final_time = time.time() - start_time
						bytesToSend = str.encode(str(final_time))
						c.sendall(bytesToSend)
					if(repr(msg)=="b'No adivinaste el personaje!!!'"):
						time.sleep(0.01)
						final_time = time.time() - start_time
						bytesToSend = str.encode(str(final_time))
						c.sendall(bytesToSend)
				else:
					if(repr(msg)=="b'No adivinaste el personaje!!!'"):
						jugada="Esta fue la jugada de tu contrincante: "+str(repr(msg1)[2:])
						c.sendall(str.encode(jugada))
					if(repr(msg)=="b'Felicidades Adivinaste al personaje!!!'"):
						c.sendall(b"Has perdido otro jugador adivino el personaje!!!")
						time.sleep(0.01)
						final_time = time.time() - start_time
						bytesToSend = str.encode(str(final_time))
						c.sendall(bytesToSend)
			except:
				self.clientes.remove(c)


	def aceptarCon(self,cond):
		print("aceptarCon iniciado")
		ban=0
		while True:
			try:
				conn, addr = self.sock.accept()
				conn.setblocking(False)
				self.clientes.append(conn)
				if(self.ban==0):	
					self.clientes[len(self.clientes)-1].sendall(b"Escoge cuantos jugadores")
					self.ban=1
					print("Esperando a recibir numero de jugadores...")
				else:
					self.clientes[len(self.clientes)-1].sendall(b"P2")
				self.inicio=1
			except:
				pass

			event_is_set=cond.wait(0)
			if(event_is_set and ban==0):
				time.sleep(0.01)
				data_string = pickle.dumps(mapa)
				self.msg_to_all(data_string)
				ban=1

				time.sleep(0.01)
				bytesToSend=str.encode("1")
				self.msg_to_c(bytesToSend,"",self.clientes[0])
				bytesToSend=str.encode("0")
				self.msg_to_except(bytesToSend,self.clientes[0])

			if(len(self.clientes)==0):
				ban=0

	def procesarCon(self,cond):
		global mapa,Lpersonajes,personajeA,Ltiros,start_time,Npistas

		print("ProcesarCon iniciado")
		contador=0
		turnocliente=0
		while True:
			data_string = pickle.dumps(mapa)
			if len(self.clientes) > 0:
				for c in self.clientes:
					try:
						if(self.Ndato!=2):
							data = c.recv(1024)

						if(self.Ndato==0):
							#contador=int(c.fileno())+1
							self.Njugadores=int(data)
							print("Se escogio ",self.Njugadores," Jugadores")
							self.Ndato=2
							print("Personaje:")
							print(personajeA)

						elif(self.Ndato==2):
							if(self.Njugadores==len(self.clientes)):
								self.Ndato=3
								cond.set()
								start_time = time.time()
								if(len(self.clientes)>1):
									turnocliente=1
									contador=int(self.clientes[turnocliente].fileno())
								else:
									contador=int(self.clientes[0].fileno())
						else:
							print(data)
							if(repr(data)=="b'1'"):
								print("audio recibido")
							try:
								r = sr.Recognizer()
								grabacion = sr.AudioFile('grab.flac')

								with grabacion  as source:
									recognizer.adjust_for_ambient_noise(source)
									audio = r.record(source, duration=4)

									response["transcription"]=r.recognize_google(audio)
									time.sleep(0.01)
									coordenada=response['transcription']
									print("dijiste: ",coordenada)
							except:
								print("audio no reconocido")

							"""if((coordenada in Lpersonajes)==False):
								print("Personaje no en lista")
								while True:
									time.sleep(0.01)
									bytesToSend=str.encode("PN")
									c.sendall(bytesToSend)
									print("enviado")
									data = c.recv(1024)

									if(repr(data)=="b'1'"):
										print("audio recibido")
									grabacion = sr.AudioFile('grab.flac')

									with grabacion  as source:
										recognizer.adjust_for_ambient_noise(source)
										audio = r.record(source, duration=4)

									response["transcription"]=r.recognize_google(audio)
									coordenada=response['transcription']
									print("dijiste: ",coordenada)

									if(coordenada in Lpersonajes):
										bytesToSend=str.encode("PS")
										c.sendall(bytesToSend)
										time.sleep(0.01)
										data = c.recv(1024)
										break
									else:
										print("Personaje no en lista")
							else:
								print("personaje en lista")
								time.sleep(0.01)
								bytesToSend=str.encode("PS")
								c.sendall(bytesToSend)
								data = c.recv(1024)"""
							#coordenada=str(data)[2:len(str(data))-1]
							#mapa.pop(mapa.index(coordenada))
							data_string = pickle.dumps(mapa)
							self.msg_to_all(data_string)

							time.sleep(0.01)

							#if(contador-4>len(self.clientes)-1):
							if(turnocliente>len(self.clientes)-1):
								contador=int(self.clientes[0].fileno())   ################# aqui si el contador es igual al tamaño maximo de clientes lo regresa al id de el cliente1
								turnocliente=0
							#######################################aqui manda a llamar la funcion que decide quien tira
							self.msg_to_shot(contador)
							turnocliente+=1
							if(len(self.clientes)>turnocliente):
								contador=int(self.clientes[turnocliente].fileno()) 
							#contador+=1  #### aumenta el contador que indica que es turno de el sigueinte cliente

							time.sleep(0.01)
							if((coordenada in Ltiros)==False):
								Ltiros.append(coordenada)
								if(coordenada!=Lpersonajes[personajeA]):
									print("NO adivinaste")
									bytesToSend = str.encode("No adivinaste el personaje!!!")
									if(Npistas<5):
										Npistas+=1
										mapa=Lpistas[personajeA][0:Npistas]
								if(coordenada==Lpersonajes[personajeA]):
									self.estatus=1
									bytesToSend = str.encode("Felicidades Adivinaste al personaje!!!")
									#self.msg_to_c(bytesToSend,c)
									print("Acabo el juego. Conencte otros Jugadores...")
									print("Presione Enter")
							else:
								bytesToSend = str.encode("Tiro repetido o no existe ese personaje")
								if(Npistas<5):
										Npistas+=1
										mapa=Lpistas[personajeA][0:Npistas]
							bytesToSend1 = str.encode(coordenada)
							self.msg_to_c(bytesToSend,bytesToSend1,c)
			
						if(self.inicio==1 and self.Ndato==2):
							time.sleep(0.1)
							bytesToSend=str.encode("Esperando a que se conecten "+str(self.Njugadores-len(self.clientes))+" jugadores"+" y estan conectados: "+str(len(self.clientes)))
							self.msg_to_all(bytesToSend)
							self.inicio=0
							print(bytesToSend)

						if(self.estatus!=1 and self.Ndato==3):
							print("Esperando a recibir un personaje... ")
					except:
						pass
s = Servidor()