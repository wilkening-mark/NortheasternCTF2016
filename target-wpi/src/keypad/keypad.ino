#include <Keypad.h>
#include <Wire.h>
#include "sha256.h"
#include <EEPROM.h>

const byte ROWS = 4;
const byte COLS = 3;
char keys[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*', '0', '#'}
};

byte rowPins[ROWS] = {8, 3, 4, 6};
byte  colPins[COLS] = {7, 9, 5};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
const int I2C_ADDR = 0x42;

/* ring buffer for data to be transmitted */
const uint8_t MAX_ENTRY_LENGTH = 17 ;
const uint8_t I2C_MAX_MSG_SIZE = 32 ;

#define PACKET_SIZE 19
#define RECEIVE_BUFFER_SIZE 32
/* buffer for receivede data */
uint8_t receiveBuffer[RECEIVE_BUFFER_SIZE];

const uint8_t HASH_SIZE = 32 ;
const uint8_t SECRET_SIZE = 32 ;
const uint8_t CHALLENGE_SIZE = 32 ;
const uint8_t KEY_SIZE = 16 ;

uint8_t key_buf[MAX_ENTRY_LENGTH] = {0};
uint8_t secret[SECRET_SIZE] = {0};
unsigned int currentDHByte = 0;

uint8_t* HMAC_Digest;
uint8_t writeSecret = 0;

//Codes for status_to_arm
enum ARMStatus {
  NONE = 0xA0,
  REGISTER = 0xA1,
  UNLOCK = 0xA2,
  UNLOCK_WAITING = 0xA3,
  UNLOCK_READY = 0xA4,
  CP = 0xA5,
  CP_WAITING = 0xA6,
  CP_READY = 0xA7,
  BLOCKING = 0x1,
  SENDING_DATA = 0x2
};

#define GET_STATUSCMD 1
#define SECRETCMD 2
#define UNLOCKCMD 3
#define PIN_CHANGECMD 4
ARMStatus currStatus = NONE;

uint8_t toSend[64];
uint8_t sendLength = 0;

const int LED = 13;

uint8_t keyIndex = 0;

void setup(void) {
  Wire.begin(I2C_ADDR);
  Wire.onRequest(on_request);
  Wire.onReceive(on_receive);
  uint8_t i;
  for(i = 0; i < SECRET_SIZE; i++){
      secret[i] = EEPROM.read(i);
  }
  pinMode(LED, OUTPUT);
}

void clearBuffer() {
  for ( keyIndex = 0 ; keyIndex < MAX_ENTRY_LENGTH ; keyIndex++ ) { // Clear the buffer
    key_buf[keyIndex] = '\0' ;
  }
  keyIndex = 0;
}

void validRequest() { // Blink four-times quickly
  clearBuffer();
  uint8_t n ;
  for ( n = 0; n < 4; n++ ) {
    digitalWrite(LED, HIGH);
    delay(50) ;
    digitalWrite(LED, LOW);
    delay(50) ;
  }
}

void blinkN(int n, int s){
   int i = 0;
   for ( i = 0; i < n; i++){
    digitalWrite(LED, HIGH);
    delay(s) ;
    digitalWrite(LED, LOW);
    delay(s) ;
   }
}

void invalidRequest() {  // Blink trice slowly
  clearBuffer();
  uint8_t n ;
  for ( n = 0; n < 3; n++ ) {
    digitalWrite(LED, HIGH);
    delay(200) ;
    digitalWrite(LED, LOW);
    delay(200) ;
  }
}
void loop(void) {
  if(currStatus == UNLOCK_WAITING){
    unlock();
    return;
  }
  if(currStatus == CP_WAITING){
    changePin();
    return;
  }
  if(writeSecret){
    uint8_t i = 0;
    for(i = 0; i < SECRET_SIZE; i++){
      EEPROM.write(i, secret[i]);
    }
  }
  if (currStatus != NONE) {
    delay(40);
    return;
  }
  char key = keypad.getKey();
  if(key && keypad.getState() == PRESSED){
    key_buf[keyIndex++] = key;
    digitalWrite(LED, HIGH);
  }
  if(keypad.getState() == RELEASED){
    digitalWrite(LED, LOW);
  }
  if ( keyIndex == MAX_ENTRY_LENGTH ) {
    validRequest();
    return;
  }


  /***********************************************************************************************
     key_buffer index:  0   1   2   3   4   5   6   7   8   9   10    11    12    13    14    15   16
     Registration:      *   #   *   #   *   #   *   #
     Unlock:            p0  p1  p2  p3  p4  p5  #
     Tenant change PIN: o0  o1  o2  o3  o4  o5  *   n0  n1  n2  n3    n4    n5    #
     Master change PIN: m0  m1  m2  m3  m4  m5  m6  m7  m8  *   n0  n1    n2    n3    n4    n5    #
   **********************************************************************************************/

  if ( key == '#' ) {
    switch ( keyIndex ) {
      case 7:
        startUnlock();
        break ;
      case 14:
      case 16:
        startChangePin();
        break;
      default:
        registration();
        break;
    }
  }
}

void startUnlock() {
  uint8_t i;
  for(i = 0; i < 6; i++){
    if(!isDigit(key_buf[i])){
      invalidRequest();
      return;
    }
  }
  currStatus = UNLOCK;
}

void startChangePin() {
  uint8_t i = 0;
  if(keyIndex == 14){
    for( i = 0; i < 6; i++){
      if(!isDigit(key_buf[i])){
        invalidRequest();
        return;
      }
    }
    if(key_buf[i++] != '*'){
      invalidRequest();
      return;
    }
    for(; i < 13; i++){
      if(!isDigit(key_buf[i])){
        invalidRequest();
        return;
      }
    }
  }else{
    for( i = 0; i < 8; i++){
      if(!isDigit(key_buf[i])){
        blinkN(100, 50);
        invalidRequest();
        return;
      }
    }
    if(key_buf[i++] != '*'){
      blinkN(200, 50);
      invalidRequest();
      return;
    }
    for(; i < 15; i++){
      if(!isDigit(key_buf[i])){
        invalidRequest();
        return;
      }
    }
  }
  currStatus = CP;
}

void changePin(){
  uint8_t hmac[HASH_SIZE];
  uint8_t IV[16];
  uint8_t newPinHash[HASH_SIZE];
  uint8_t oldPinHash[HASH_SIZE];
  uint8_t data[64];
  int i = 0;
  int j = 0;
  //Begin Phase one Hashing
  Sha256.init();
  while(key_buf[i] != '*') {
    Sha256.write(key_buf[i++]);
  }
  memcpy(oldPinHash, Sha256.result(), HASH_SIZE);
  
  Sha256.initHmac((const uint8_t*) secret, SECRET_SIZE);
  for(j = 0; j < HASH_SIZE; j++){
    Sha256.write(oldPinHash[j]);
  }
  
  memcpy(hmac, Sha256.resultHmac(), 32);
  i++;
  Sha256.init();
  while(key_buf[i] != '#'){
    Sha256.write(key_buf[i++]);
  }
  memcpy(newPinHash, Sha256.result(), HASH_SIZE);

  for(i = 0; i < HASH_SIZE; i++){
    newPinHash[i] ^= hmac[i];
  }

  memcpy(data, newPinHash, 32);
  
  for(j = 0; j < HASH_SIZE; j++){
    receiveBuffer[j] ^= oldPinHash[j];
  }
  
  Sha256.init();
  for(j = 0; j < HASH_SIZE; j++){
    Sha256.write(receiveBuffer[j]);
  }
  memcpy(data+32, Sha256.result(), 32);
  
  memcpy(toSend, data, 64);

  sendLength = 64;
  blinkN(10,40);
  currStatus = CP_READY;
}

void unlock() {
  
  uint8_t pinHash[HASH_SIZE];
  int i = 0;
  //Begin Phase one Hashing
  Sha256.init();
  //Hash the key entered
  for (i = 0; i < 6; i++) {
    Sha256.write(key_buf[i]);
  }

  memcpy(pinHash, Sha256.result(), HASH_SIZE);
  Sha256.initHmac((const uint8_t*) secret, SECRET_SIZE);

  for (i = 0; i < CHALLENGE_SIZE; i++) {
    Sha256.write(receiveBuffer[i]);
  }

  for (i = 0; i < HASH_SIZE; i++) {
    Sha256.write(pinHash[i]);
  }

  memcpy(toSend, Sha256.resultHmac(), HASH_SIZE);
  sendLength = 32;
  blinkN(5, 50);
  currStatus = UNLOCK_READY;
}

void registration() {
  uint8_t incorrect = memcmp((void *) key_buf, "*#*#*#*#", keyIndex);
  if(incorrect){
    invalidRequest();
  }else{
    if(keyIndex == 8){
      currStatus = REGISTER;
      validRequest();
    }
  }
}

uint8_t count = 0;
int flop = 0;
void on_request() {
  if(currStatus == BLOCKING){
    return;
  }
  if(currStatus == SENDING_DATA){
     Wire.write(toSend[count]);
     count++;
    if(count == sendLength + 1){
     count = 0;
     currStatus = NONE;
     memset(key_buf, 0, MAX_ENTRY_LENGTH);
     keyIndex = 0;
     memset(receiveBuffer, 0, 32);
    }
  }else{
    Wire.write(currStatus);
    if(currStatus == UNLOCK_READY || currStatus == CP_READY){
      count = 0;
      currStatus = SENDING_DATA;
    }
  }
}

void on_receive(int bytes) {

  if(bytes > PACKET_SIZE || bytes < 3){
    while(Wire.available()) Wire.read();
    return; 
  }
  uint8_t i = 0 ;
  uint8_t msg;
  uint8_t msg_buf[PACKET_SIZE];
  while (i < bytes) {
    msg = Wire.read();
    msg_buf[i] = msg;
    i++;
  }
  uint8_t command = msg_buf[0];
  uint8_t done = msg_buf[1];
  uint8_t start = msg_buf[2];
  if(start + bytes - 3 > RECEIVE_BUFFER_SIZE){
   return; 
  }
  memcpy(receiveBuffer + start, msg_buf+3, bytes - 3);
  if(done){
    switch (command) {
      case SECRETCMD:
        currStatus = NONE;
        memcpy(secret, receiveBuffer, RECEIVE_BUFFER_SIZE);
        writeSecret = 1;
        break;
      case UNLOCKCMD:
        currStatus = UNLOCK_WAITING;
        break;
      case PIN_CHANGECMD:
        currStatus = CP_WAITING;
        break;
      default:
        currStatus = NONE;
        break;
    }
  }else{
    currStatus = BLOCKING;
  }
}

