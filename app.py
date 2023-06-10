from flask import Flask, request
from web3 import Web3
from telegram import Bot
from telegram.utils.request import Request
from telegram import Update
from telegram.ext import Updater
from functools import partial
import threading
import time

# Connect to the BSC provider
provider_url = 'https://shy-cool-card.bsc.discover.quiknode.pro/dbb034c8952c4eaa68ed905b7217d666e37d05a0/'
web3 = Web3(Web3.HTTPProvider(provider_url))

# Contract address and ABI
contract_address = '0xD01A3196c5A64E745EE15Cb26A81c6Fd98f93A42'
contract_abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lpToken","type":"address"},{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"lockDate","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"unlockDate","type":"uint256"}],"name":"onDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lpToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"onWithdraw","type":"event"},{"inputs":[],"name":"gFees","outputs":[{"internalType":"uint256","name":"ethFeeLock","type":"uint256"},{"internalType":"uint256","name":"ethFeeRelock","type":"uint256"},{"internalType":"uint256","name":"ethFeeIncrementLock","type":"uint256"},{"internalType":"uint256","name":"ethFeeSplitLock","type":"uint256"},{"internalType":"contract IERCBurn","name":"secondaryFeeToken","type":"address"},{"internalType":"uint256","name":"secondaryTokenFee","type":"uint256"},{"internalType":"uint256","name":"secondaryTokenDiscount","type":"uint256"},{"internalType":"uint256","name":"liquidityFee","type":"uint256"},{"internalType":"uint256","name":"referralPercent","type":"uint256"},{"internalType":"contract IERCBurn","name":"referralToken","type":"address"},{"internalType":"uint256","name":"referralHold","type":"uint256"},{"internalType":"uint256","name":"referralDiscount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getLockedTokenAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getNumLockedTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"}],"name":"getNumLocksForToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getUserLockForTokenAtIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getUserLockedTokenAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getUserNumLockedTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"address","name":"_lpToken","type":"address"}],"name":"getUserNumLocksForToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getUserWhitelistStatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getWhitelistedUserAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getWhitelistedUsersLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"incrementLock","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_unlock_date","type":"uint256"},{"internalType":"address payable","name":"_referral","type":"address"},{"internalType":"bool","name":"_fee_in_eth","type":"bool"},{"internalType":"address payable","name":"_withdrawer","type":"address"}],"name":"lockLPToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"migrate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_unlock_date","type":"uint256"}],"name":"relock","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_feeAddress","type":"address"}],"name":"setFeeAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_referralPercent","type":"uint256"},{"internalType":"uint256","name":"_referralDiscount","type":"uint256"},{"internalType":"uint256","name":"_ethFeeLock","type":"uint256"},{"internalType":"uint256","name":"_ethFeeRelock","type":"uint256"},{"internalType":"uint256","name":"_ethFeeIncrementLock","type":"uint256"},{"internalType":"uint256","name":"_ethFeeSplitLock","type":"uint256"},{"internalType":"uint256","name":"_secondaryTokenFee","type":"uint256"},{"internalType":"uint256","name":"_secondaryTokenDiscount","type":"uint256"},{"internalType":"uint256","name":"_liquidityFee","type":"uint256"}],"name":"setFees","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IMigrator","name":"_migrator","type":"address"}],"name":"setMigrator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERCBurn","name":"_referralToken","type":"address"},{"internalType":"uint256","name":"_hold","type":"uint256"}],"name":"setReferralTokenAndHold","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_secondaryFeeToken","type":"address"}],"name":"setSecondaryFeeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"splitLock","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"tokenLocks","outputs":[{"internalType":"uint256","name":"lockDate","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"initialAmount","type":"uint256"},{"internalType":"uint256","name":"unlockDate","type":"uint256"},{"internalType":"uint256","name":"lockID","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"address payable","name":"_newOwner","type":"address"}],"name":"transferLockOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"bool","name":"_add","type":"bool"}],"name":"whitelistFeeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]

# Telegram bot token
telegram_token = '6159122774:AAHF1bNwU83ZswIK8W0sXhdhllGpRtNdcjc'


# Create a Telegram bot instance
bot = Bot(token=telegram_token)

# Set up event listeners
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


def process_event(event, bot_instance):
    # Construct the transaction URL
    tx_hash = event.transactionHash.hex()
    tx_url = f"https://bscscan.com/tx/{tx_hash}"
    
    # Format the message with the transaction URL
    message = f"New transaction detected!\nTransaction URL: {tx_url}"
    
    # Send the message to the desired chat or group
    chat_id = -1001888644934
    bot_instance.send_message(chat_id=chat_id, text=message)
    
    # Print the chat ID for verification
    print("Message sent to chat ID:", chat_id)
    
    # Print a message for debugging purposes
    print("Event processed successfully.")


def check_transactions():
    while True:
        # Get the latest block number
        latest_block = web3.eth.block_number
        
        # Retrieve the 10 most recent transactions
        block_range = max(0, latest_block - 9)
        transactions = []
        for block_number in range(latest_block, block_range, -1):
            block = web3.eth.get_block(block_number, full_transactions=True)
            transactions.extend(block["transactions"])
        
        # Process each transaction
        for transaction in transactions:
            process_transaction(transaction)
        
        # Sleep for 1 second before checking for new transactions again
        time.sleep(1)


def process_transaction(transaction):
    # Extract relevant information from the transaction
    tx_hash = transaction["hash"]
    tx_url = f"https://bscscan.com/tx/{tx_hash}"
    
    # Format the message with the transaction URL
    message = f"New transaction detected!\nTransaction URL: {tx_url}"
    
    # Send the message to the desired chat or group
    chat_id = -1001888644934
    bot.send_message(chat_id=chat_id, text=message)
    
    # Print the chat ID for verification
    print("Message sent to chat ID:", chat_id)
    
    # Print a message for debugging purposes
    print("Transaction processed successfully.")


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    event = update.message
    bot_instance = bot
    process_event(event, bot_instance)
    return 'OK'


if __name__ == '__main__':
    # Set up the Telegram bot webhook
    request = Request(con_pool_size=8)
    bot = Bot(token=telegram_token, request=request)
    updater = Updater(bot=bot)
    updater.bot.setWebhook(url='https://api.telegram.org/bot6159122774:AAHF1bNwU83ZswIK8W0sXhdhllGpRtNdcjc/setWebhook?url=https://icebotevents.netlify.app/webhook')
    
    # Start the event listener in a separate thread
    event_listener_thread = threading.Thread(target=start_event_listener)
    event_listener_thread.start()

    app.run()
