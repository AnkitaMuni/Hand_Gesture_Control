This project combines hand tracking using MediaPipe, a virtual keyboard interface in Pygame, and hardware control via an Arduino running StandardFirmata. The system allows users to play musical notes by interacting with a virtual keyboard using their fingertips. Additionally, an IR sensor detects objects and triggers a beep sound while controlling an LED on the Arduino.

Features
1. Virtual Keyboard:
   - A Pygame-based virtual keyboard that plays piano notes (Sa, Re, Ga, Ma, Pa, Da, Ni) when the user's fingertips interact with the keys.
   - Real-time visualization of hand landmarks and heatmap intensity.

2. Hand Tracking:
   - Uses MediaPipe Hands to track hand landmarks and detect fingertip interactions with the virtual keyboard.

3. IR Sensor Integration:
   - An IR sensor connected to the Arduino detects objects and triggers:
     - A beep sound in the Python application.
     - An LED on the Arduino board.

4. LED Control:
   - LEDs corresponding to each key on the virtual keyboard light up when the respective note is played.

5. Heatmap Visualization:
   - Displays a heatmap of hand activity over time, highlighting areas of interaction.

Requirements

Hardware
1. Arduino Board (e.g., Arduino Uno)
   - Running the StandardFirmata sketch.
2. IR Sensor (connected to digital pin 3).
3. LED (connected to digital pin 13).
4. 7 Additional LEDs (connected to pins 6–12 for virtual keyboard control).
5. Resistors for LEDs and IR sensor as needed.

Software
1. Python Libraries:
   - opencv-python
   - mediapipe
   - pygame
   - pyfirmata2
   - numpy
2. Arduino IDE:
   - To upload the *StandardFirmata* sketch to the Arduino.
3. Audio Files:
   - Piano notes (sa.wav, re.wav, etc.) and a beep sound (beep.wav).
