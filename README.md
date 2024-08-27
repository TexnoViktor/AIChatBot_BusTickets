# AIChatBot_BusTickets

![License](https://img.shields.io/github/license/TexnoViktor/AIChatBot_BusTickets) ![Language](https://img.shields.io/github/languages/top/TexnoViktor/AIChatBot_BusTickets)

## Overview

**AIChatBot_BusTickets** is a Python-based chat bot designed to assist users with bus ticket operations. This project was developed to showcase skills in Natural Language Processing (NLP) using SpaCy and integrating OpenAI's API for AI-driven conversations. The chat bot interacts with a database (reused from a previous project) to provide real-time assistance to users, such as searching for routes, booking tickets, and managing travel plans. **Please note that the chat bot is designed to understand and process inputs in the Ukrainian language only.**

## Features

- **Natural Language Processing:** Utilizes SpaCy for understanding and processing user input in Ukrainian.
- **AI-Powered Conversations:** Integrates OpenAI API for intelligent and context-aware responses.
- **Bus Ticket Management:** Allows users to search, book, and manage bus tickets through conversational interactions.
- **Database Integration:** Reuses the database from the previous bus ticket management project, ensuring consistency in data handling.

## Technologies Used

- **Programming Language:** Python
- **NLP Library:** SpaCy
- **AI Integration:** OpenAI API
- **Database:** SQLite 

## Installation

### Prerequisites

- Python 3.x
- SpaCy
- OpenAI API Key
- Pip

### Steps

1. **Clone the repository:**
    ```bash
    git clone https://github.com/TexnoViktor/AIChatBot_BusTickets.git
    ```

2. **Navigate to the project directory:**
    ```bash
    cd AIChatBot_BusTickets
    ```

3. **Set up a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up SpaCy:**
    - Download the necessary SpaCy language model.
    ```bash
    python -m spacy download uk_core_news_sm
    ```

6. **Configure the OpenAI API:**
    - Add your OpenAI API key to the environment or configuration file as needed.

7. **Run the chat bot:**
    ```bash
    python chatbot.py
    ```

8. **Interacting with the Bot:**
   - Follow the prompts to interact with the bot, using natural language to search for bus routes, book tickets, and manage your travel plans.
   - **Note:** The bot only understands and processes inputs in Ukrainian.

## Usage

- **Starting a Conversation:**
  - Launch the chat bot and start typing your queries in Ukrainian. The bot is trained to understand natural language inputs and provide relevant responses.

- **Example Commands:**
  - "Знайди автобус з Берліна до Мюнхена на 20 вересня."
  - "Покажи мені доступні місця на автобус о 10:00 до Гамбурга."
  - "Скасувати мій квиток на поїздку з Берліна до Мюнхена."

## Contributing

Contributions are welcome! If you have ideas for improving the bot’s functionality or expanding its capabilities, feel free to fork the repository and submit a pull request. Ensure that your contributions align with the project’s coding standards and are well-documented.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or further information, you can reach me at:

- **GitHub:** [TexnoViktor](https://github.com/TexnoViktor)
- **Email:** ushakovviktor14@gmail.com
