import pigpio
import time

SERVO_FIRST_PIN = 6
SERVO_FIRST_MIN = 900 # 900
SERVO_FIRST_MAX = 1400 # 1800

SERVO_SECOND_PIN = 20
SERVO_SECOND_MIN = 800 #800
SERVO_SECOND_MAX = 1800 #2200

DECODER_ONE_PIN_A = 4
DECODER_ONE_PIN_B = 17

DECODER_TWO_PIN_A = 22
DECODER_TWO_PIN_B = 27

def get_sign( number ):

	if number > 0:
		return 1

	if number < 0:
		return -1

	return 0  

class Pigpio():

	def __init__(self):
		# self.pi_socket = pigpio.pi("192.168.2.102" , 8888)
		self.pi_socket = pigpio.pi()

		if not self.pi_socket.connected:
		   print " not connect"
		else:
		   print " succesed connect"
		self.servo_first_position = SERVO_FIRST_MIN
		self.servo_second_position = SERVO_SECOND_MAX

		self.pi_socket.set_servo_pulsewidth(SERVO_FIRST_PIN,self.servo_first_position)
		self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, self.servo_second_position)

		self.decoder_one_position = 0
		self.decoder_two_position = 0

		self.decoder_one = decoder(self.pi_socket, DECODER_ONE_PIN_A, DECODER_ONE_PIN_B, self.decoder_one_callback)
		self.decoder_two = decoder(self.pi_socket, DECODER_TWO_PIN_A, DECODER_TWO_PIN_B, self.decoder_two_callback)

	def close(self):
		self.pi_socket.stop()

	def set_servo(self,first_target_n , second_target_n):

		first_target = self.mapping(first_target_n,0,1,SERVO_FIRST_MIN,SERVO_FIRST_MAX)
		second_target = self.mapping(second_target_n,0,1,SERVO_SECOND_MIN,SERVO_SECOND_MAX)

		print("first_target : {0} , second_target : {1}".format(first_target,second_target))

		first_arrival = False
		second_arrival = False

		first_step = first_target - self.servo_first_position
		second_step = second_target - self.servo_second_position

		first_direction = get_sign(first_step)
		second_direction = get_sign(second_step)

		if first_step == 0:
			first_arrival = True

		if second_step == 0:
			second_arrival = True

		while first_arrival is False or second_arrival is False:

			if first_arrival is False:
				self.servo_first_position += first_direction * 5
				
				if abs(first_target - self.servo_first_position) < 5:
					self.servo_first_position = first_target
					self.pi_socket.set_servo_pulsewidth(SERVO_FIRST_PIN, self.servo_first_position)
					first_arrival = True
				else:
					self.pi_socket.set_servo_pulsewidth(SERVO_FIRST_PIN, self.servo_first_position)


			if second_arrival is False:
				self.servo_second_position += second_direction  * 5
				self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, self.servo_second_position)

				if abs(second_target - self.servo_second_position) < 5:
					self.servo_second_position = second_target
					self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, self.servo_second_position)
					second_arrival = True
				else:
					self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, self.servo_second_position)

			self.check_servo_position()

			# print(self.servo_second_position)

		time.sleep(1)



	def check_servo_position(self):

		if self.servo_first_position < SERVO_FIRST_MIN:
			self.pi_socket.set_servo_pulsewidth(SERVO_FIRST_PIN, SERVO_FIRST_MIN)

		if self.servo_first_position > SERVO_FIRST_MAX:
			self.pi_socket.set_servo_pulsewidth(SERVO_FIRST_PIN, SERVO_FIRST_MAX)

		if self.servo_second_position < SERVO_SECOND_MIN:
			self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, SERVO_SECOND_MIN)

		if self.servo_second_position > SERVO_SECOND_MAX:
			self.pi_socket.set_servo_pulsewidth(SERVO_SECOND_PIN, SERVO_SECOND_MAX)

	def get_servo(self):

		sp_1 = self.mapping(self.servo_first_position , SERVO_FIRST_MIN ,SERVO_FIRST_MAX , 0,1)
		sp_2 = self.mapping(self.servo_second_position , SERVO_SECOND_MIN ,SERVO_SECOND_MAX , 0,1)

		return sp_1 , sp_2

	def decoder_one_callback(self,way):
		self.decoder_one_position += way
		# print("decoder_one_callback : {0}".format(self.decoder_one_position))

	def decoder_two_callback(self,way):
		self.decoder_two_position += way
		# print("decoder_two_callback : {0}".format(self.decoder_two_position))

	def decoder_reset(self):
		self.decoder_one_position = 0
		self.decoder_two_position = 0

	def get_decoder(self):

		return self.decoder_one_position , self.decoder_two_position

	def mapping(self, x, in_min, in_max, out_min, out_max):
		return (x - in_min) * (out_max - out_min) / (float)(in_max - in_min) + out_min;



class decoder:

   """Class to decode mechanical rotary encoder pulses."""

   def __init__(self, pi, gpioA, gpioB, callback):

      """
      Instantiate the class with the pi and gpios connected to
      rotary encoder contacts A and B.  The common contact
      should be connected to ground.  The callback is
      called when the rotary encoder is turned.  It takes
      one parameter which is +1 for clockwise and -1 for
      counterclockwise.
	  
	  """

      self.pi = pi
      self.gpioA = gpioA
      self.gpioB = gpioB
      self.callback = callback

      self.levA = 0
      self.levB = 0

      self.lastGpio = None

      self.pi.set_mode(gpioA, pigpio.INPUT)
      self.pi.set_mode(gpioB, pigpio.INPUT)

      self.pi.set_pull_up_down(gpioA, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpioB, pigpio.PUD_UP)

      self.cbA = self.pi.callback(gpioA, pigpio.EITHER_EDGE, self._pulse)
      self.cbB = self.pi.callback(gpioB, pigpio.EITHER_EDGE, self._pulse)

   def _pulse(self, gpio, level, tick):

      """
      Decode the rotary encoder pulse.

                   +---------+         +---------+      0
                   |         |         |         |
         A         |         |         |         |
                   |         |         |         |
         +---------+         +---------+         +----- 1

             +---------+         +---------+            0
             |         |         |         |
         B   |         |         |         |
             |         |         |         |
         ----+         +---------+         +---------+  1
      """

      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level;

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if   gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback(-1)

   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.cbA.cancel()
      self.cbB.cancel()



