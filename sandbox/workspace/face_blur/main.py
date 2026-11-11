import cv2
import sys

def main():
    # Load Haar cascade for face detection (built-in OpenCV data)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print('Failed to load Haar cascade.')
        sys.exit(1)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Cannot open webcam')
        sys.exit(1)

    print('Press "q" to quit.')
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Failed to grab frame')
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Apply blur to each detected face region
        for (x, y, w, h) in faces:
            # Extract ROI and apply Gaussian blur
            face_roi = frame[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(face_roi, (99, 99), 30)
            frame[y:y+h, x:x+w] = blurred_roi

        cv2.imshow('Face Blur', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
