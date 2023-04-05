# GMX GLP_weighting_hedger

This script retrieves and processes data related to GMX token weightings and sends an email to specified recipients with the results.

## Requirements

- Python 3
- `selenium` library
- ChromeDriver
- `web3` library
- `json` library
- `pandas` library
- Custom implementation  of `print_sql_driver` and `print_sql_driver` for email client and sql client

## How to Use

1. Install the required libraries.
2. Download and install ChromeDriver.
3. Update the variables in `main()` with your specific values.
4. Run the script.

## Description

The `GMXWeightings` class contains several functions for retrieving and processing data related to GMX token weightings, including:

- `get_chrome_driver()`: sets up the ChromeDriver instance for use in other functions.
- `get_token_dict_from_text()`: processes the text of a page on GMX and returns a dictionary of token weightings.
- `get_glp_price()`: retrieves the current GLP price from GMX.
- `init_web3_instance()`: initializes a web3 instance for retrieving the GLP balance.
- `get_web3_glp_balance()`: retrieves the GLP balance for the specified token holder address.
- `get_glp_token_dict()`: retrieves the token weightings from GMX.
- `send_email()`: sends an email to the specified recipients with the results.
- `add_to_sql()`: adds the retrieved data to an SQL database.

The `main()` function sets up the `GMXWeightings` instance, retrieves the necessary data, and sends an email with the results. The script also includes functionality for adding the retrieved data to an SQL database.

## License

This script is released under the MIT License. See LICENSE.txt for more information.
