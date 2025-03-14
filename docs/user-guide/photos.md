# Photo Module

The Photo Module provides a way to browse, view, and manage photos captured by your Creaturebox/Mothbox device.

## Features

- Browse through photo directories
- View photos with zooming and navigation controls
- Display image metadata including EXIF information
- Download individual photos or batches of photos
- Efficient thumbnail generation with background processing

## Photo Browser

The photo browser allows you to navigate through your photo directories and view your image collections.

### Navigating Directories

1. Select a root directory from the sidebar to view its contents
2. Use the breadcrumb navigation at the top to move up in the directory structure
3. Click on any folder to navigate into it

### Viewing Options

- Toggle between Grid and List views using the view buttons
- Sort files by Name, Date, or Size using the Sort dropdown

### Selecting and Downloading Multiple Photos

1. Click the "Select" button to enter selection mode
2. Click on photos to select/deselect them
3. The number of selected items is displayed
4. Click "Download" to create a ZIP archive with the selected photos
5. Click "Cancel" to exit selection mode

## Photo Viewer

The photo viewer provides a detailed view of individual images with metadata display.

### Viewer Controls

- Click the back button to return to the browser
- Use zoom controls (+ and -) to adjust the image size
- Use keyboard shortcuts: arrow keys for navigation, +/- for zoom, Esc to return

### Navigation Between Photos

- Use the left and right arrow buttons to navigate between images in a directory
- Keyboard shortcuts: Left/Right arrow keys

### Viewing Metadata

The metadata panel displays:

- Basic file information (name, size, modified date)
- Image information (dimensions, format)
- EXIF data (if available) including camera settings

## Performance Features

The Photo Module includes several features to optimize performance, especially on the Raspberry Pi:

### Thumbnail Caching

- Thumbnails are generated once and cached for future use
- Multiple thumbnail sizes are supported for different views
- Background processing prevents UI freezing when generating thumbnails

### Batch Processing

- Large operations like ZIP creation happen in the background
- Tasks can resume after system interrupts like shutdowns
- Progress tracking and status updates are provided

## Technical Notes

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tif, .tiff)

### Storage Locations

- Thumbnails are stored in: `instance/thumbnails/`
- Temporary downloads are stored in the system temp directory
- The module looks for photos in:
  - `/home/pi/creaturebox/images`
  - `/home/pi/mothbox/images`
  - Application's `instance/photos` directory
