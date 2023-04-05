import sys
import time as timey
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append("..")
from print_sql_driver import execute_sql_get_command
from email_driver import gmail_send_message
from print_sql_driver import add_to_sql_df
from web3 import Web3
import json


class GMXWeightings:
    def __init__(self, chrome_executable_path, recipients, glp_token_holder_address, glp_abi_file):
        self.chrome_executable_path = chrome_executable_path
        self.recipients = recipients
        self.browser = self.get_chrome_driver()
        self.glp_gmx_url = 'https://app.gmx.io/#/dashboard'
        self.glp_price_xpath = '//*[@id="root"]/div[1]/div/div/div[2]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]'
        self.xpath = '//*[@id="root"]/div[1]/div/div/div[2]/div[3]/div[3]'
        self.token_dict = None
        self.glp_balance = None

        # Arbitrum public RPC URL
        self.arbitrum_rpc_url = 'https://arb1.arbitrum.io/rpc'
        self.fsGLP_contract_address = '0x1addd80e6039594ee970e5872d247bf0414c8903'
        self.glp_abi_file = glp_abi_file
        self.token_holder_address = glp_token_holder_address
        self.contract_abi_string = None
        self.contract_abi = None
        self.contract = None
        self.checksum_token_holder_address = None
        self.function_names = None
        self.latest_block = None


    def __del__(self):
        self.browser.quit()

    def get_chrome_driver(self, headless=True):
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        return webdriver.Chrome(executable_path=self.chrome_executable_path, options=chrome_options)

    def get_token_dict_from_text(self, text):
        lines = text.split("\n")
        token_dict = {}
        current_token = None
        flag = False
        utilization = False
        price = False

        for line in lines:
            words = line.split(" ")
            if words[0] in ['ETH', 'BTC', 'LINK', 'UNI', 'USDC', 'USDT', 'DAI', 'FRAX']:
                current_token = words[0]
                token_dict[current_token] = {}
            elif words[0] == "Weight":
                flag = True
            elif words[0] == "Utilization":
                utilization = True
            elif words[0] == "Price":
                price = True
            elif flag:
                token_dict[current_token]['Weight'] = words[0].strip("%").strip("/")
                flag = False
            elif utilization:
                token_dict[current_token]['Utilization'] = words[0].strip("%")
                utilization = False
            elif price:
                token_dict[current_token]['Price'] = words[0].strip("$")
                price = False

        return token_dict

    def get_glp_price(self):
        self.browser.get(self.glp_gmx_url)
        # wait 6 seconds
        timey.sleep(6)
        wait = WebDriverWait(self.browser, 10)
        
        try:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, self.glp_price_xpath)))
            text = str(element.text)
            text = text.replace("$", "")
            print(text)
            #number_regex = "[0-9.,]+"
            #number = re.search(number_regex, text)
            glp_price = float(text)
            return glp_price
        except TimeoutException:
            print("The element was not found within the given timeout.")
            return None


    def init_web3_instance(self):
        self.w3 = Web3(Web3.HTTPProvider(self.arbitrum_rpc_url))

        if self.w3.is_connected():
            print("Connected to Arbitrum network")
        else:
            print("Not connected")
            
    def get_web3_glp_balance(self):
        with open(self.glp_abi_file) as f:
            contract_abi = json.load(f)
        
        # Create a contract object
        self.contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(self.glp_contract_address),
                                             abi=contract_abi)
        checksum_token_holder_address = self.w3.toChecksumAddress(self.glp_token_holder_address)

        function_names = [function['name'] for function in contract_abi if function['type'] == 'function']
        print(function_names)

        latest_block = self.w3.eth.block_number
        contract_abi = json.loads(contract_abi)

        function_names = [function['name'] for function in contract_abi if function['type'] == 'function']
        print(function_names)

        latest_block = self.w3.eth.block_number
        print(f"Latest block number: {latest_block}")

        # Get the balance
        #[{"internalType":"address","name":"_account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
        balance = self.contract.functions.balanceOf(checksum_token_holder_address).call()
        balance = balance / 10**18
        print(f"fsGLP balance of {self.token_holder_address}: {balance}")
        
        return balance

    
    def get_glp_token_dict(self):
        self.browser.get(self.glp_gmx_url)
        # wait 6 seconds
        timey.sleep(6)
        wait = WebDriverWait(self.browser, 10)
        
        try:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, self.xpath)))
            text = str(element.text)
            print(text)
            token_dict = self.get_token_dict_from_text(text)
            return token_dict
        except TimeoutException:
            print("The element was not found within the given timeout.")
            return None
    
    def send_email(self, subject, body):
        gmail_send_message(self.gmail_user, self.gmail_password, self.gmail_to, subject, body)

    def add_to_sql(self, sql_table):
        # create sql table if it doesn't exist

        # add data to sql table
        print(f"Adding data to {sql_table} table in SQL database")
        add_to_sql_table(sql_table, self.token_dict)


def main():
    # set up GMXWeightings instance
    chrome_executable_path = 'path/to/chromedriver.exe'
    recipients = ['recipient1@example.com', 'recipient2@example.com']
    glp_token_holder_address = '0x1234567890abcdef1234567890abcdef12345678'
    glp_abi_file = 'path/to/glp_abi.json'
    gmxClass = GMXWeightings(chrome_executable_path, recipients, glp_token_holder_address, glp_abi_file)
    
    # retrieve GLP price
    glp_price = gmxClass.get_glp_price()
    print(f"GLP Price: ${glp_price}")
    
    # initialize web3 instance and retrieve GLP balance
    gmxClass.init_web3_instance()
    glp_balance = gmxClass.get_web3_glp_balance()
    print(f"GLP Balance: {glp_balance} fsGLP")
    
    # retrieve GLP token dict
    token_dict = gmxClass.get_glp_token_dict()
    print(token_dict)
    
    # send email with results
    subject = "GMX Weightings Update"
    body = f"GLP Price: ${glp_price}\nGLP Balance: {glp_balance} fsGLP\n\nToken Weightings:\n{token_dict}"
    gmxClass.send_email(subject, body)
    
    # add data to SQL database
    gmxClass.add_to_sql("gmx_weightings")

    
if __name__ == "__main__":
    main()