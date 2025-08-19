# Camera Screenshot Node

A MOFA node that captures images from the system camera and saves them to specified file paths. This node provides real-time camera access and image capture functionality using OpenCV, making it useful for computer vision workflows, surveillance applications, and image processing pipelines.

## Features

- **Camera Access**: Direct access to system camera (default camera index 0)
- **Image Capture**: Real-time image capture with OpenCV
- **File System Integration**: Saves captured images to specified file paths
- **Error Handling**: Comprehensive error handling for camera access and image capture
- **Native Dora Integration**: Uses native Dora Node API for efficient data flow
- **Configurable Parameters**: Supports command-line arguments for task and node naming

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

This node uses a native Dora Node architecture rather than the MofaAgent base class:

### Command Line Arguments
- `--name`: The name of the node in the dataflow (default: "arrow-assert")
- `--task`: Tasks required for the node (default: "Paris Olympics")

### Environment Variables
- `CI`: Set to "true" for CI/CD environments
- `TASK`: Override for the task parameter
- `IS_DATAFLOW_END`: Control dataflow termination

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_path` | string | Yes | File path where the captured image should be saved |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `camera_screenshot_result` | string | Result status and saved image filename |

## Usage Example

### Basic Dataflow Configuration

```yaml
# camera_screenshot_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      camera_screenshot_result: camera-screenshot/camera_screenshot_result
  - id: camera-screenshot
    build: pip install -e ../../agent-hub/camera-screenshot
    path: camera-screenshot
    outputs:
      - camera_screenshot_result
    inputs:
      image_path: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Ensure camera access:**
   ```bash
   # On Linux, you may need to add your user to the video group
   sudo usermod -a -G video $USER
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build camera_screenshot_dataflow.yml
   dora start camera_screenshot_dataflow.yml
   ```

4. **Send image path:**
   Input the desired save path for the captured image (e.g., "/path/to/save/image.jpg")

## Code Example

The core functionality is implemented in `main.py`:

```python
import cv2
import time
from dora import Node
from mofa.kernel.utils.util import create_agent_output
import pyarrow as pa

def main():
    node = Node(args.name)
    
    for event in node:
        if event["type"] == "INPUT":
            if event['id'] in ['image_path']:
                image_path = event["value"][0].as_py()
                
                try:
                    # Initialize the camera
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        print("Cannot open camera")
                        exit()
                    
                    # Allow the camera to warm up
                    time.sleep(1)
                    
                    # Capture the image
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to capture image")
                        cap.release()
                        exit()
                    
                    # Save the image
                    cv2.imwrite(image_path, frame)
                    print(f"Image saved as {image_path}")
                    
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    # Release the camera
                    cap.release()
                
                # Send output
                node.send_output("camera_screenshot_result", 
                    pa.array([create_agent_output(
                        agent_name='camera_screenshot_result',
                        agent_result='image.jpg',
                        dataflow_status=os.getenv("IS_DATAFLOW_END", True)
                    )]), event['metadata'])
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **opencv-python**: For camera access and image processing
- **mofa**: MOFA framework utilities (automatically available in MOFA environment)

## Camera Requirements

### Hardware Requirements
- System camera (webcam, built-in camera, or USB camera)
- Camera must be accessible at device index 0
- Sufficient lighting for image capture

### Software Requirements
- Camera drivers properly installed
- Camera permissions granted to the application
- No other applications blocking camera access

### Platform-Specific Notes

#### Linux
```bash
# Check available cameras
ls /dev/video*

# Grant camera permissions
sudo usermod -a -G video $USER
```

#### macOS
- Grant camera permissions in System Preferences → Security & Privacy → Camera

#### Windows
- Ensure camera drivers are installed
- Grant camera permissions in Windows Settings → Privacy → Camera

## Use Cases

### Computer Vision Workflows
- **Image Processing Pipelines**: Capture images for real-time analysis
- **Object Detection**: Provide input images for detection algorithms
- **Quality Control**: Capture images for automated inspection systems

### Surveillance and Monitoring
- **Security Systems**: Capture images triggered by events
- **Time-lapse Photography**: Regular image capture for time-lapse creation
- **Motion Detection**: Capture images when motion is detected

### Documentation and Archiving
- **Process Documentation**: Capture images of manufacturing processes
- **Inventory Management**: Take photos of items for cataloging
- **Scientific Research**: Document experiments and observations

## Troubleshooting

### Common Issues

1. **Camera Access Denied**
   - Check camera permissions
   - Ensure no other applications are using the camera
   - Verify camera drivers are installed

2. **Image Capture Failed**
   - Check camera connection
   - Verify sufficient lighting
   - Test camera with other applications

3. **File Save Errors**
   - Verify write permissions for the target directory
   - Check available disk space
   - Ensure valid file path format

### Debug Tips
- Enable logging with `WRITE_LOG: true`
- Test camera independently with OpenCV
- Check camera device index (try different values if 0 fails)
- Verify image path permissions

## Contributing

1. Test with various camera devices and platforms
2. Add support for multiple camera indices
3. Implement additional image formats and quality settings
4. Add metadata extraction and EXIF data support

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [OpenCV Python Documentation](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [Dora Framework](https://github.com/dora-rs/dora)