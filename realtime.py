import cv2
import numpy as np

# Define the variables
config_path = "yolov3.cfg"
weights_path = "yolov3.weights"
classes_path = "yolov3.txt"

def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Open camera
cap = cv2.VideoCapture(0)  # 0 represents the first camera connected, change it if you have multiple cameras

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Load YOLO model
net = cv2.dnn.readNet(weights_path, config_path)

# Read the class names
classes = None
with open(classes_path, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Generate random colors for each class
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    print("Frame dimensions:", frame.shape)

    Width = frame.shape[1]
    Height = frame.shape[0]
    scale = 0.00392

    # Create blob
    blob = cv2.dnn.blobFromImage(frame, scale, (416,416), (0,0,0), True, crop=False)

    # Set input to the network
    net.setInput(blob)

    # Forward pass
    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    # Parse the outputs
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # Apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Draw the bounding boxes and labels
    for i in indices:
        try:
            box = boxes[i]
        except:
            i = i[0]
            box = boxes[i]

        x, y, w, h = box
        draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

    # Display the frame
    cv2.imshow("object detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera
cap.release()
cv2.destroyAllWindows()