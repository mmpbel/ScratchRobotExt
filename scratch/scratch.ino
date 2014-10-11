/*
  Scratch
  Executes Scratch commands and reports sensor states.
 */
 
// Pin 13 has an LED connected on most Arduino boards.
const byte LED = 13;
byte ledSt = 0;

// Pins 2..5 are used for motor control
const byte IN1 = 2;
const byte IN2 = 3;
const byte IN3 = 4;
const byte IN4 = 5;

// sensor
const byte WAIT_SENSOR = 0;
const byte TEMP_SENSOR = 1;
const byte SENSOR_SIZE = 5;
byte sensor[SENSOR_SIZE] = {0,1,2,3,4};

// commands
const byte LED_CMD = 'e';
const byte MOVE_FWD_CMD = 'f';
const byte MOVE_BACK_CMD = 'b';
const byte MOVE_LEFT_CMD = 'l';
const byte MOVE_RIGHT_CMD = 'r';

const byte MAX_CMD_SIZE = 5;

const byte EOL = '\r';

byte moveCounter = 0;

// the setup routine runs once when you press reset:
void setup() {                
  // initialize the digital pin as an output.
  pinMode(LED, OUTPUT);     

  pinMode(IN1, OUTPUT);     
  pinMode(IN2, OUTPUT);     
  pinMode(IN3, OUTPUT);     
  pinMode(IN4, OUTPUT);     

  Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
}

void motorStop ()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, HIGH);
}

void motorFwd ()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void motorBack ()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void motorLeft ()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void motorRight ()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

byte cmd[MAX_CMD_SIZE];
byte cmdPtr=0;

// the loop routine runs over and over again forever:
void loop ()
{
  delay(500);               // wait for ms

  // toggle led
  ledSt ^= 1;
  if (ledSt)
  {
    digitalWrite(LED, HIGH);
  }
  else
  {
    digitalWrite(LED, LOW);
  }

  Serial.write('s');
  for (byte i=0; i<SENSOR_SIZE; ++i)
  {
    Serial.write(' ');
    Serial.print(sensor[i]);
  }
  Serial.write('\n');

  if (moveCounter)
  {
    --moveCounter;
    if (0 == moveCounter)
    {
      motorStop();
      ++sensor[WAIT_SENSOR];
    }
  }

  if (cmdPtr >= MAX_CMD_SIZE)
  {
    byte param = 0;
    byte digit;

    for (cmdPtr=1; cmdPtr<(MAX_CMD_SIZE-1); ++cmdPtr)
    {
      digit = cmd[cmdPtr];
      cmd[cmdPtr] = EOL;  // erase old data
      if ((digit < '0') || (digit > '9'))
      {
        break;
      }
      param = param*10 + (digit - '0');
    }
    
    switch (cmd[0])
    {
      case MOVE_FWD_CMD:
        motorFwd();
        moveCounter = param;
        break;
      case MOVE_BACK_CMD:
        motorBack();
        moveCounter = param;
        break;
      case MOVE_LEFT_CMD:
        motorLeft();
        moveCounter = param;
        break;
      case MOVE_RIGHT_CMD:
        motorRight();
        moveCounter = param;
        break;
      case LED_CMD:
        break;
    }
    
    cmdPtr = 0;
  }
  else if (Serial.available() > 0)
  {
    byte ch = Serial.read();
    cmd[cmdPtr++] = ch;
    if (ch == EOL)
    {
      cmdPtr = MAX_CMD_SIZE;
    }
  }
}


