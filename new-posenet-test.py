import jetson.inference
import jetson.utils
import numpy as np
import argparse
import sys
import time

def parse_arguments():
    """Parse and return command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run pose estimation DNN on a video/image stream.", 
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=jetson.inference.poseNet.Usage() +
               jetson.utils.videoSource.Usage() +
               jetson.utils.videoOutput.Usage() +
               jetson.utils.logUsage()
    )

    parser.add_argument("input_URI", type=str, default="", nargs='?', 
                      help="URI of the input stream")
    parser.add_argument("output_URI", type=str, default="", nargs='?', 
                      help="URI of the output stream")
    parser.add_argument("--network", type=str, default="resnet18-body", 
                      help="pre-trained model to load (see below for options)")
    parser.add_argument("--overlay", type=str, default="links,keypoints", 
                      help="pose overlay flags (e.g. --overlay=links,keypoints)\n"
                           "valid combinations are:  'links', 'keypoints', 'boxes', 'none'")
    parser.add_argument("--threshold", type=float, default=0.15, 
                      help="minimum detection threshold to use")
    parser.add_argument("--fps", type=int, default=30, 
                      help="maximum frames per second to process")

    try:
        return parser.parse_known_args()[0]
    except:
        print("")
        parser.print_help()
        sys.exit(0)

def calculate_angle(pose, id1, id2, id3):
    """Calculate angle between three keypoints in degrees"""
    try:
        # Get keypoint coordinates
        point1 = (pose.Keypoints[id1].x, pose.Keypoints[id1].y)
        point2 = (pose.Keypoints[id2].x, pose.Keypoints[id2].y)
        point3 = (pose.Keypoints[id3].x, pose.Keypoints[id3].y)
        
        # Calculate vectors
        v1 = (point1[0] - point2[0], point1[1] - point2[1])
        v2 = (point3[0] - point2[0], point3[1] - point2[1])
        
        # Calculate angle using dot product
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if norm_v1 == 0 or norm_v2 == 0:
            return None
            
        cosine_angle = np.dot(v1, v2) / (norm_v1 * norm_v2)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # Prevent numerical issues
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)
    except Exception as e:
        print(f"Error calculating angle: {e}")
        return None

def process_arm_angle(pose, arm_side, font, img):
    """Process and visualize angle for either left or right arm"""
    # Get keypoint indices
    shoulder_idx = pose.FindKeypoint(f'{arm_side}_shoulder')
    elbow_idx = pose.FindKeypoint(f'{arm_side}_elbow')
    wrist_idx = pose.FindKeypoint(f'{arm_side}_wrist')
    
    # Check if all keypoints were found
    if shoulder_idx < 0 or elbow_idx < 0 or wrist_idx < 0:
        return None
        
    # Calculate angle
    angle = calculate_angle(pose, shoulder_idx, elbow_idx, wrist_idx)
    if angle is None:
        return None
        
    # Print to console
    print(f"{arm_side.capitalize()} arm angle: {angle:.2f}°")
    
    # Get elbow position for text placement
    elbow_x = pose.Keypoints[elbow_idx].x
    elbow_y = pose.Keypoints[elbow_idx].y
    
    # Position text with offset based on arm side
    x_offset = -50 if arm_side == 'left' else 10
    text_x = elbow_x + x_offset
    text_y = elbow_y - 30
    
    # Draw text on image
    text = f"{arm_side.capitalize()}: {angle:.1f}°"
    color = (0, 255, 0) if arm_side == 'left' else (255, 0, 0)  # Green for left, red for right
    
    font.OverlayText(
        img, img.width, img.height,
        text,
        int(text_x), int(text_y),
        color, (0, 0, 0, 128)  # Semi-transparent black background
    )
    
    return angle

def main():
    # Parse command line arguments
    opt = parse_arguments()
    
    # Load the pose estimation model
    net = jetson.inference.poseNet(opt.network, sys.argv, opt.threshold)
    
    # Create video sources & outputs
    input_stream = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
    output_stream = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv)
    
    # Initialize font once (more efficient than creating it every frame)
    font = jetson.utils.cudaFont()
    
    # Calculate frame interval for FPS control
    frame_interval = 1.0 / opt.fps
    
    # Process frames until the user exits
    while True:
        start_time = time.time()
        
        # Capture the next image
        img = input_stream.Capture()
        if img is None:  # Handle case where image capture fails
            time.sleep(frame_interval)
            continue

        # Perform pose estimation (with overlay)
        poses = net.Process(img, overlay=opt.overlay)

        # Print detection count
        print(f"Detected {len(poses)} objects in frame")

        # Process each detected pose
        for pose in poses:
            print("------------------------------------------------------------------------------")
            
            # Process both arms
            process_arm_angle(pose, 'left', font, img)
            process_arm_angle(pose, 'right', font, img)
            
            print("------------------------------------------------------------------------------")

        # Render the image
        output_stream.Render(img)

        # Update the title bar
        output_stream.SetStatus(f"{opt.network} | Network FPS: {net.GetNetworkFPS():.0f} | Processing FPS: {1/(time.time()-start_time):.1f}")

        # Print performance info periodically
        net.PrintProfilerTimes()

        # Control frame rate
        elapsed_time = time.time() - start_time
        if elapsed_time < frame_interval:
            time.sleep(frame_interval - elapsed_time)

        # Exit on input/output EOS
        if not input_stream.IsStreaming() or not output_stream.IsStreaming():
            break

if __name__ == "__main__":
    main()
    
