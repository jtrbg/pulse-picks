# Winter Project: PulsePicks

The picks 

## Getting Started

These instructions will help you set up and run the project on your local machine.

### Prerequisites

- **Python (version 3.10.x)**
- **Flask (version 3.0.0)**
- **FLASK-SQLAlchemy (version 3.1.1)**: local database management
- **The-Odds-API (version 4)**: _populates the odds for upcoming games_
    - maximum **500** requests/month
- **nfl-data-py (version 0.3.1)**: _populates the scores, player stats, and team stats_

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/jtrbg/pulse-picks.git
    ```

2. Navigate to the project directory:

    ```bash
    cd your-repo
    ```

3. Set up a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    ```bash
    # On Windows
    .\venv\Scripts\activate

    # On macOS/Linux
    source venv/bin/activate
    ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Create a `config.py` file in the project root:
    ```bash
    python generate_config.py
    ```

    The generated config file should look something along the lines of:

    ```python
    # config.py

    class Config:
        API_KEY = 'your_api_key_here'
        # Add other configuration parameters as needed
    ```

    Replace `'your_api_key_here'` with your actual API key that you got from [https://the-odds-api.com/](https://the-odds-api.com/).

### Usage

1. Run the application:

    ```bash
    python main.py
    ```

2. Open your browser and go to [http://localhost:5000/](http://localhost:5000/).

3. Explore the site and enjoy!

## Additional Information

[Include any additional information, troubleshooting tips, or FAQs.]

## License

This project is licensed under the [Your License] - see the [LICENSE.md](LICENSE.md) file for details.