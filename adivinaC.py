import socket
import threading
import sys
import pickle
import time
import speech_recognition as sr
import subprocess
import pyaudio
import wave


cicle=0
estatus=0
tirar=1
esperando=0
recognizer = 0
mic = 0
response = 0
Lpersonajes=[]

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
duracion=5
archivo="grabacion.wav"

def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.
    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source) # #  analyze the audio source for 1 second
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #   update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable/unresponsive"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


class Cliente():
	"""docstring for Cliente"""
	def __init__(self, host="localhost", port=9000):
	#def __init__(self,host,port):
		global cicle,cont,ganar,estatus,tirar,esperando,recognizer,mic,response,Lpersonajes

		msg=""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((str(host), int(port)))
		data = self.sock.recv(1024)
		if(repr(data)!="b'P2'"):
			#print(repr(data)[0:19]+"\n"+repr(data)[20:28]+"\n"+repr(data)[29:39])
			print(repr(data))
			msg = input()
			self.send_msg(str(msg))
		else:
			print("espera a que se establezca numero de jugadores...")

			
		msg_recv = threading.Thread(target=self.msg_recv)

		msg_recv.daemon = True
		msg_recv.start()

		while True:
			if(estatus==0):
				time.sleep(0.001)
				msg = input()

			if(msg == 'salir' or estatus==1):
				self.sock.close()
				sys.exit()
			if msg != 'salir' and tirar==1:
				"""while True:
					recognizer = sr.Recognizer()
					mic = sr.Microphone()
					print("\nDi el nombre de un personaje ejemplo('Arya')...")
					print("Speak:")
					response = recognize_speech_from_mic(recognizer, mic)
					msg=response['transcription']
					print("Say: ",msg)
					if(msg != None):
						print(Lpersonajes)
						if(msg in Lpersonajes):
							break
						else:
							print("personaje no existe")
					else:
						print("palabra no reconocida")
				msg=input("Ingrese un personaje: ")
				#print(msg)
				self.send_msg(msg)"""
				print("\nDi el nombre de un personaje ejemplo('Arya')...")
				audio=pyaudio.PyAudio()
				stream=audio.open(format=FORMAT,channels=CHANNELS,
                   					rate=RATE, input=True,
                    				frames_per_buffer=CHUNK)

				print("grabando...")
				frames=[]

				for i in range(0, int(RATE/CHUNK*duracion)):
					data=stream.read(CHUNK)
					frames.append(data)
				print("grabación terminada")

					#DETENEMOS GRABACIÓN
				stream.stop_stream()
				stream.close()
				audio.terminate()

					#CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
				waveFile = wave.open(archivo, 'wb')
				waveFile.setnchannels(CHANNELS)
				waveFile.setsampwidth(audio.get_sample_size(FORMAT))
				waveFile.setframerate(RATE)
				waveFile.writeframes(b''.join(frames))
				waveFile.close()

				subprocess.call(['avconv', '-i', '/home/aryi/Documentos/Materias/AplicacionesRed/Problema1/actualizacion1/grabacion.wav', '-y', '-ar', '48000', '-ac', '1', 'grab.flac'])
				self.send_msg("1")
				time.sleep(0.01)
				#print("esperando respuesta...")	
			if msg != 'salir' and tirar==0:
				print("No es tu turno...")


	def msg_recv(self):
		global cont,estatus,tirar,Lpersonajes
		while True:
			try:
				data = self.sock.recv(4096)
				#print(data)

				if(repr(data)[0:11]=="b'Esperando"):
					print(data)
				elif(repr(data)=="b'PN'"):
					print("\nPersonaje no en lista")
					print("\nDi el nombre de un personaje ejemplo('Arya')...")
					audio=pyaudio.PyAudio()
					stream=audio.open(format=FORMAT,channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

					print("grabando...")
					frames=[]

					for i in range(0, int(RATE/CHUNK*duracion)):
					    data=stream.read(CHUNK)
					    frames.append(data)
					print("grabación terminada")

					#DETENEMOS GRABACIÓN
					stream1.stop_stream()
					stream1.close()
					audio.terminate()

					#CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
					waveFile = wave.open(archivo, 'wb')
					waveFile.setnchannels(CHANNELS)
					waveFile.setsampwidth(audio.get_sample_size(FORMAT))
					waveFile.setframerate(RATE)
					waveFile.writeframes(b''.join(frames))
					waveFile.close()

					subprocess.call(['avconv', '-i', '/home/aryi/Documentos/Materias/AplicacionesRed/Problema1/actualizacion1/grabacion.wav', '-y', '-ar', '48000', '-ac', '1', 'grab.flac'])
					self.send_msg("1")
					time.sleep(0.01)
					print("esperando respuesta...")
				elif(repr(data)=="b'No adivinaste el personaje!!!'"):
					 print(data)
					 #print("\nNo es tu turno...")
				elif(repr(data)=="b'Tiro repetido'" ):
					print(data)
				elif(repr(data)=="b'Felicidades Adivinaste al personaje!!!'" ):
					print(data)
					estatus=1
					data = self.sock.recv(1024)
					print("Tiempo: ",repr(data)[2:7],"segundos")
					print("Presione Enter")
				elif(repr(data)=="b'Has perdido otro jugador adivino el personaje!!!'"):
					print(data)
					estatus=1
					time.sleep(0.01)
					data = self.sock.recv(4024)
					print("Tiempo: ",repr(data)[2:7],"segundos")
					print(data)
					print("Presione Enter")
				elif(repr(data)[2:39]=="Esta fue la jugada de tu contrincante"):
					print(data)
					if(tirar==0):
						print("\nNo es tu turno...")
					else:
						print("\nEnvia un nombre de un personaje ejemplo('Arya')...")
				else:
					data_arr = pickle.loads(data)
					print()
					print(data_arr)
					Lpersonajes=data_arr
					time.sleep(0.01)

					data = self.sock.recv(1024)
					print(data)

				if(estatus!=1):
					if(repr(data)!="b'Escoge cuantos jugadores: '" and repr(data)[0:11]!="b'Esperando"):
						if(repr(data)=="b'1'"):
							tirar=1   ################si recibe 1 es su turno
							print("\nEs su turno. Teclee Enter, para decir su personaje...")
						if(repr(data)=="b'0'"):
							tirar=0   ########### si recibe 0 no lo es
							print("\nNo es tu turno...")
			except:
				pass

	def send_msg(self, msg):
		self.sock.sendall(str.encode(msg))

#HOST=input("Escribe la direccion IP: >")
#PORT=int(input("Escribe el Puerto: >"))
c = Cliente()
			