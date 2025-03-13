# Creaturebox Web Interface

A web-based interface for managing the Creaturebox/Mothbox software running on Raspberry Pi 5.

## Features

- Single-password authentication
- System monitoring and control
- Photo browsing and management
- Camera and hardware controls
- Schedule and settings configuration

## Installation

See the [installation guide](docs/installation.md) for detailed setup instructions.

## Development

This project uses Flask for the web framework and follows a modular architecture for easy extension.

### Project Structure

```
creaturebox_web/
├── app/                    # Main application code
│   ├── static/             # Static assets (CSS, JS)
│   ├── templates/          # HTML templates
│   ├── auth/               # Authentication module
│   └── utils/              # Utility functions
├── config/                 # Configuration files
├── scripts/                # Installation and utility scripts
└── docs/                   # Documentation
```

## License

This project is proprietary and confidential.
