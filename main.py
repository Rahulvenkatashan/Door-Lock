import RPi.GPIO as GPIO
import time


#Set up the pin output
channel = 2

#Set up motor
GPIO.setmode(GPIO.BCM) 
GPIO.setup(14,GPIO.OUT)
pwm=GPIO.PWM(14,50)
pwm.start(0)

#setup leds
blue_led = 10
green_led = 9
red_led = 11

GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(blue_led, GPIO.OUT)
GPIO.setup(red_led, GPIO.OUT)

#Set up button press
GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.setup(channel, GPIO.IN)
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime = 250)

#Knock visualiation
def knock_visulizer(pinOn,pinOff,knock_led,is_for_knock_vis, for_button_ops):
    if is_for_knock_vis:
		GPIO.output(knock_led, True)
		time.sleep(0.05)
		GPIO.output(knock_led, False)

    elif type(pinOn) == int and type(pinOff) == int:
		GPIO.output(pinOn, True)
		GPIO.output(pinOff, False)
    
    elif for_button_ops:
		GPIO.output(knock_led, True)
		time.sleep(0.4)
		GPIO.output(knock_led, False)



#Button options
def button_pressed():
    counts = []
    while GPIO.input(5) == False:
		counts.append(True)
		knock_visulizer(False, False, blue_led, False, True)
		time.sleep(0.4)
    return len(counts)

#Open door function
def unlock():
	print("The motor unlocked the door")
	pwm.start(0)
	pwm.ChangeDutyCycle(6.5) 
	time.sleep(1)
	pwm.ChangeDutyCycle(0)

#Close door function
def Lock():
	print("The door was locked")
	pwm.start(0)
	pwm.ChangeDutyCycle(12) 
	time.sleep(1)
	pwm.ChangeDutyCycle(0)

#Main function to generate the time bewtween knocks and shut it off when time is more than 5 seconds
def record_knock_times():
    #First let's set up the variables
    timeout_length = 3 #3 second time out length(program shuts off if no knock is detected within 3 seconds 
    time_when_knocked = [] #Time between knocks
    current_time = time.time() #Current time
    end_time = time.time() + timeout_length #End time How long before while loop ends
    real_time_between_knocks = [] #This is where I store diffrences between knocks
    while current_time < end_time:
        current_time = time.time() #Update time
        if GPIO.event_detected(channel) == True: #See if signial is changed from 1 to 0(This means that a knock is registerd)
	    print("kncok detected")
	    knock_visulizer(False,False,blue_led,True, False)
            end_time = time.time() + timeout_length  #Reseting the endtime
            #Record the time at which the knocks were registerd
            time_when_knocked.append(time.time())
            time.sleep(0.01)
    for i in range(len(time_when_knocked)):
        if (i+1)%len(time_when_knocked) != 0:
            real_time_between_knocks.append(round(time_when_knocked[(i+1)%len(time_when_knocked)]-time_when_knocked[i],2)) #did % here to stay within range of array, and we subtract t2 - t1. We do this because the time 2 will always be greater than time 1 
             
    return real_time_between_knocks

def same_knock_detector(pattern,attempt):
    check = [] #All this is for is to add a True value if a thing is right
    acceptance = 0.7 #This is how off the ratio can be
    ratio = pattern[0]/attempt[0] #This is the ratio between the two patterns first elements]
    #Music; Tempo How fast or slow something is
    #You can slow down a song but the ratio will be the same otherwise it is diffrent
    #Sure your ratio can be off by a couple of tenth seconds or even hundreth seconds etc..
    #This is why I am using a acceptance rate so that I can make sure that it is reasonable
    #So basicly if I divide the first element of Offical knock pattern(Of pattern I stored) by first element of pattern I attemped I can get ratio, using the logic above we can move on
    for i in range(len(pattern)): #Looping through pattern to check for inconcentinsies in tempo
        if pattern[i]/attempt[i] >= ratio * acceptance and pattern[i]/attempt[i] <= ratio + (ratio - (ratio * acceptance)): #This checks if the ratio  is within the tolreance limit, the part before the "and" is for minuimum, and the part after the "and" is for the maximum value this part is diffrent to calculating thr minuimum part inorder to keep a balanced threshold 
            check.append(True)#If the if statment is passed then True is appended to the check variable meaning that the current element in attempt is true as it fits the limit and tempo
        else: #Is basicly if the "if" was not satisfied then the element or the specific knock was not a true set with ratio 
            return "There was an inconcestincy at " + str(i) #This is just for me for testing purposes, this allowes me to get the index where the error was, then I can make manual calculations and see if the error should have occured    
    if len(check) == len(pattern):#This is checking the length of the check value, so basiclly if every element satisfies the requirements then a True was added to the check vaiable, so if the len of the check variable is the same to the length of the pattern wee know it is the same pattern 
        return True 
    else:
        return False
            

knock_code = []#This is what will store you knock
door_is_unlocked = False
while True:
	if door_is_unlocked == False:
	    knock_visulizer(red_led,green_led,blue_led,False,False)
	
	if GPIO.input(5) == False:
	    print("activated")
	    button_held = button_pressed()
	    if button_held == 1 and not door_is_unlocked:
			print("door open")
			door_is_unlocked = True
	    elif button_held > 1 and not door_is_unlocked:
			print("Password reset protocol activated")
			knock_code = []
	    
	
	if not door_is_unlocked: #ensures that did program is not detecting knocks while door is unlocked
		result = record_knock_times()

	if len(knock_code) == 0: #Determines if person has not set knock code
		print("Please set up your knock")
		GPIO.output(red_led, True)
		GPIO.output(green_led, True)
		while len(knock_code) == 0: #Makes sure program does not run until knock is greater than 1
			knock_code = record_knock_times()
		print("knock was saved")
		GPIO.output(green_led, False)
		time.sleep(0.5)
		GPIO.output(green_led, True)
		time.sleep(1)
		if door_is_unlocked:
		    knock_visulizer(green_led, red_led, blue_led, False)
		else:
		    knock_visulizer(red_led, green_led, blue_led, False, False)
	elif len(knock_code) !=0 and len(result) == len(knock_code) and not door_is_unlocked: #If door is locked and valid knock exists and if len are same
		if same_knock_detector(knock_code,result) == True:
			knock_visulizer(green_led,red_led,blue_led,False,False)
			unlock()
			door_is_unlocked = True
			vib_unlock = True 
			while door_is_unlocked and vib_unlock:
				print("door is unlocked")
				knock_count = 0
				while knock_count != 2:
					if GPIO.event_detected(channel)==True: #Closes door when vibration detected
						knock_count += 1
				
				Lock()
				knock_visulizer(red_led,green_led,blue_led,False,False)
				door_is_unlocked = False

		else:
			print("wrong password try again")
			GPIO.output(red_led, False)
			time.sleep(0.5)
			GPIO.output(red_led, True)
			time.sleep(1)
	elif door_is_unlocked:
	    knock_visulizer(green_led,red_led,blue_led,False,False)
	    unlock()
	    while door_is_unlocked:
		print("door is unlocked")
		time.sleep(10)
		Lock()
		knock_visulizer(red_led,green_led,blue_led,False,False)
		door_is_unlocked = False
	
	elif len(result) != len(knock_code) and len(result) !=0: #another edge case
		print("Length was not same so door did not unlock")
		GPIO.output(red_led, False)
		time.sleep(0.5)
		GPIO.output(red_led, True)
		time.sleep(1)
	
