"""
Simple .env file loader that works on Windows without python-dotenv
"""
import os
from pathlib import Path


def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        print(f"Warning: .env file not found at {env_path}")
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Only set if not already in environment
                if key and not os.getenv(key):
                    os.environ[key] = value

    print("Environment variables loaded from .env")


if __name__ == "__main__":
    load_env()
    # Print loaded variables (without values for security)
    print("Loaded variables:", [k for k in ['SECRET', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN', 'GITHUB_USERNAME', 'PORT'] if os.getenv(k)])
