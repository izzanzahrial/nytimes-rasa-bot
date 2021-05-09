<br />
<p align="center">
  <a href="https://github.com/izzanzahrial/nytimes-rasa-bot">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">NY Times Book Bot</h3>

  <p align="center">
    A level 3 bot that can be used for searching NY Times Book best seller.
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

[![Product Name Screen Shot][product-screenshot]](https://example.com)

### Built With

* [Rasa-SDK](https://rasa.com/)
* [Python](https://www.python.org/)
* [Anaconda](https://www.anaconda.com/)



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1.  Get python 3.6 - 3.8
    ```sh
    https://www.python.org/downloads/
    ```
2.  Get rasa-sdk
    ```sh
    https://rasa.com/open-source/
    ```
3.  Get anaconda (for windows)
    ```sh
    https://www.anaconda.com/products/individual
    ```
### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/izzanzahrial/nytimes-rasa-bot.git
   ```
2. Install packages
   ```sh
   pip install -r requirements.txt 
   ```
3. Get your NY Times book API at https://developer.nytimes.com/get-started
4. Enter your API at .env
   ```sh
   KEY = "YOUR API"
   ```
5. Connect your bot to your messenger
   ```sh
   https://rasa.com/docs/rasa/connectors/your-own-website
   ```
6. Run ngrok and enter your ngrok https at credentials.yml
   ```sh
   ngrok http 5005
   webhook_url: "YOUR_NGROK_HTTPS/webhooks/telegram/webhook"
   ```
7. restart ngrok
8. run rasa and rasa actions
   ```sh
   rasa run actions
   rasa run
   ```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.