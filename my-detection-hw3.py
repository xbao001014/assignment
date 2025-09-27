import jetson_inference
import jetson_utils

net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

img = jetson_utils.loadImage("images1.jpeg")

detections = net.Detect(img)

jetson_utils.saveImage("detection_result.jpg", img)

for det in detections:
	print(f"class:{net.GetClassDesc(det.ClassID)}, confidence:{det.Confidence:.2f}, grid:({det.Left}, {det.Right}, {det.Top}, {det.Bottom})")


