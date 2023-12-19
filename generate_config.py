# generate_config.py

import os

# generate_config.py
class DefaultConfigGenerator:
    @staticmethod
    def generate_config():
        with open('config.py', 'w') as config_file:
            config_file.write(
                """
                # config.py
                class Config:
                API_KEY = 'your_api_key_here'
                # Add other configuration parameters as needed
                """
            )

if __name__ == '__main__':
    DefaultConfigGenerator.generate_config()

