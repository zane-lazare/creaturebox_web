# Photo Module - Developer Guide

This document provides technical details about the Photo Module implementation for developers.

## Architecture

The Photo Module is structured into several components:

- **Browser/Viewer UI**: Frontend interfaces for browsing and viewing photos
- **API Endpoints**: Backend routes for data retrieval and actions
- **Thumbnail Manager**: Handles thumbnail generation and caching
- **Task System**: Background processing with interrupt resistance
- **Download Handler**: Manages batch download creation

### File Structure

```
app/
├── photos/
│   ├── __init__.py         # Blueprint definition
│   ├── routes.py           # API routes and views
│   ├── utils.py            # Utility functions
│   ├── tasks.py            # Background task system
│   ├── thumbnail_manager.py # Thumbnail handling
│   └── download.py         # Download functionality
├── templates/
│   └── photos/
│       ├── index.html      # Module landing page
│       ├── browser.html    # Directory browser
│       └── viewer.html     # Photo viewer
└── static/
    └── img/
        └── thumbnail-placeholder.svg # Loading image
```

## Background Processing System

The task system provides a way to perform long-running operations without blocking the web interface, with specific design considerations for the Raspberry Pi environment.

### Key Features

- Thread-based background processing
- Task state persistence across application restarts
- Safe shutdown and restart handling
- Progress tracking and status reporting

### Task Lifecycle

1. Tasks are enqueued via `tasks.enqueue_task()`
2. A worker thread processes tasks sequentially
3. Task state is saved to disk in real-time
4. Tasks can be monitored via status API endpoints
5. Interrupted tasks are marked for recovery

### Implementation Details

- Tasks are stored in `instance/state/photo_tasks.json`
- Each task has a unique ID and type identifier
- Task states: pending, processing, completed, failed, interrupted
- Worker thread is a daemon to prevent blocking application shutdown

## Thumbnail Generation

The thumbnail system is designed to efficiently generate and cache thumbnails while minimizing resource usage.

### Thumbnail Sizes

- Small: 100x100 pixels
- Medium: 240x240 pixels
- Large: 480x480 pixels
- XLarge: 800x800 pixels

### Caching Strategy

- Thumbnails are stored in `instance/thumbnails/[size]/[hash].jpg`
- The hash is derived from the source path to ensure uniqueness
- Thumbnails are only regenerated when the source is newer
- Background generation prevents UI blocking
- Placeholder images are shown during generation

### Implementation Details

- Uses Pillow (PIL) for image processing
- Preserves image EXIF orientation during thumbnail creation
- Converts transparency to white background for consistent display
- Implements fallback paths for error conditions

## Batch Download System

The download system allows for creating ZIP archives of multiple photos for batch download.

### Features

- Background ZIP creation to prevent UI blocking
- Progress tracking and status updates
- Automatic cleanup of old downloads

### Implementation Details

- Downloads are stored in the system temporary directory
- Uses the Python standard library `zipfile` module
- Implements path security checks to prevent traversal
- Provides both single-file and multi-file download options

## Metadata Extraction

The metadata system extracts and displays information about images.

### Types of Metadata

- Basic file information (size, modified date)
- Image properties (dimensions, format, color mode)
- EXIF data from digital cameras

### Implementation Details

- Uses exifread for EXIF extraction
- Falls back gracefully when libraries are not available
- Handles binary data safely

## Security Considerations

- All paths are validated against allowed root directories
- Path traversal attacks are prevented via `get_safe_path()`
- User-supplied filenames are sanitized with `secure_filename()`
- Subprocess execution is not used for image operations

## Error Handling

- Comprehensive error logging
- Graceful fallbacks for missing dependencies
- Client-friendly error messages
- Automatic recovery from interrupted operations

## Extending the Module

### Adding New Image Formats

To add support for additional image formats:

1. Add the extension to `IMAGE_EXTENSIONS` in `utils.py`
2. Ensure Pillow supports the format for thumbnail generation
3. Add any specific handling if needed

### Adding New Operations

To add new batch operations:

1. Create a new endpoint in `routes.py`
2. Implement the operation function in an appropriate module
3. Use the task system for long-running operations
4. Update the UI to provide access to the new feature

### Configuration

The module can be configured by modifying:

- `PHOTO_ROOT_DIRS`: List of directories to search for photos
- `THUMBNAIL_SIZES`: Dimensions for various thumbnail sizes
- `THUMBNAIL_QUALITY`: JPEG quality setting for thumbnails
