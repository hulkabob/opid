import OPi.GPIO as GPIO
GPIO.setmode(GPIO.SUNXI)
GPIO.setup("PA13", GPIO.OUT)
GPIO.setup("PA14", GPIO.OUT) 
GPIO.setup("PD14", GPIO.OUT)  
GPIO.setup("PC4", GPIO.OUT)  
 
GPIO.output("PA13", True) 
GPIO.output("PA13", False) 
GPIO.output("PA14", True) 
GPIO.output("PA14", False) 
GPIO.output("PD14", True) 
GPIO.output("PD14", False) 
GPIO.output("PC4", True) 
GPIO.output("PC4", False) 


GPIO.output("PA14", False)
GPIO.output("PD14", False)
GPIO.output("PC4", False)

GPIO.output("PA14", True)
GPIO.output("PD14", True)
GPIO.output("PC4", True)